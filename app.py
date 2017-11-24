#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, Response
from flask import request
from flask import abort, redirect, url_for
from flask import render_template
import os
import json
from flask import jsonify, send_from_directory
from flask.ext.cors import CORS, cross_origin
import notification
from werkzeug.routing import BaseConverter

from user import User
import tweet
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__, static_url_path='/uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class RegexConverter(BaseConverter):
	def __init__(self, url_map, *items):
		super(RegexConverter, self).__init__(url_map)
		self.regex = items[0]
app.url_map.converters['regex'] = RegexConverter

app.secret_key = "Key"
app.debug = True


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<path>')
def send_img(path):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               path)

@app.route('/uploads/open-iconic/font/css/<path>')
def send_css(path):
    return send_from_directory(app.config['UPLOAD_FOLDER'] + "/open-iconic/font/css",
                               path)
@app.route('/uploads/open-iconic/font/fonts/<path>')
def send_fonts(path):
    return send_from_directory(app.config['UPLOAD_FOLDER'] + "/open-iconic/font/fonts",
                               path)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return "Nothing"
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return "No filename"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            data = {}
            data["file_url"] = "/uploads/" + filename
            data["file_type"] = file.filename.rsplit('.', 1)[1].lower()

            data = tweet.addFile(data)

            p = json.dumps(data)

            resp = Response(response=p,
                    status=200,
                    mimetype="text/plain")
            return resp
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

@app.route("/", methods=['GET'])
def index():
	
	handle = request.cookies.get('handle')
	if handle is not None:
		user = User(handle)
		user.setAuth()
		user_data = user.getInfo()
		return render_template("feed.html", handle = handle, full_name = user_data["full_name"], email = user_data["email"])
	return render_template("index.html")

@app.route("/search", methods=['GET'])
def search_controller():
	
	handle = request.cookies.get('handle')

	search = request.args.get('q')

	if handle is not None:
		user = User(handle)
		user.setAuth()
		user_data = user.getInfo()
		return render_template("search.html", handle = handle, full_name = user_data["full_name"], email = user_data["email"], search = search)
	return render_template("index.html")

@app.route("/", methods=['POST'])
def register():
	handle = str(request.form["handle"].encode('utf-8'))
	email = str(request.form["email"].encode('utf-8'))
	full_name = str(request.form["full_name"].encode('utf-8'))
	phone = str(request.form["phone"].encode('utf-8'))
	password = str(request.form["password"].encode('utf-8'))

	data = {"success": "User have been registered"}
	
	user = User()

	try:
		user.register(handle, email, full_name, phone, password)
	except:
		data = {"error": "Couldn't register user! Check handle or email"}
	p = json.dumps(data)
	resp = Response(response=p,
                    status=200,
                    mimetype="text/plain")
	return resp

@app.route("/login", methods=['POST'])
def login():
	
	tmp_handle = request.cookies.get('handle')

	handle = request.form["handle"]

	password = request.form["password"]

	data = {"success": "You logged in"}
	
	user = User(handle, password)

	if not user.isAuth():
		handle = None
		data = {"error": "Couldn't log in user!"}
	else:
		data = {"success": "You logged in!"}

	p = json.dumps(data)
	resp = Response(response=p,
                    status=200,
                    mimetype="text/plain")
	
	if handle is not None:
		resp.set_cookie("handle", handle)
	
	return resp

@app.route("/tweet", methods=['POST'])
def add_tweet():
	
	handle = request.cookies.get('handle')
	
	data = {}

	if handle is not None:
		text = request.form["text"]
		files = request.form["files"] # Comma separated list of file_id
		if files == "":
			files = []
		else:
			files = files.split(",")

		tweet_id = tweet.add(handle, text, files)

		if tweet_id is None:
			data["error"] = "Error occured while adding the tweet"
		else:
			data["success"] = "Tweet added"

	p = json.dumps(data)
	resp = Response(response=p,
                    status=200,
                    mimetype="text/plain")
	
	if handle is not None:
		resp.set_cookie("handle", handle)
	
	return resp

@app.route("/follow", methods=['POST'])
def follow():
	from_handle = request.cookies.get('handle')
	to_handle = request.form["handle"]
	data = {"error": "You must log in!"}
	if from_handle is not None:
		user = User(from_handle)
		user.setAuth()

		try:
			data = {"success": "You followed the user!"}
			user.follow(to_handle)
		except:
			try:
				user.unfollow(to_handle)
				data = {"success": "You unfollowed the user!"}
			except:
				data = {"error": "Couldn't follow the user"}
	p = json.dumps(data)
	resp = Response(response=p,
                    status=200,
                    mimetype="text/plain")
	return resp

@app.route("/notification/count", methods=['GET'])
def notification_count():
	handle = request.cookies.get('handle')
	data = {"count": 0}
	print(handle)
	if handle is not None:
		try:
			data["count"] = notification.count(handle)
		except Exception as e:
			print(str(e))
			data["count"] = 0
	p = json.dumps(data)
	resp = Response(response=p,
                    status=200,
                    mimetype="text/plain")
	return resp

