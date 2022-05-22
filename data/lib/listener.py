import subprocess
import os
import signal
import pdb
import pathlib
import socket
from rich.text import Text
from lib.style import Style
from rich import print as pprint

class Listener:
	## Class variable, since database url will be a constant for all listener
	mongoclient = None
	listeners = []
	databasename = os.environ['MONGODB_DATABASE']

	def __init__(self,port):
		self.port = port
		self.pid = None
		self.protocol = 'tcp'
		self.status = 'Stopped'


	## Checks whether a listener object already exists for that port, if true returns that object
	@classmethod
	def listener_exists(cls,port):
		for listener in cls.listeners:
			if listener.port == port:
				return listener

		return False
	@classmethod
	def fetch_from_db(cls):
		mydb = cls.mongoclient[cls.databasename]
		mycol = mydb["listeners"]

		listeners = mycol.find()

		listener_dict = {}
		i = 0
		for listener in listeners:
			if 'sample' not in listener.keys():
				del listener['_id']
				listener_dict[i] = listener
				i+=1
		
		return listener_dict

	@classmethod
	def show_listeners(cls):
		print("")
		row = []
		for listener in cls.listeners:
			listener.is_listener_running()
			status = Text(listener.status)
			status.stylize("red") if listener.status == 'Stopped' else status.stylize("blink bold green")
			row.append([listener.port,str(listener.pid),listener.protocol,status])
			print(f'Port - {listener.port} , Process ID - {listener.pid}, Protocol - {listener.protocol} , Status - {listener.status}')
			

		column = {
			"Port" : {'style':"gold3"},
			"Process ID":{},
			"Protocol": {},
			"Status":{}
		}

		s = Style()
		s.create_table("[gold3]LISTENERS[/gold3]",column,row,'center')

	@classmethod
	def kill_all_listeners(cls):
		for listener in cls.listeners:
			## Only kill running listeners
			listener.is_listener_running()
			if listener.status == 'Running':
				listener.kill_listener()
				print(f'Killed listeners -> Port - {listener.port} , Process ID - {listener.pid}, Protocol - {listener.protocol}')


	def is_listener_running(self):
	    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	        if s.connect_ex(('localhost', int(self.port))) == 0:
	        	self.status = 'Running'
	        	return True
	        else:
	        	self.status = 'Stopped'
	        	return False

	def kill_listener(self):
		os.killpg(os.getpgid(self.pid), signal.SIGTERM)


	def start_listener(self):
		listener_script = os.path.join(str(pathlib.Path(__file__).parent.resolve()), f'../server.py')
		log_dir = os.path.join(str(pathlib.Path(__file__).parent.resolve()), f'../logs')

		if not self.is_listener_running():
			flask_process = subprocess.Popen(f'nohup python3 {listener_script} {self.port} > {log_dir}/logs 2>&1 &', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
			stdout, stderr = flask_process.communicate()
			if flask_process.returncode != 0:
				pprint(f"[red]\nError running server : {stdout}[/red]")
				return False

			self.pid = flask_process.pid +1
			if self not in self.listeners: self.listeners.append(self)

			return True
		else:
			## Port in use
			return False

		
		

	def list_listeners(self):
		print(self.port)
		print(self.process)

	## no real need to add listeners to db
	# def add_to_db(self):
	# 	mydb = self.mongoclient[self.databasename]
	# 	mycol = mydb["listeners"]
		
	# 	h = {'protocol':self.protocol, 'port': self.port, 'pid': self.pid}
		
	# 	mycol.insert_one(h)


class HTTPListener(Listener):
	pass


class HTTPSListener(Listener):
	pass