from bottle import route, run, static_file, request, redirect, post, delete, jinja2_view as jinja
import sqlite3, os, uuid, json

base_dir = os.path.dirname(os.path.realpath(__file__))
static_dir = base_dir + "/static/"
upload_dir = base_dir + "/static/uploaded_images/"

### DATABASE FUNCTIONS ###

# Opens DB
def open_db():
	conn = sqlite3.connect('photoviewer.db')
	cur = conn.cursor()
	return conn, cur

# Closes DB
def close_db(cur, conn):
	cur.close()
	conn.close()

# Fetches album info and user info based on foreign key
def get_albums():
	conn, cur = open_db()
	
	# get user name from users table based on user_id foreign key in albums table
	sql = "select a.name, a.description, u.username, u.fname, u.lname, u.email, a.album_id FROM users u INNER JOIN albums a ON u.user_id = a.user_id;"

	# selects info from albums table
	cur.execute(sql)
	albums = cur.fetchall()

	close_db(cur, conn)
	return albums

# Fetches current users' information
def get_users():
	conn, cur = open_db()
	
	# get user name from users table based on user_id foreign key in albums table
	sql = "select user_id, username, fname, lname from users"

	# selects info from albums table
	cur.execute(sql)
	users = cur.fetchall()

	close_db(cur, conn)
	return users


### MISC FUNCTIONS
def get_uuid():
	return uuid.uuid1()


### ROUTING ###

# Home page
@route('/')
@jinja('home.html', template_lookup=['templates'])
def index():
	context_dict = {'title': 'Home'}
	return context_dict

# Loads static files
@route('/static/<filename>')
def get_static(filename):
	return static_file(filename, root="static")

# Loads images
@route('/static/uploaded_images/<filename>')
def get_images(filename):
	return static_file(filename, root="static/uploaded_images")

# Album page that passes in album info
@route('/albums')
@jinja('albums.html', template_lookup=['templates'])
def albums():
	albums = get_albums()
	users = get_users()
	context_dict = {'title': 'Albums', 'albums': albums, 'users': users}
	if request.query.success == 'yes':
		context_dict['created'] = True
	return context_dict

# Photo page that passes in all photo info
@route('/photos')
@jinja('photos.html', template_lookup=['templates'])
def albums():

	# if request is an AJAX request (?)
	if request.headers.get('Accept') == "application/json, text/plain, */*":

		# grab all the photos
		conn, cur = open_db()
		sql_all_photos = "select photo_id, file_name, file_ext, name, description FROM photos;"
		
		# query to get photos that belong to a particular album
		cur.execute(sql_all_photos)
		results = cur.fetchall()
		close_db(cur, conn)

		# put photos into an array to send to client
		image_data = []
		for index,result in enumerate(results):
			image_data.append([])
			image_data[index] = {}
			image_data[index]['photo_id'] = result[0]
			image_data[index]['file_name'] = result[1]
			image_data[index]['file_ext'] = result[2]
			image_data[index]['name'] = result[3]
			image_data[index]['description'] = result[4]

		return json.dumps(image_data)
	else:
		return {}

# Individual album page that passes in album info
@route('/albums/view')
@jinja('album_view.html', template_lookup=['templates'])
def album_view():

	album = request.query.name
	album_id = request.query.id

	# if it's a normal (non-AJAX request)
	if request.headers.get('Accept') == "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8":

		# check DB to see if album with associated user exists -- if not, return 404 error
		# sql = "select * from albums where name=? and album_id=?"
		
		sql_basic = "select * from albums where name=? and album_id=?"
		conn, cur = open_db()

		# query to see if album and album_id match. If they do, that album with that name exist
		cur.execute(sql_basic, (album, album_id))
		check = cur.fetchall()

		# check to see if the album/album_id combo don't exist
		if not check:
			context_dict = {'title': 'Album view',  'exists': False}
			return context_dict

		user_id = check[0][3]

		# gets user info based on previous query
		sql_get_name = "select * from users where user_id=?"
		cur.execute(sql_get_name, (user_id,))  #check[0][3] user_id pulled from albums
		user_info = list(cur.fetchone())
		print user_info

		close_db(cur, conn)

		# add info to a dictionary and return it
		context_dict = {'title': 'Album view', 'exists': True, 'album_name': album, 'album_id': album_id, 'user_info': user_info}
		return context_dict

	# Else if AJAX request, get photos:
	elif request.headers.get('Accept') == "application/json, text/plain, */*":
		
		conn, cur = open_db()
		sql_album_photos = "select p.photo_id, p.file_name, p.file_ext, p.name, p.description FROM albums a INNER JOIN photos p ON a.album_id = p.album_id where a.name=? and a.album_id=?;"
		
		# query to get photos that belong to a particular album
		cur.execute(sql_album_photos, (album, album_id))
		results = cur.fetchall()
		close_db(cur, conn)

		# put photos into list to send to client side
		image_data = []
		for index,result in enumerate(results):
			image_data.append([])
			image_data[index] = {}
			image_data[index]['photo_id'] = result[0]
			image_data[index]['file_name'] = result[1]
			image_data[index]['file_ext'] = result[2]
			image_data[index]['name'] = result[3]
			image_data[index]['description'] = result[4]

		return json.dumps(image_data)

