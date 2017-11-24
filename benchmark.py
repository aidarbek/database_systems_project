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
	data = tweet.get(handle = handle, page="feed", limit = 10000)
	sql_time = time.clock() - start_sql

	# Benchmark Neo4j
	start_neo = time.clock()
	neo.get_feed(handle)
	neo_time = time.clock() - start_neo

	if i == start_id:
		continue

	sum_sql += sql_time
	sum_neo += neo_time

print("SQL average feed time for 1000 records: " + str(sum_sql / n))
print("Neo4j average feed time for 1000 records: " + str(sum_neo / n))

