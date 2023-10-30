# West Predictions Game
#### Video Demo:  https://youtu.be/8Q8jTfzy7dk
#### Description:

For my final project I've built a website that runs a football match predictions game. The game specifically looks at fixtures for the football club West Didsbury & Chorlton based in Manchester, UK and allows users to predict whether each match will result in a win, a loss or a draw for "West".

After signing up, users and presented with a predictions page showing upcoming fixtures, each of which has a drop down menu allowing for a prediction to be made. Each prediction that has been made is displayed at the top of this page so that users can change their prediction if they choose to.

The next page, "League", displays a league table for all users ordered by the % of predictions that they have made correctly. It also contains some other detail such as how many predictions they have made as a proportion of how many matches of the season have been played.

Next is the provate leagues page. The website contains functionality for users to create leagues that their friends can join. The private leagues page uses a drop down menu so that the user can display which of their private leagues they would like to view.

The profile page contains functionality for a user to update their password and also to create or join provate leagues. For the creation of private leagues the user will provide a code that they can provide to anyone they want to join their league and form to join a league contains a field to validate that code. The league codes are not hashed in the same way as user's passwords as security is not as important for these.

### Python files

#### app.py

app.py contains all the routes and functions that are used to make the website run. This includes routes for each webpage and all the SQL connectivity.

#### helpers.py

helpers.py contains three helper functions.
- login_required(), is referenced from the CS50 pset Finance and is a decorator function used to ensure a user is logged in before they can access any of the other routes.
- percent_format() is used to force specific percentage formatting with jinja.
- create_league_stats() is a function used to compile user's past predictions into a dictionary that represents the current state of their league. I have separated this out into its own function because it is used in more than one place in app.py

#### updates.py

update.py is used to update the database with results after a game has been played. There are no routes that access this and it has to be run manually. The game number and result type are entered as variables and then this is run at the command line.

#### setup.py

setup.py is a file used to set up the initial state of the database. It took match data from fixtures.csv and populated it into the sqlite table "matches"

### Other files

#### nwc.db

This is the sqlite database file that contains all the details of matches and useres predictions. The list of tables includes

- users
- sqlite_sequence
- locations
- result_types
- leagues
- league_memberships
- matches
- predictions

#### templates

A number of html files using jijna to enable dynamic content as well as inheritance. layout.html is my master file with everything else acting as a "block" that is inserted

#### styles.css

A small amount of custom css used in conjunction with bootstrap