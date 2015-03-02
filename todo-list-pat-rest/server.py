import os, sqlite3, json
from bottle import route, run, static_file, request, abort, redirect, post, delete, put

base_dir = os.path.dirname(os.path.realpath(__file__))

@route('/')
def index():
	return static_file('index.html', root=base_dir+"/static/")

@route('/static/<filename>')
def get_static(filename):
	return static_file(filename, root=base_dir+"/static/")

# responds to AJAX request
@route('/get-todo-list')
def get_todo_list():

	if request.headers.get('Accept') == "application/json, text/plain, */*":

		# opens database, gets info from inside and puts it into data var
		db = sqlite3.connect('todolist.db')
		c = db.cursor()
		c.execute("SELECT * FROM todolist")
		data = c.fetchall()
		c.close()

		return generate_list(data)
	else:
		# abort(401, "\tSorry, access denied unless you're an AJAX request.")
		redirect("/")

# add entry to database
@post('/add-entry')
def add_entry():

	# POST data in json format
	pd = request.json

	# converts boolean to integer for sqlite3
	if not pd['done']:
		pd['done'] = 0
	else:
		pd['done'] = 1

	# opens database, inserts new entry and fetches whole list
	db = sqlite3.connect('todolist.db')
	c = db.cursor()
	c.execute("INSERT INTO todolist (priority, name, due_date, done) VALUES ("+ str(pd['id']) +", " + "'" + pd['name'] + "'" + ", " + "'" + pd['due_date'] + "'" + ", " + str(pd['done']) + ")")
	db.commit()
	c.execute("SELECT * FROM todolist")
	data = c.fetchall()
	c.close()

	return generate_list(data)

# deletes entry in database
@delete('/delete-entry')
def delete_entry():
	id = request.query.priority

	# opens database, deletes row and grabs updated list to spit out
	db = sqlite3.connect('todolist.db')
	c = db.cursor()
	c.execute("DELETE FROM todolist WHERE priority == " + id)
	db.commit()
	c.execute("SELECT * FROM todolist")
	data = c.fetchall()
	c.close()

	return generate_list(data)

@put('/update-done-field')
def update_done_field():
	update = request.json
	
	# opens database, deletes row and grabs updated list to spit out
	db = sqlite3.connect('todolist.db')
	c = db.cursor()
	if update['done'] == False: 
		c.execute("UPDATE todolist SET done = 0 WHERE priority == " + str(update['priority']))
	else:
		c.execute("UPDATE todolist SET done = 1 WHERE priority == " + str(update['priority']))
	db.commit()
	c.execute("SELECT * FROM todolist")
	data = c.fetchall()
	c.close()

	return generate_list(data)

@put('/update-priority-field')
def update_priority_field():
	update = request.json

	# opens database, deletes row and grabs updated list to spit out
	db = sqlite3.connect('todolist.db')
	c = db.cursor()
	c.execute("UPDATE todolist SET priority = " + str(update['new_pr']) + " WHERE id == " + str(update['db_id']))
	db.commit()
	c.execute("SELECT * FROM todolist")
	data = c.fetchall()
	c.close()

	return generate_list(data)

@put('/update-entry-text')
def update_entry_text():
	update = request.json

	# opens database, deletes row and grabs updated list to spit out
	db = sqlite3.connect('todolist.db')
	c = db.cursor()
	c.execute("UPDATE todolist SET name = " + "'" +  update['task'] + "'" +  ", due_date = " +  "'" + update['due_date'] +  "'" + " WHERE id == " + str(update['db_id']))
	db.commit()
	c.execute("SELECT * FROM todolist")
	data = c.fetchall()
	c.close()

	return generate_list(data)

# takes database tuples and generates python list, returned in json format
def generate_list(data):
	# loops through data putting into dictionary to be converted into json
	export_data = []
	for index, entry in enumerate(data):
		export_data.append([])
		export_data[index] = {}
		export_data[index]['db_id'] = entry[0]
		export_data[index]['id'] = entry[1]
		export_data[index]['task'] = entry[2]
		export_data[index]['due_date'] = entry[3]
		if entry[4] == 0:
			export_data[index]['done'] = False
		elif entry[4] == 1:
			export_data[index]['done'] = True

	return json.dumps(export_data)

run(host="localhost", port="8081", debug=True)