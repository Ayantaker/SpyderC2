import logging
import os
import pdb
import pathlib
from termcolor import colored
import datetime
import subprocess

class Logger:

	def __init__(self,logdir,logfile,verbose):
		self.logdir = logdir
		self.logfile = logfile
		self.verbose = verbose
		self.filelogger = logging.getLogger(__name__)
		self.consolelogger = logging.getLogger('console'+__name__)
		
	def setup(self):

		filelogger = self.filelogger
		consolelogger = self.consolelogger
		
		
		log_dir = os.path.join(str(pathlib.Path(__file__).parent.resolve()), f'../{self.logdir}')
		
		if not os.path.isdir(log_dir):
			os.makedirs(log_dir)

		## FILE LOGGING CONFIGURATION
		
		filelogger.setLevel(logging.DEBUG)
		fileformatter = logging.Formatter('%(levelname)s:  %(message)s')
		file_handler = logging.FileHandler( os.path.join(log_dir,self.logfile))
		file_handler.setFormatter(fileformatter)
		filelogger.addHandler(file_handler)

		## CONSOLE LOGGING CONFIGURATION
		
		if self.verbose:
			consolelogger.setLevel(logging.DEBUG)
		else:
			consolelogger.setLevel(logging.INFO)

		consoleformatter = logging.Formatter('%(message)s')
		consoleHandler = logging.StreamHandler()
		consoleHandler.setFormatter(consoleformatter)
		consolelogger.addHandler(consoleHandler)


	def info_log(self,message,color='white'):
		self.consolelogger.info(colored(message,color))
		self.filelogger.info(colored(f'{datetime.datetime.now()} - {message}',color))

	def debug_log(self,message,color):
		self.consolelogger.debug(colored(message,color))
		self.filelogger.debug(colored(f'{datetime.datetime.now()} - {message}',color))

		
	def launch_logs_screen(self,args):
		## launch the logs in new tab if gnome terminal available
		log_cmd  = f"tail -f {os.path.join(str(pathlib.Path(__file__).parent.resolve()),'../logs/logs')}"
		cmd = f'gnome-terminal -e \'bash -c "{log_cmd}; bash"\' --tab 2>&1'

		if not args.detached:
			process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
			process.wait()
			if process.returncode == 0:
				self.info_log("Logs opened in a new terminal",'green')
			else:
				self.info_log(f"Tried opening logs in a new terminal, Failed. Please check if Gnome-terminal installed. You can launch maually by running {colored(log_cmd,'cyan')}",'yellow')
		else:
			self.info_log(f"You can launch logs maually by running {colored(log_cmd,'cyan')}",'green')