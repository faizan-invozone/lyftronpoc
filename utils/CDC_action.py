#!/usr/bin/env python3

import psycopg2   
import json
import subprocess
import re
from pathlib import Path
from utils.CDC_elt import MYSQL_SETTINGS
import requests
from ast import literal_eval

BASE_DIR = str(Path(__file__).resolve().parent.parent)

def type_Check(st):
    if type(st) == str:
        st = st.replace("\n","").strip()
        if st.isnumeric():
            pass
        else:
            st= "'" + st +"'"
    return st
    
def type_map(value):
    table = ""
    tab = ""
    value_ = value.split()
    for d_ in value_:
        datatype = d_.lower()
        if 'bigint' in datatype:
            d_ = 'bigint'
        if 'tinyint' in datatype:
            d_ = 'smallint'
        if 'mediumint' in datatype:
            d_ = 'integer'
        if 'double' in datatype:
            d_ = 'DOUBLE PRECISION'
        if 'float' in datatype:
            d_ = 'REAL'
        if 'longtext' in datatype:
            d_ = 'TEXT'
        if 'mediumtext' in datatype:
            d_ = 'TEXT'
        if 'tinytext' in datatype:
            d_ = 'TEXT'
        if 'blob' in datatype:
            d_ = 'BYTEA'
        if 'datetime' in datatype:
            d_ = 'timestamp'
        if 'int(' in datatype:
            d_ = 'int'
        if 'unsigned' in datatype:
            d_ = ''   
        table +=" "+d_     
    table_ = table.split(",")
    for t_ in table_:
        if 'AUTO_INCREMENT' in t_:
            if 'int' in t_:
                t_ = t_.replace('int','')
                t_ = t_.replace("AUTO_INCREMENT", "SERIAL")
        tab += ","+t_     
    tab = tab[1::] 
    tab = tab.strip()        
    return tab

def get_job_actions(table_name):
    file_name = 'config_source.json'
    new_table_name = table_name.replace('\n', '')
    with open(file_name,"r") as json_file:
        data = json.load(json_file)
        integration_id = data.get('integration_id', None)
        if integration_id:
            data = {'integration': integration_id, 'table_name': new_table_name}
            res = requests.post('http://localhost:8000/api/v1/integration-actions', data=data)
            res_data = json.loads(res.text)
            return res_data
    return False

