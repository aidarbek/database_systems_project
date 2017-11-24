#!/usr/bin/python

import MySQLdb
import config

def get(handle):
	db = MySQLdb.connect(config.DB["host"], config.DB["user"], config.DB["password"], config.DB["db"])

	cursor = db.cursor()

	cursor.execute("SELECT `id`, `content`, `url` FROM `notification` WHERE `handle`='{}' AND `read` = 0 LIMIT 10".format(handle))
		
	result = cursor.fetchall()

	data = []
	notifications = []
	for row in result:
		row_data = {}
		row_data["content"] = row[1]
		row_data["url"] = row[2]
		data.append(row_data)
		notifications.append(str(row[0]))
	if len(notifications) > 0:
		cursor.execute("UPDATE `notification` SET `read` = 1   WHERE `id` IN({})".format(",".join(notifications)))
		db.commit()

	db.close()
	return data
def count(handle):
	db = MySQLdb.connect(config.DB["host"], config.DB["user"], config.DB["password"], config.DB["db"])

	cursor = db.cursor()

	cursor.execute("SELECT COUNT(`id`) FROM `notification` WHERE `handle`='{}' AND `read` = 0 ".format(handle))
		
	result = cursor.fetchone()[0]

	db.close()

	return result
if __name__ == '__main__':
	print(count("aidarbek1"))
	pass