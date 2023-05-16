import pyodbc

cnxn = pyodbc.connect('DRIVER={SQL Server};'' SERVER=localhost;'' DATABASE=Users;'' UID=sa;'' PWD=messino1')

username='crashkk'
password='messino1'

cursor = cnxn.cursor()

result =cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
#result = cursor.fetchone()
print(result)