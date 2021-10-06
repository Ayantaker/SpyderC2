class Database:
	def __init__(self,url):
		import pymongo
		self.url = url
		self.mongoclient = pymongo.MongoClient(self.url)
		self.init_collections()

	def init_collections(self):

		mongoclient = self.mongoclient

		dblist = mongoclient.list_database_names()

		if "pythonc2" not in dblist:
			print("Creating database")
			mydb = mongoclient["pythonc2"]

		mydb = mongoclient["pythonc2"]



	## Drops the collections whenever the server quits
	def drop_db(self):  
		mydb = self.mongoclient["pythonc2"]

		tasks = mydb["tasks"]
		tasks.drop()

		victims = mydb["victims"]
		victims.drop()

		listeners = mydb["listeners"]
		listeners.drop()