from flask import redirect, session
from functools import wraps


## Decorator function sourced from week 9 pset Finance.
## Forces a redirect to the "/login" route when the current session contains no "user_id"
def login_required(f):
    """
    Decorate routes to require login.

    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


## Formatting function used in jinja to render percentages as percentages in league tables.
def percent_format(value):
    value *= 100
    return f"{value:.1f}%"


## Create a league that contains all details
def create_league_stats(league, matches):
    ## For each user calcuate the percentage of predictions that were correct and
    ## the number of predictions made compared with the total number of matches.
    ## Add both to the "league" dictionary
    for member in league:
        member["Total games"] = matches
        member["Predictions made"] = float(member["predictions"] / matches)
        if member["predictions"] == 0:
            member["Correct %"] = 0
        else:
            member["Correct %"] = float(member["correct"] / member["predictions"])

    ## Sort league dictionary based on two keys, % of correct predictions and number of predicitions made
    sorted_league = sorted(
        league, key=lambda x: (x["Correct %"], x["predictions"]), reverse=True
    )

    return sorted_league