def apply_cdc(host, port, user, password, database, etl=None):
    try:
        # connect to database
        db_name = ''
        if etl:
            db_name = '{}_staging'.format(database)
        else:
            db_name = database
        connection = psycopg2.connect(user = user,
                                    password = password,
                                    host = host,
                                    port = port,
                                    database = db_name)

        cursor = connection.cursor()
        print('MySQL settings are:')
        print(MYSQL_SETTINGS)
        print('data base connected with these credentials host:{}, port:{}, user:{}, password:{}, database:{}'.format(
            host, port, user, password, database
        ))
        print("d")
        file_path = '{}/utils/CDC_elt.py'.format(BASE_DIR)
        proc = subprocess.Popen('python3 {}'.format(file_path),
                        shell=True,
                        stdout=subprocess.PIPE,
                        )
        print(file_path)
        Query = False
        Update = False
        Write = False
        Delete = False


        inside_Query = False
        inside_Update = False
        inside_Write = False
        inside_Delete = False

        Default = False
        data_post_en = False

        print("start")
        checked = False
        while proc.poll() is None:
            output = proc.stdout.readline()
            data = output.decode("utf-8")
            if data != "":
                if '==' in data: 
                    query_data_key_value = ""
                    Update_q_key = []
                    Update_q_value = []
                    Write_q_key = ""
                    Write_q_value = ""
                    Delete_q_key = []
                    Delete_q_value = []
                    update_count = 0 
                    update_final_string = ""

                    Default = True
                    Query = False
                    Update = False
                    Write = False
                    Delete = False

                    inside_Query = False
                    inside_Update = False
                    inside_Write = False
                    inside_Delete = False 

                if "QueryEvent" in data:
                    print("---- Query ----")
                    Query = True
                elif "UpdateRowsEvent" in data:
                    print("---- Update ----")
                    Update = True
                elif "WriteRowsEvent" in data:
                    print("---- Write ----")
                    Write = True
                elif "DeleteRowsEvent" in data:
                    print("---- Delete ----")
                    Delete = True

                if Default == True and Query == True:  
                    if "FLUSH" in data:
                        pass
                    elif "Schema" in data:
                        schema_data = data.replace("Schema: b","").replace("'","")
                        print(schema_data)
                    elif "Query" in data and "BEGIN" not in data and "==" not in data:
                        query_data_key_value += data.replace("Query: ","").strip()
                        print(query_data_key_value)
                        inside_Query = True
                        data_post_en = True
                    elif data_post_en == True:
                        print("n")
                        
                        query_data_key_value += data.strip()
                        query_data_key_value = re.sub('`', '', query_data_key_value)
                        query_data_key_value = type_map(query_data_key_value)
                        print(query_data_key_value)
                        cursor.execute(query_data_key_value)
                        connection.commit()
                        data_post_en = False
                        
                elif Default == True and Update == True:
                    if "Table" in data:
                        Update_data = data.replace("Table: ","")
                        Update_data_t = Update_data.split(".")
                        print(Update_data_t[1])
                    elif "*" in data:
                        Update_data = data.replace("*","")
                        Update_data = Update_data.split(":")
                        Update_data_value = Update_data[1].split("=>")
                        print(Update_data)
                        print(Update_data_value)
                        type_update = type_Check(Update_data_value[1])
                        if Update_data_value[0] != Update_data_value[1].replace("\n",""):
                            update_count += 1
                            update_final_string += Update_data[0] +"="+type_update +","
                        
                        Update_q_key.append(Update_data[0]) 
                        Update_q_value.append(type_update)
                        data_post_en = True
                    elif data_post_en == True:
                        print(update_final_string)
                        
                        update_final_string = update_final_string[:-1]
                        U_DATA = "Update "+ Update_data_t[1] +" set "+update_final_string +" where "+ Update_q_key[0]+" ="+Update_q_value[0]
                        U_DATA = U_DATA.replace("\n","")
                        print(U_DATA)
                        cursor.execute(U_DATA)
                        connection.commit()
                        data_post_en = False
                        # job_actions = get_job_actions(Update_data_t[1])
                        # jobs = job_actions.get('data', None)
                        # for job in jobs:
                        #     query = job.get('job_action', None)
                        #     if Update_data_t[1] in query:
                        #         if Update_data[1] in query:

                        #             #will go to the stage with the id and table name..
                        #             #have to call the transformation code with the given query and get the data with given id then dump it into target
                        # cursor.execute()
                        # if job_actions:
                        #     print(job_actions)

                elif Default == True and Write == True:
                    if "Table" in data:
                        Write_data = data.replace("Table: ","")
                        Write_data_t = Write_data.split(".")
                        print(Write_data_t[1])
                    elif "*" in data:
                        Write_data = data.replace("*","")
                        Write_data = Write_data.split(":")
                        print(Write_data)   
                        print(type(Write_data[1])) 
                        type_write = type_Check(Write_data[1])
                        Write_q_key += ","+ Write_data[0] 
                        Write_q_value += ","+ type_write
                        data_post_en = True
                    elif data_post_en == True:
                        job_actions = get_job_actions(Write_data_t[1])
                        if job_actions:
                            print(job_actions)
                        Write_q_key = Write_q_key[1::].replace("\n","")
                        Write_q_value = Write_q_value[1::].replace("\n","")
                        W_DATA = "INSERT INTO " +Write_data_t[1]+ " (" + Write_q_key + ") VALUES ("+Write_q_value+");"
                        W_DATA = W_DATA.replace("\n","")
                        print(W_DATA)
                        cursor.execute(W_DATA)
                        connection.commit()
                        data_post_en = False
                        
                elif Default == True and Delete == True:
                    # DELETE FROM MyGuests WHERE id = 1
                    if "Table" in data:
                        Delete_data = data.replace("Table: ","")
                        Delete_data_t = Delete_data.split(".")
                        print(Delete_data_t[1])
                    elif "*" in data:
                        Delete_data = data.replace("*","")
                        Delete_data = Delete_data.split(":")
                        print(Delete_data)
                        Delete_q_key.append(Delete_data[0]) 
                        Delete_q_value.append(Delete_data[1])
                        data_post_en = True
                    elif data_post_en == True:
                        D_DATA = "DELETE FROM "+ Delete_data_t[1] +" WHERE "+Delete_q_key[0]+" = "+Delete_q_value[0]
                        print(D_DATA)
                        cursor.execute(D_DATA)
                        connection.commit()
                        data_post_en = False
        checked = False

    
    except (Exception, psycopg2.Error) as error :
        if(connection):
            print(error)

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
