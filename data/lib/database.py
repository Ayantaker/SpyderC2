import os
from lib.victim import Victim
from lib.task import Task

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

	## Checks if previous collections exsists
	def db_data_exists(self):
		mydb = self.mongoclient[self.databasename]
		if len(mydb.list_collection_names()) != 0:
			return True
		else:
			return False

	def load_db_data(self):
		mydb = self.mongoclient[self.databasename]
		if 'tasks' in mydb.list_collection_names():
			Task.load_tasks_from_db()
		if 'victims' in mydb.list_collection_names():
			Victim.load_victims_from_db()
			Victim.load_tasks_to_victim()





	## Drops the collections whenever the server quits
	def drop_db(self):  
		mydb = self.mongoclient[self.databasename]

		tasks = mydb["tasks"]
		tasks.drop()

		victims = mydb["victims"]
		victims.drop()

		listeners = mydb["listeners"]
		listeners.drop()