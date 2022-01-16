import os

class Database:
	databasename = os.environ['MONGODB_DATABASE']
	def __init__(self,url):
		import pymongo
		self.url = url
		self.mongoclient = pymongo.MongoClient(self.url)
		self.init_collections()

	def init_collections(self):

		mongoclient = self.mongoclient

		dblist = mongoclient.list_database_names()

		if self.databasename not in dblist:
			print("Creating database")
			mydb = mongoclient[self.databasename]

		mydb = mongoclient[self.databasename]



	## Drops the collections whenever the server quits
	def drop_db(self):  
		mydb = self.mongoclient[self.databasename]

		tasks = mydb["tasks"]
		tasks.drop()

		victims = mydb["victims"]
		victims.drop()

		listeners = mydb["listeners"]
		listeners.drop()