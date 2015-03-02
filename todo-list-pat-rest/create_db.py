import sqlite3

db = sqlite3.connect('todolist.db')
db.execute("CREATE TABLE todolist (id INTEGER PRIMARY KEY, priority INTEGER NOT NULL, name CHAR(200) NOT NULL, due_date CHAR(100) NOT NULL, done INTEGER NOT NULL)")
db.execute("INSERT INTO todolist (priority, name, due_date, done) VALUES (1, 'Clean up room', 'tomorrow', 0)")
db.execute("INSERT INTO todolist (priority, name, due_date, done) VALUES (2, 'Learn Angular', 'now', 1)")
db.execute("INSERT INTO todolist (priority, name, due_date, done) VALUES (3, 'Washing dishes', 'later', 1)")
db.execute("INSERT INTO todolist (priority, name, due_date, done) VALUES (4, 'Dust fine china', 'right now', 0)")
db.commit()