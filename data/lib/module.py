import pdb
import os
import pathlib
import sys
from termcolor import colored
from lib.style import Style
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
	def module_help_menu(cls):
		pass

	## takes in the option hash defined in each modules and returns the required ones
	@classmethod
	def get_required_options(cls,module_options):
		required_options = []
		for option_name in module_options.keys():
			if module_options[option_name]['required'] == True:
				required_options.append(option_name)
		return required_options

	@classmethod
	def module_menu(cls,module,utility):
		module_options,description = cls.get_options(module,utility)
		required_options = cls.get_required_options(module_options)
		option_hash = {}

		while True:
			cmd = str(input(colored(f"\n(SpyderC2: Victim: Module) {colored(module,'cyan')} > ",'red')))
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
				unfilled_options = [item for item in required_options if item not in list(option_hash.keys())]

				if len(unfilled_options) > 0 :
					## User needs to set values for these options as they are required
					print(colored(f"Set some values for these options as they are required : {', '.join(unfilled_options)}. Use : set <option_name> <option_value>",'yellow'))
					continue
				else:
					return option_hash

			elif cmd == 'help':
				cls.module_help_menu()
			elif cmd == 'back' or cmd == 'exit':
				## TODO handle this
				return False
			elif cmd == '':
				print()
				pass
			else:
				print(f"Not supported. Type {colored('help','cyan')} to see commands supported.")


	@classmethod
	def get_options(cls,module,utility):
		module_folder = os.path.join(str(pathlib.Path(__file__).parent.resolve()), "../modules",utility)

		sys.path.append(module_folder)
		mod = __import__(module)
		
		## capitalize the first letter
		module_name = module.title()
		
		module_options = getattr(mod,module_name).module_options()
		description = getattr(mod,module_name).description

		return module_options,description
	@classmethod
	def show_options(cls,module,utility):
		print(colored(f"\n\nInteracting with {colored(module,'cyan')}. You can configure the options below by {colored('set <option_name> <option_value>','cyan')}. Once done configuring module, press {colored('run','cyan')} to run it on vicitim."))
		module_options,description = cls.get_options(module,utility)

		print(f"\n{colored(module.upper(),'blue')} : {description}\n")
		row = []
		for key in module_options.keys():
			row.append([key,str(module_options[key]['required']),module_options[key]['desc']])

		column = {
			"Name" : {'style':"cyan"},
			"Required":{'style':"cyan"},
			"Description":{'justify':"left", 'no_wrap':False}
		}

		s = Style()
		s.create_table("MODULE CONFIGURABLE OPTIONS",column,row,'center')


		
		