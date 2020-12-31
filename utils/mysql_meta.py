import json
import subprocess
import uuid
from pathlib import Path


BASE_DIR = str(Path(__file__).resolve().parent.parent)

def mysql_meta_(host,port,user, password):
    # host = 'localhost'
    # port = '3307'
    # user = 'root'
    # password = ''

    count = 0
    with open(BASE_DIR + '/utils/config.json',"r") as json_file:
        data = json.load(json_file)

    data['host'] = host
    data['port'] = port
    data['user'] = user
    data['password'] = password


    with open(BASE_DIR + '/utils/config.json', "w") as jsonFile:
        json.dump(data, jsonFile)


    try:
        s = subprocess.run("tap-mysql -c config.json --discover > properties.json",shell=True)
    except:
        pass

    with open('properties.json',"r") as json_properties:
        data = json.load(json_properties)    
    return data    