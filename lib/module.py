import pdb
import os
import pathlib
import sys

class Module:

	def __init__(self,name,utility,language):

		self.name = name
		self.description = None
		self.utility = utility
		self.language = language
		self.script = None

	def load(self):
		## Send command script to victim
		
		module_folder = os.path.join(str(pathlib.Path(__file__).parent.resolve()), "../modules",self.utility)

		sys.path.append(module_folder)
		mod = __import__(self.name)
		
		## capitalize the first letter
		module_name = self.name.title()
		
		module_obj = getattr(mod,module_name)(name=self.name,utility = self.utility, language=self.language)
		self.description = module_obj.description
		self.script = module_obj.script

	