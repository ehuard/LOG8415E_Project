import sqlfluff

sql_code = "Select * FROM your_table "

try:
    sqlfluff.parse(sql_code)
    print("SQL code is valid.")
except Exception as err:
    print(f"Linting Error: {err}")