@app.route("/notification", methods=['GET'])
def notification_page():
	handle = request.cookies.get('handle')
	data = {"notifications": []}
	if handle is not None:
		try:
			data["notifications"] = notification.get(handle)
		except:
			data["notifications"] = []

		user = User(handle)
		user.setAuth()
		user_data = user.getInfo()
		return render_template("notification.html", handle = handle, full_name = user_data["full_name"], email = user_data["email"],
			notifications = data["notifications"])
	else:
		return render_template("index.html")

@app.route("/notification", methods=['POST'])
def notification_get():
	handle = request.cookies.get('handle')
	data = {"notifications": []}
	if handle is not None:
		try:
			data["notifications"] = notification.get(handle)
		except:
			data["notifications"] = []
	p = json.dumps(data)
	resp = Response(response=p,
                    status=200,
                    mimetype="text/plain")
	return resp


@app.route("/like", methods=['POST'])
def like():
	handle = request.cookies.get('handle')
	tweet_id = request.form["tweet_id"]
	data = {"success": "You liked tweet!"}
	if handle is not None:
		try:
			tweet.likes(handle, tweet_id)
		except:
			try:
				tweet.unlikes(handle, tweet_id)
				data = {"success": "You unliked the tweet!"}
			except:
				data = {"error": "Couldn't unlike the tweet"}
	p = json.dumps(data)
	resp = Response(response=p,
                    status=200,
                    mimetype="text/plain")
	return resp



@app.route("/tweet/delete", methods=['POST'])
def tweet_delete():
	handle = request.cookies.get('handle')
	tweet_id = request.form["tweet_id"]
	data = {"success": "You delete tweet!"}
	if handle is not None:
		try:
			if tweet.isOwner(handle, tweet_id):
				tweet.delete(tweet_id)
		except Exception as e:
			print(str(e))
			data = {"error": "Couldn't unlike the tweet"}
	p = json.dumps(data)
	resp = Response(response=p,
                    status=200,
                    mimetype="text/plain")
	return resp

@app.route("/tweet/feed", methods=['GET'])
def feed():
	handle = request.cookies.get('handle')

	last = request.args.get('last')
	data = {}
	if handle is not None:
		data = tweet.get(handle, "feed", 10, last, handle)
	p = json.dumps(data)
	resp = Response(response=p,
                    status=200,
                    mimetype="text/plain")
	return resp

@app.route("/tweet/search", methods=['GET'])
def search():
	handle = request.cookies.get('handle')

	last = request.args.get('last')
	search = request.args.get('q')
	
	print(handle)
	print(search)

	data = {}
	if handle is not None:
		data = tweet.get(search, "search", 10, last, handle)
	p = json.dumps(data)
	resp = Response(response=p,
                    status=200,
                    mimetype="text/plain")
	return resp

@app.route("/logout", methods=['GET'])
def logout():
	handle = request.cookies.get('handle')
	p = ""
	if handle is not None:
		p = "You logged out"
	headers = {
        'Location': '/'
    }
	resp = redirect(url_for("index"))
	if handle is not None:
		resp.set_cookie("handle", '', expires=0)
	
	return resp
	return redirect(url_for("index"))

@app.route('/user/<handle>', methods=['GET'])
def profile(handle):
	user = User(handle)
	data = {}
	
	current_user = request.cookies.get('handle')
	last = request.args.get('last')

	if user.getHandle() is not None:

		data = tweet.get(handle, "user", 10, last, current_user)
	
		p = json.dumps(data)

		resp = Response(response=p,
	                    status=200,
	                    mimetype="text/plain")
	else:
		resp = Response(response="User not found",
	                    status=404,
	                    mimetype="text/plain")
	return resp

@app.route('/settings', methods=['GET', 'POST'])
def settings():
	
	current_user = request.cookies.get('handle')
	if current_user is not None:
		authorised = True
	else:
		authorised = False
		return redirect(url_for("index"))
	
	user = User(current_user)

	if request.method == 'POST':
		email = str(request.form["email"].encode('utf-8'))
		full_name = str(request.form["full_name"].encode('utf-8'))
		phone = str(request.form["phone"].encode('utf-8'))
		photo_url = str(request.form["photo_url"].encode('utf-8'))
		user.update(["email", "full_name", "phone_number", "photo_url"], 
			[email, full_name, phone, photo_url])
	
	data = user.getInfo()
	if user.getHandle() is not None:

		if data["photo_url"] == "":
			data["photo_url"] = "http://via.placeholder.com/200x150"

		resp = render_template("settings.html", data = data, handle = current_user)
	else:
		resp = Response(response="User not found",
	                    status=404,
	                    mimetype="text/plain")
	return resp

@app.route('/<handle>', methods=['GET'])
def profile_page(handle):
	user = User(handle)
	data = {}
	
	current_user = request.cookies.get('handle')
	if current_user is not None:
		authorised = True
	else:
		authorised = False
	if user.getHandle() is not None:

		data = user.getInfo()

		if data["photo_url"] == "":
			data["photo_url"] = "http://via.placeholder.com/200x150"

		resp = render_template("user.html", handle=data["handle"], full_name=data["full_name"], 
			followers = data["followers"], following = data["following"], photo_url = data["photo_url"], current_user = current_user,
			authorised = authorised, followed = user.followedBy(current_user), current_user_page = current_user == data["handle"])
	else:
		resp = Response(response="User not found",
	                    status=404,
	                    mimetype="text/plain")
	return resp

if __name__ == "__main__":
    app.run(threaded=True)