# Add photo -- AJAX request from angular
@post('/add_photo')
def add_photo():

	# parse data from request -- includes photo, photo form info, user_id and album_id
	photo_form = json.loads(request.forms.get('photo_form'))
	album_id = request.forms.get('album_id')
	user_id = request.forms.get('user_id')
	photo_upload = request.files.get('file')
	photo_user_pass = photo_form['password']
	photo_name = photo_form['name']
	photo_desc = photo_form['desc']

	# get file name and extension
	name, ext = os.path.splitext(photo_upload.filename)

	# check password is valid
	sql_pass = "select * from users where password_hash=? and user_id=?"
	conn, cur = open_db()

	# query to see if album and album_id match. If they do, that album with that name exist
	cur.execute(sql_pass, (photo_user_pass, user_id))
	check_pass = cur.fetchall()

	# if password does not much user_id and that user's password, then return pass_valid = False
	if not check_pass:
		close_db(cur, conn)
		context_dict = {'pass_valid': False}
		return context_dict

	# find out if file type is valid
	if ext.lower() not in ('.png','.jpg','.jpeg', '.gif'):
		close_db(cur, conn)
		context_dict = { 'pass_valid': True, 'valid_type': False }
		return context_dict
	else:
		# valid password and file type, so get UUID, add info to DB and return file name and extension
		photo_uuid = str(get_uuid())
		photo_upload.filename = photo_uuid + ext
		photo_upload.save(upload_dir)

		sql = "insert into photos (file_name, file_ext, name, description, album_id, user_id) values (?,?,?,?,?,?)"
		conn, cur = open_db()
		cur.execute(sql, (photo_uuid, ext, photo_name, photo_desc, album_id, user_id))
		conn.commit()
		close_db(cur, conn)

		# send photo back to client side
		image_data = {}
		image_data['file_name'] = photo_uuid
		image_data['file_ext'] = ext
		image_data['name'] = photo_name
		image_data['description'] = photo_desc

		context_dict = { 'pass_valid': True, 'valid_type': True, 'uploaded': True, 'photo_info': image_data }
		return context_dict

# receives info 
@route('/add_album', method=['POST'])
@jinja('albums.html', template_lookup=['templates'])
def create_album():

	# pull in data from form
	album_name = request.forms.get('albumName')
	album_desc = request.forms.get('albumDesc')
	album_user_id = request.forms.get('userSelect')

	# commit data to database
	sql = "insert into albums (name, description, user_id) values (?,?,?)"
	conn, cur = open_db()
	cur.execute(sql, (album_name, album_desc, album_user_id))
	conn.commit()
	close_db(cur, conn)

	redirect('/albums?success=yes')

# deletes photo in database and in static folder
@delete('/delete-photo')
def delete_photo():
	# get id of photo sent over
	photo_id = request.query.photo_id

	# make sure entry exists for that photo id, and retrieve file name and ext so they can be removed
	sql_verify = "select file_name, file_ext from photos where photo_id=?"
	conn, cur = open_db()
	cur.execute(sql_verify, (photo_id,))
	photo = cur.fetchone()

	# check to see if photo exists with that photo_id
	if photo:

		# delete from database
		sql_delete = "DELETE FROM photos WHERE photo_id=?"
		cur.execute(sql_delete, (photo_id,))
		conn.commit()

		# delete actual file
		file_name_full = "".join(photo)
		os.remove(upload_dir + file_name_full)
		close_db(cur, conn)

		context_dict = {'success': True}

	else:
		# photo was not deleted
		context_dict = {'success': False}
	
	return context_dict

# Runs server
run(host="localhost", port="8082")






