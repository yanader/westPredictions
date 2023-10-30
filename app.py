from flask import Flask, render_template, session, request, redirect
from flask_session import Session
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, percent_format, create_league_stats

## Initiate Flask instance
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

## Use precent_format from helpers.py
app.jinja_env.filters["percent_format"] = percent_format

## Initialise sqlite database
db = SQL("sqlite:///nwc.db")


## Main route that displays the login form to the user or, if already logged in, directs to the "/predict" route
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        if "user_id" in session:
            return redirect("/predict")
        else:
            return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    ## Clear any user_id
    session.clear()

    ## User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        ## Ensure username was submitted
        if not request.form.get("username"):
            return redirect("/register")

        ## Ensure password was submitted
        elif not request.form.get("password"):
            return redirect("/register")

        ## Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        ## Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return redirect("/register")

        ## Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        ## Redirect user to home page
        return redirect("/predict")

    ## User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


## Route provided to clear session
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        ## Validation that the user has entered values in all three fields
        if (
            not request.form.get("username")
            or not request.form.get("password")
            or not request.form.get("confirmation")
        ):
            return redirect("/register")
        ## Validation that the user has confirmed their password accurately
        if request.form.get("password") != request.form.get("confirmation"):
            return redirect("/register")
        ## Enter new user details into the database and redirect to login
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            request.form.get("username"),
            generate_password_hash(request.form.get("password")),
        )
        return redirect("/login")
    else:
        return render_template("register.html")


## Render profile page that allows for password change and creation/joining of private leagues
@app.route("/profile", methods=["GET"])
@login_required
def profile():
    user = db.execute("SELECT username FROM users WHERE id = ?;", session["user_id"])[
        0
    ]["username"]
    return render_template("profile.html", user=user)


@app.route("/changepassword", methods=["POST"])
@login_required
def changepassword():
    if request.method == "POST":
        ## Validate that the user has entered values into all fields
        if (
            not request.form.get("oldpassword")
            or not request.form.get("newpassword")
            or not request.form.get("confirmednewpassword")
        ):
            return
        ## Validate that the users new password and confirmation match
        if request.form.get("newpassword") != request.form.get("confirmednewpassword"):
            return
        ## Retrieve hash of old password and check the old password matches
        hash = db.execute("SELECT hash FROM users WHERE id = ?;", session["user_id"])[
            0
        ]["hash"]
        if check_password_hash(request.form.get("oldpassword"), hash):
            return
        new_hash = generate_password_hash(request.form.get("newpassword"))
        ## If so, update the database with the hash of the new password
        db.execute(
            "UPDATE users SET hash = ? WHERE id = ?;", new_hash, session["user_id"]
        )
        return redirect("/predict")


@app.route("/predict", methods=["GET", "POST"])
@login_required
def predict():
    if request.method == "POST":
        ## When accessed through POST, a user's predictions are entered into the predictions table and then redirected to GET
        db.execute(
            "INSERT INTO predictions (user_id, match_id, prediction) VALUES (?,?,?)",
            session["user_id"],
            int(request.form.get("match_id")),
            request.form.get("result"),
        )
        return redirect("/predict")
    elif request.method == "GET":
        user = db.execute(
            "SELECT username FROM users WHERE id = ?;", session["user_id"]
        )[0]["username"]

        ## Extract matches that have no current predictions as a list of dictionaries
        matches = db.execute(
            "SELECT id, date, opponent, location_id, competition FROM matches WHERE id NOT IN (SELECT DISTINCT match_id FROM predictions WHERE user_id = ?) AND visible = 1",
            session["user_id"],
        )

        ## Extract predictions that already exist
        predictions = db.execute(
            "SELECT p.id as prediction_id, p.match_id, p.prediction, r.result_type, m.id as match_id, m.date, m.opponent, case when m.location_id = 1 then 'H' else 'A' end as location, m.competition FROM predictions p JOIN result_types r on r.id = p.prediction JOIN matches m on m.id = p.match_id where p.user_id = ? AND m.visible = 1",
            session["user_id"],
        )

        ## Formatting to turn codes in database into human readable content
        for match in matches:
            if match["location_id"] == 1:
                match["location"] = "H"
            elif match["location_id"] == 2:
                match["location"] = "A"

        ## Render template passing in variables
        return render_template(
            "predict.html", user=user, matches=matches, predictions=predictions
        )


## Route used when a user changed an existing prediction
@app.route("/repredict", methods=["POST"])
def repredict():
    ## Uses an UPDATE statement to change an existing database line instead of adding a new line.
    db.execute(
        "UPDATE predictions SET prediction = ? WHERE id = ?",
        int(request.form.get("result")),
        request.form.get("prediction_id"),
    )
    return redirect("/predict")


