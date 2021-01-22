import json
import subprocess
import uuid
from pathlib import Path
import os
from datetime import datetime




BASE_DIR = str(Path(__file__).resolve().parent.parent)

def fetch_data_from_mysql(host,port,user, password):
    start_insertion_time = datetime.now()
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
                file_name = 'database.json'
                if os.path.isfile(file_name):
                    os.remove(file_name)
                with open(file_name, 'w+') as json_file:
                    pass
                s = subprocess.run("tap-mysql -c config.json --properties data_properties.json >>database.json",shell=True)
                print(datetime.now() - start_insertion_time)
            except:
                pass
    except Exception as e:
        return False