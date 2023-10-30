from cs50 import SQL

## This file is used to update the results of games and users' predictions
## after a match day

db = SQL("sqlite:///nwc.db")

# update match and result variables then run
match = 8
result = 1

db.execute("UPDATE predictions SET correct = 0 WHERE match_id = ?", match)
db.execute("UPDATE matches SET result_id = ? WHERE id = ?", result, match)
db.execute("UPDATE matches SET visible = 0 WHERE id = ?", match)
db.execute(
    "UPDATE predictions SET correct = 1 WHERE match_id = ? and prediction = ?",
    match,
    result,
)