## Creates the main league including all users
@app.route("/leagues", methods=["GET"])
@login_required
def leagues():
    ## Query database to include predictions, results and number of matches played
    league = db.execute(
        "select u.username, count(p.id) as predictions, sum(case when p.correct = 1 then 1 else 0 end) as correct from users u left join predictions p on p.user_id = u.id and p.correct is not null group by u.username"
    )
    matches = db.execute(
        "select count(id) as played from matches where result_id is not null"
    )[0]["played"]

    ## Use helper function to add % stats to league
    league = create_league_stats(league, matches)

    return render_template("leagues.html", league=league, matches=matches)


## Allows access to viewing private leagues that contain a subset of users
@app.route("/privateleagues", methods=["GET", "POST"])
@login_required
def privateleagues():
    ## Retrieve a list of leagues based on the current session user
    leagues = db.execute(
        "SELECT DISTINCT l.id as leagueid, name FROM leagues l JOIN league_memberships WHERE memberid = ?;",
        session["user_id"],
    )
    if request.method == "GET":
        return render_template("privateleagues.html", leagues=leagues)
    elif request.method == "POST":
        ## Retrive (from POST/db) id of league to display, name and member list
        leagueid = request.form.get("selectedleague")
        leaguename = db.execute("SELECT name FROM leagues WHERE id = ?;", leagueid)[0][
            "name"
        ]
        members = db.execute(
            "SELECT username from league_memberships JOIN users on users.id = league_memberships.memberid WHERE leagueid = ?;",
            leagueid,
        )
        ## Convert memberlist from dictionary retrieved from db to a list of usernames
        memberlist = []
        for member in members:
            memberlist.append(member["username"])
        ## Query database to include predictions, results and number of matches played
        league = db.execute(
            "select u.username, count(p.id) as predictions, sum(case when p.correct = 1 then 1 else 0 end) as correct from users u left join predictions p on p.user_id = u.id and p.correct is not null group by u.username"
        )
        matches = db.execute(
            "select count(id) as played from matches where result_id is not null"
        )[0]["played"]

        ## Use helper function to add % stats to league and sort
        league = create_league_stats(league, matches)

        ## Create a league that only includes the members of the private league
        filtered_league = []
        for member in league:
            if member["username"] in memberlist:
                filtered_league.append(member)

        return render_template(
            "privateleagues.html",
            leagues=leagues,
            filtered_league=filtered_league,
            matches=matches,
            leaguename=leaguename,
        )


## Access through the profile page, a route for users to create private leagues
@app.route("/createleague", methods=["POST"])
@login_required
def createleague():
    if request.method == "POST":
        ## Validate both fields have been completed
        if not request.form.get("leaguename") or not request.form.get("joiningcode"):
            return
        name = request.form.get("leaguename")
        leaguecount = db.execute(
            "SELECT count(id) as count FROM leagues where name = ?;", name
        )[0]["count"]
        ## Validate the league name doesn't already exist
        if leaguecount > 0:
            return
        code = request.form.get("joiningcode")
        ## Create an entry for the private league in the leagues database
        db.execute(
            "INSERT INTO leagues (ownerid, name, code) VALUES (?, ?, ?);",
            session["user_id"],
            name,
            code,
        )
        currentleague = db.execute("SELECT MAX(id) as id FROM leagues;")[0]["id"]
        ## Add an entry for the league owner into the league memberships database
        db.execute(
            "INSERT INTO league_memberships (memberid, leagueid) VALUES (?, ?);",
            session["user_id"],
            currentleague,
        )
        ## Once create, redirect to the private leagues page
        return redirect("/privateleagues")


## A route for users to join private leagues
@app.route("/joinleague", methods=["POST"])
@login_required
def joinleague():
    if request.method == "POST":
        ## Validate that both fields have been completed
        if not request.form.get("leaguename") or not request.form.get("joiningcode"):
            return
        ## Retrieve details of the league
        league = db.execute(
            "SELECT id, code FROM leagues where name = ?;",
            request.form.get("leaguename"),
        )
        id = league[0]["id"]
        code = league[0]["code"]
        ## Check that the user is not already in the league to prevent multiple entries to the same league from the same user
        leagueentry = db.execute(
            "SELECT count(id) as count from league_memberships where memberid = ? and leagueid = ?;",
            session["user_id"],
            id,
        )
        if leagueentry[0]["count"] > 0:
            return
        ## Confirm the correct joining code has been used
        if code != request.form.get("joiningcode"):
            return
        else:
            ## Insert the user into the private league
            db.execute(
                "INSERT INTO league_memberships (memberid, leagueid) VALUES (?, ?);",
                session["user_id"],
                id,
            )
        return redirect("/privateleagues")
