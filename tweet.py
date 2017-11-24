
#!/usr/bin/python

import MySQLdb
import config

def isOwner(handle, tweet_id):
	db = MySQLdb.connect(config.DB["host"], config.DB["user"], config.DB["password"], config.DB["db"])

	cursor = db.cursor()

	cursor.execute("SELECT Creator FROM tweet WHERE tweet_id={} AND Creator='{}'".format(tweet_id, handle))
		
	result = cursor.fetchone()
		
	db.close()
	if result is None:
		return False	
	return True

def add(handle, text, files):
	db = MySQLdb.connect(config.DB["host"], config.DB["user"], config.DB["password"], config.DB["db"])

	cursor = db.cursor()

	try:
		cursor.execute("INSERT INTO tweet(Creator, content) VALUES('{}', '{}')".format(handle, text))
		tweet_id = cursor.lastrowid
		db.commit()
	except Exception as e:
		print(str(e))
		db.close()
		return None
	try:
		if len(files) > 0:
			for f in files:
				cursor.execute("INSERT INTO attach_list(tweet, file) VALUES({}, {})".format(tweet_id, f))
			db.commit()
	except Exception as e:
		print(str(e))
		db.close()
		return None
	db.close()
	return tweet_id

def likes(user, tweet):
	db = MySQLdb.connect(config.DB["host"], config.DB["user"], config.DB["password"], config.DB["db"])

	cursor = db.cursor()

	try:
		cursor.execute("INSERT INTO likes(handle, tweet_id) VALUES('{}', {})".format(user, tweet))
		db.commit()
	except:
		db.close()
		raise Exception("Couldn't insert")
	db.close()
def delete(tweet):
	db = MySQLdb.connect(config.DB["host"], config.DB["user"], config.DB["password"], config.DB["db"])

	cursor = db.cursor()

	try:
		cursor.execute("DELETE FROM attach_list WHERE tweet = {}".format(tweet))
		cursor.execute("DELETE FROM likes WHERE tweet_id = {}".format(tweet))
		cursor.execute("DELETE FROM tweet WHERE tweet_id = {}".format(tweet))
		db.commit()
	except Exception as e:
		print(str(e))
		raise Exception("Couldn't delete")
	db.close()
def unlikes(user, tweet):
	db = MySQLdb.connect(config.DB["host"], config.DB["user"], config.DB["password"], config.DB["db"])

	cursor = db.cursor()
	try:
		cursor.execute("DELETE FROM likes WHERE handle = '{}' AND tweet_id = {}".format(user, tweet))
		db.commit()
	except:
		db.close()
		raise Exception("Couldn't unlike")
	db.close()
def get(handle, page="feed", limit = 10, last = None, current_user = None):
	"""
		handle - handle of the user. Depending on "page" parameter it can be:
			1) Handle of user, whose feed we would like to get
			2) Handle of user, whose tweets we would like to get
		page - ("feed" or "user" or "search") - get user feed, user tweets or search respectively
		limit - limit number of tweets
		last - ID of the last tweet
	"""

	db = MySQLdb.connect(config.DB["host"], config.DB["user"], config.DB["password"], config.DB["db"])

	cursor = db.cursor()
 	
 	additional_condition = ""

 	if last is not None:
 		# Necessary to continue the tweet
 		additional_condition = "tweet.tweet_id < {} AND ".format(last)

	if page == "feed":
		# User news feed
		cursor.execute("""SELECT tweet.tweet_id,content, Created, Creator, 
			COUNT(likes.handle) FROM tweet 
				LEFT JOIN likes ON likes.tweet_id = tweet.tweet_id 
			WHERE {} (
					tweet.Creator IN 
					(SELECT to_user FROM follows WHERE from_user='{}') 
						OR 
					tweet.Creator = '{}'
				) 
			GROUP BY tweet.tweet_id
			ORDER BY tweet.tweet_id DESC LIMIT {}""".format(additional_condition, handle, handle, limit))
	elif page == "user":
		# Tweets of particular user only
		cursor.execute("""SELECT tweet.tweet_id,content, Created, Creator, 
			COUNT(likes.handle) FROM tweet 
				LEFT JOIN likes ON likes.tweet_id = tweet.tweet_id 
			WHERE {} Creator = '{}' 
			GROUP BY tweet.tweet_id
			ORDER BY tweet_id DESC LIMIT {}""".format(additional_condition, handle, limit))
	elif page == "search":
		# Tweets of particular user only
		cursor.execute("""SELECT tweet.tweet_id,content, Created, Creator, 
			COUNT(likes.handle) FROM tweet 
				LEFT JOIN likes ON likes.tweet_id = tweet.tweet_id 
			WHERE {} content LIKE '%{}%' 
			GROUP BY tweet.tweet_id
			ORDER BY tweet_id DESC LIMIT {}""".format(additional_condition, handle, limit))
	
	results = cursor.fetchall()
	data = []
	for row in results:
		row_data = {}
		row_data["tweet_id"] = row[0]
		row_data["content"] = row[1]
		row_data["Created"] = row[2].strftime('%Y-%m-%d %H:%M:%S')
		row_data["Creator"] = row[3]
		row_data["likes"] = row[4]

		cursor.execute("SELECT file.file_url, file.file_type FROM file INNER JOIN attach_list ON attach_list.file = file.file_id WHERE attach_list.tweet = {}".format(row_data["tweet_id"]))
		files = cursor.fetchall()
		row_data["files"] = [{"file_url": f[0], "file_type": f[1]} for f in files]
		row_data["liked"] = False

		if current_user is not None:
			cursor.execute("SELECT * FROM likes WHERE tweet_id = {} AND handle = '{}' ".format(row_data["tweet_id"], current_user))
			liked = cursor.fetchone()
			if liked is not None:
				row_data["liked"] = True
		data.append(row_data)
	db.close()
	return data

def addFile(data):
	db = MySQLdb.connect(config.DB["host"], config.DB["user"], config.DB["password"], config.DB["db"])

	cursor = db.cursor()

	try:
		cursor.execute("INSERT INTO file(file_url, file_type) VALUES('{}', '{}')".format(data["file_url"], data["file_type"]))
		db.commit()
		cursor.execute("SELECT file_id FROM file ORDER BY file_id DESC LIMIT 1")
		data["file_id"] = cursor.fetchone()[0]
	except Exception as e:
		raise e
	db.close()
	return data

if __name__ == '__main__':
	#add("aidarbek1", "New tweet", [2,3])
	delete(1139)
	#print(get("hello", "search", 10))
	pass