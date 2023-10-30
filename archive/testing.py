from cs50 import SQL

db = SQL("sqlite:///nwc.db")

league = db.execute("select u.username, count(p.id) as predictions, sum(case when p.correct = 1 then 1 else 0 end) as correct from users u left join predictions p on p.user_id = u.id and p.correct is not null group by u.username")
matches = db.execute("select count(id) as played from matches where result_id is not null")[0]['played']

for member in league:
    member['Total games'] = matches
    member['Predictions made'] = float(member['predictions']/matches)
    if member['predictions'] == 0:
        member['Correct %'] = 0
    else:
        member['Correct %'] = float(member['correct']/member['predictions'])

print(league)