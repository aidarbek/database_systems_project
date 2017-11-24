
#!/usr/bin/python

import MySQLdb
import config

class User:

	def __init__(self, login = None, password = None):
		"""
			Class constructor can become also authorization function
		"""
		self.handle = None
		self.auth = False

		if login != None:
			if self.__exists(login):
				self.handle = login
			else:
				self.handle = None

			if password != None:
				if self.__login(password):
					self.auth = True
				else:
					self.auth = False

	def isAuth(self):
		return self.auth
	
	def setAuth(self):
		self.auth = True

	def getHandle(self):
		return self.handle

	def getInfo(self):
		db = MySQLdb.connect(config.DB["host"], config.DB["user"], config.DB["password"], config.DB["db"])

		cursor = db.cursor()

		cursor.execute("SELECT handle, full_name, email, phone_number, photo_url FROM user WHERE handle='{}'".format(self.handle))
		data = {}
		data["handle"], data["full_name"], data["email"], data["phone"], data["photo_url"] = cursor.fetchone()
		
		cursor.execute("SELECT COUNT(*) FROM follows WHERE from_user='{}'".format(self.handle))
		data["following"] = cursor.fetchone()[0]

		cursor.execute("SELECT COUNT(*) FROM follows WHERE to_user='{}'".format(self.handle))
		data["followers"] = cursor.fetchone()[0]

		db.close()
		return data
	def followedBy(self, handle):
		if handle is None:
			return False
		db = MySQLdb.connect(config.DB["host"], config.DB["user"], config.DB["password"], config.DB["db"])

		cursor = db.cursor()

		cursor.execute("SELECT from_user FROM follows WHERE from_user='{}' AND to_user='{}'".format(handle, self.handle))
		follows = cursor.fetchone()
		db.close()
		if follows is not None:
			return True
		return False
	def update(self, columns, values):
		set_string = ""

		if len(columns) != len(values):
			raise Exception("Columns do not match values!")

		set_string = ",".join([columns[i] + "='" + values[i]+"'" for i in range(len(columns))])

		db = MySQLdb.connect(config.DB["host"], config.DB["user"], config.DB["password"], config.DB["db"])

		cursor = db.cursor()
		cursor.execute("UPDATE user SET {} WHERE handle = '{}'".format(set_string, self.handle))
		db.commit()
		db.close()
	def __exists(self, handle):

		db = MySQLdb.connect(config.DB["host"], config.DB["user"], config.DB["password"], config.DB["db"])

		cursor = db.cursor()

		cursor.execute("SELECT handle FROM user WHERE handle='{}'".format(handle))
		
		handle = cursor.fetchone()
		
		db.close()
		if handle is None:
			return False
		return True

	def register(self, handle, email, full_name, phone, password):
		db = MySQLdb.connect(config.DB["host"], config.DB["user"], config.DB["password"], config.DB["db"])

		cursor = db.cursor()

		try:
			cursor.execute("INSERT INTO user(handle, email, full_name, phone_number, password) VALUES('{}', '{}', '{}', '{}', '{}')".format(handle, email, full_name, phone, password))
			db.commit()
		except:
			db.close()
			raise Exception("Couldn't create user")
		db.close()

	def __login(self, password):
		db = MySQLdb.connect(config.DB["host"], config.DB["user"], config.DB["password"], config.DB["db"])

		cursor = db.cursor()

		cursor.execute("SELECT handle FROM user WHERE handle='{}' AND password='{}'".format(self.handle, password))
		
		handle = cursor.fetchone()
		
		db.close()
		if handle is None:
			return False	
		return True

	def follow(self, to_user):
		db = MySQLdb.connect(config.DB["host"], config.DB["user"], config.DB["password"], config.DB["db"])

		cursor = db.cursor()

		try:
			if self.isAuth():
				cursor.execute("INSERT INTO follows(from_user, to_user) VALUES('{}', '{}')".format(self.handle, to_user))
				cursor.execute("INSERT INTO notification(content, url, handle) VALUES('@{} user followed you', '/{}', '{}')".format(self.handle, self.handle, to_user))
				db.commit()
			else:
				raise Exception("")
		except:
			db.close()
			raise Exception("Couldn't insert")
		db.close()

	def unfollow(self, to_user):
		db = MySQLdb.connect(config.DB["host"], config.DB["user"], config.DB["password"], config.DB["db"])

		cursor = db.cursor()
		try:
			if self.isAuth():
				cursor.execute("DELETE FROM follows WHERE from_user = '{}' AND to_user = '{}'".format(self.handle, to_user))
				db.commit()
			else:
				raise Exception("")
		except:
			db.close()
			raise Exception("Couldn't unfollow")
		db.close()


if __name__ == '__main__':
	user = User("aidarbek1", "qwerty")
	user.update(["full_name"], ["Aidarbek Suleimenov"])
	pass