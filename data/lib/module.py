import pdb
import os
import pathlib
import sys
from termcolor import colored
import readline
import re

class Module:
	## Has the task ID to module object mapping
	module_task_id = {}

	def __init__(self,name,description,utility,language,script):

		self.name = name
		self.description = description
		self.utility = utility
		self.language = language
		self.script = script

	@classmethod
	def module_help_menu(self):
		pass

	@classmethod
	def module_menu(cls,module,utility):
		module_options = cls.get_options(module,utility)
		option_hash = {}

		while True:
			print(colored(f"Interacting with {module}. Once done configuring module, press 'run' to run it on vicitim.",'green'))

			cmd = str(input())
			if re.match(r'^set ([^ ]+) ([^ ]+)$',cmd):
				info = re.findall(r'^set ([^ ]+) ([^ ]+)$',cmd)
				## TODO - error handling
				option = info[0][0]
				value = info[0][1]

				if option not in module_options.keys():
					print(colored(f"Invalid option - {option} for module {module}",'yellow'))
				else:
					option_hash[option] = value
					print(colored(f"{option} set to {value}",'green'))
			elif cmd == 'options':
					cls.show_options(module,utility)
			elif cmd == 'execute' or cmd == 'run':
				return option_hash
			elif cmd == 'help':
				cls.module_help_menu()
			elif cmd == 'back' or cmd == 'exit':
				## TODO handle this
				return False


	@classmethod
	def get_options(cls,module,utility):
		module_folder = os.path.join(str(pathlib.Path(__file__).parent.resolve()), "../modules",utility)

		sys.path.append(module_folder)
		mod = __import__(module)
		
		## capitalize the first letter
		module_name = module.title()
		
		module_options = getattr(mod,module_name).module_options()

		return module_options
	@classmethod
	def show_options(cls,module,utility):
		
		module_options = cls.get_options(module,utility)
		print(' --------------------------------------')
		print('|          MODULE OPTIONS             |')
		print(' --------------------------------------')

		for key in module_options.keys():
			print(f"{colored(key,'cyan')} - {module_options[key]}")