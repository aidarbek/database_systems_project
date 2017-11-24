import user

import time

import neo

import tweet

sum_neo = 0.0
sum_sql = 0.0

start_id = 1
end_id = 1001

n = (end_id - start_id) * 1.0

for i in range(start_id, end_id):
	handle = "a" + str(i)

	# Benchmark SQL
	start_sql = time.clock()
	user.register(handle, handle, handle, handle, handle)
	sql_time = time.clock() - start_sql

	# Benchmark Neo4j
	start_neo = time.clock()
	neo.insert_user(handle)
	neo_time = time.clock() - start_neo

	if i == start_id:
		continue

	sum_sql += sql_time
	sum_neo += neo_time

print("SQL average user adding time of 1000 records: " + str(sum_sql / n))
print("Neo4j average user adding time of 1000 records: " + str(sum_neo / n))
sum_neo = 0.0
sum_sql = 0.0
for i in range(start_id, end_id):
	for j in range(start_id, end_id):

		if i == j:
			continue
		handle1 = "a" + str(i)
		handle2 = "a" + str(j)

		# Benchmark SQL
		start_sql = time.clock()
		user.follow(handle1, handle2)
		sql_time = time.clock() - start_sql

		# Benchmark Neo4j
		start_neo = time.clock()
		neo.insert_relation(handle1, handle2)
		neo_time = time.clock() - start_neo

		if i == start_id and j == start_id:
			continue

		sum_sql += sql_time
		sum_neo += neo_time

print("SQL average relationship adding time of 1000 records: " + str(sum_sql / n))
print("Neo4j average relationship adding time of 1000 records: " + str(sum_neo / n))

sum_neo = 0.0
sum_sql = 0.0

for i in range(start_id, end_id):
	handle = "a" + str(i)
	text = "What a good day!"
	tweet_id = i

	# Benchmark SQL
	start_sql = time.clock()
	tweet.add(handle, text, "")
	sql_time = time.clock() - start_sql

	# Benchmark Neo4j
	start_neo = time.clock()
	neo.add_tweet(handle, text, tweet_id)
	neo_time = time.clock() - start_neo
	
	if i == start_id:
		continue

	sum_sql += sql_time
	sum_neo += neo_time

print("SQL average tweet adding time of 1000 records: " + str(sum_sql / n))
print("Neo4j average tweet adding time of 1000 records: " + str(sum_neo / n))


