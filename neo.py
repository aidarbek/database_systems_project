"""
MATCH (a:User),(b:User)
WHERE a.handle = 'a1' AND b.handle = 'a2'
CREATE (a)-[r:FOLLOWS]->(b)
RETURN r
"""
query = """
		MATCH (person {name: "Keanu Reeves"})-[:ACTED_IN]->(movie)<-[:ACTED_IN]-(guy)
		RETURN person.name, guy.name, movie.title;
		"""


from neo4j.v1 import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "neo4j"))

def insert_user(handle):
	session = driver.session()
	query = "CREATE (n:User {handle: \""+ handle + "\", email: \""+ handle + "\",full_name: \""+ handle + "\",phone: \""+ handle + "\",password: \""+ handle + "\"})"
	result = session.run(query)
	session.close()

def insert_relation(handle1, handle2):
	session = driver.session()
	query = """
			MATCH (a:User),(b:User)
			WHERE a.handle = '"""+handle1+"""' AND b.handle = '"""+handle2+"""'
			CREATE (a)-[r:FOLLOWS]->(b)
			RETURN r
	"""
	result = session.run(query)
	session.close()

def add_tweet(handle, tweet, tweet_id):
	session = driver.session()
	
	query = "CREATE (n:Tweet {tweet_id: \""+str(tweet_id)+"\", text: \""+ tweet + "\"})"
	result = session.run(query)

	query = """
			MATCH (a:User),(b:Tweet)
			WHERE a.handle = '"""+handle+"""' AND b.tweet_id = '"""+str(tweet_id)+"""'
			CREATE (a)-[r:TWEETS]->(b)
			RETURN r
	"""
	result = session.run(query)
	
	session.close()

def get_feed(handle):
	session = driver.session()
	query = """
			MATCH (person {handle: \"""" +handle+ """\"})-[:FOLLOWS]->(guy)-[:TWEETS]->(tweet)
			RETURN tweet;
	"""
	result = session.run(query)
	session.close()