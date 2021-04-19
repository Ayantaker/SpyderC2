import os
import requests

## Getting list of files in current directory
files = [f for f in os.listdir('.') if os.path.isfile(f)]

## Sending out data
url = 'http://localhost:8080'
params = {}
r = requests.post(url = url, params = params, json={"name": files})

