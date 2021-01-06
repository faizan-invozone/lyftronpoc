import json
import subprocess
import uuid
from pathlib import Path


BASE_DIR = str(Path(__file__).resolve().parent.parent)

def test_mysql_connection(host, port, user, password):
    with open('config.json',"r") as json_file:
        data = json.load(json_file)
    data['host'] = host
    data['port'] = port
    data['user'] = user
    data['password'] = password
    with open('config.json', "w") as jsonFile:
        json.dump(data, jsonFile)
    try:
        proc = subprocess.Popen("tap-mysql -c config.json",shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        print(stderr.decode("utf-8"))
        str_status = stderr.decode("utf-8").lower()
        if 'error' in str_status:
            return False
        if "Access denied" in stderr.decode("utf-8"):
            return False
        else:
            return True
    except:
        return False

def mysql_meta_(host,port,user, password):
    with open('config.json',"r") as json_file:
        data = json.load(json_file)

    data['host'] = host
    data['port'] = port
    data['user'] = user
    data['password'] = password


    with open('config.json', "w") as jsonFile:
        json.dump(data, jsonFile)

    try:
        proc = subprocess.Popen("tap-mysql -c config.json",shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        print(stderr.decode("utf-8"))
        if "Access denied" in stderr.decode("utf-8"):
            return False
        else:
            try:
                s = subprocess.run("tap-mysql -c config.json --discover > properties.json",shell=True)
            except:
                pass
            with open('properties.json',"r") as json_properties:
                data = json.load(json_properties)    
            return data  
    except:
        return False