import subprocess
import os
import signal
import pdb
import pathlib

class Listener:
	## Class variable, since database url will be a constant for all listener
	mongoclient = None
	listeners = []
	databasename = os.environ['MONGODB_DATABASE']
	def __init__(self,port):
		self.port = port
		self.pid = None
		self.protocol = 'tcp'

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
		for listener in cls.listeners:
			print(f'Port - {listener.port} , Process ID - {listener.pid}, Protocol - {listener.protocol}')

	@classmethod
	def kill_all_listeners(cls):
		for listener in cls.listeners:
			listener.kill_listener()
			print(f'Killed listeners -> Port - {listener.port} , Process ID - {listener.pid}, Protocol - {listener.protocol}')


	def kill_listener(self):
		os.killpg(os.getpgid(self.pid), signal.SIGTERM)


	def start_listener(self):
		listener_script = os.path.join(str(pathlib.Path(__file__).parent.resolve()), f'../server.py')
		log_dir = os.path.join(str(pathlib.Path(__file__).parent.resolve()), f'../logs')

		try:
			flask_process = subprocess.Popen(f'nohup python3 {listener_script} > {log_dir}/logs 2>&1 &',stdout=subprocess.PIPE, 
						shell=True, preexec_fn=os.setsid)
			

			## Should be changed
			self.pid = flask_process.pid+1
			self.listeners.append(self)
		except subprocess.CalledProcessError as grepexc:
			return False

		return True


		

	def list_listeners(self):
		print(self.port)
		print(self.process)

	def add_to_db(self):
		mydb = self.mongoclient[self.databasename]
		mycol = mydb["listeners"]
		
		h = {'protocol':self.protocol, 'port': self.port, 'pid': self.pid}
		
		mycol.insert_one(h)


class HTTPListener(Listener):
	pass


class HTTPSListener(Listener):
	pass