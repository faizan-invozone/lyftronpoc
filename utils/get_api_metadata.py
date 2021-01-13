import json
import psycopg2
from random import seed
from random import random

def table_data_arranged(arg):
    new_arg = []
    for arg_ in arg:
        if isinstance(arg_,int):
            arg_new = arg_
            new_arg.append(arg_new)
        elif arg_.isnumeric():
            arg_new = int(arg_)
            new_arg.append(arg_new)
        else:
            new_arg.append(arg_)
    return new_arg

def load_data_into_target_db(host, port, user, password, api_data):
    with open("meta_data_db.json","r") as json_file:
        data = json.load(json_file)
    try:
        # connect to database
        con = psycopg2.connect(user = user,
                                    password = password,
                                    host = host,
                                    port = port,
                                    database = "api")
        cur = con.cursor()
        table_ = ""
        seed(1)
        
        
        # print(data)
        get_meta = False
        for t_ in api_data:
            # print(t_)
            if not get_meta:
                
                for d_ in data['stream_data']:
                    d_['tap_stream_id'] = "api-api_as_source"
                    title_ = "api_as_source_"+str(random())
                    title_ = title_.replace(".","")
                    d_['table_name'] = title_


                    for t_key, t in t_.items():
                        print(t_key,t)
                        if isinstance(t,int):
                            d_["metadata"]["properties"].update({""+t_key +"": {"Type": "int","Default":"NULL"}})
                        elif t.isnumeric():
                            d_["metadata"]["properties"].update({""+t_key +"": {"Type": "int","Default":"NULL"}})
                        else:
                            d_["metadata"]["properties"].update({""+t_key +"": {"Type": "TEXT","Default":"NULL"}})
                
                
                table_+="CREATE TABLE IF NOT EXISTS "+d_['table_name']+"( "
                # print(t_['table_name'])
                for key_t_m, t_m in d_["metadata"]["properties"].items():
                    # print("-")
                    table_+=key_t_m
                    # print(key_t_m)
                    for key_d_, d__ in t_m.items():
                        table_+=" "+d__
                        # print(d_)
                    table_+=","
                table_+=" );"
                table_ = table_.replace(", );"," );")
                print(table_)        

                cur.execute(table_)
                    
                con.commit()
                
                print("Table created successfully") 
                table_ = ""
                get_meta = True

        
    
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
        return False
    


    try:
        
        for a in api_data:
            # print(a)
            
            table_data = []
            table_column_data = []
            table_name = title_
            print(table_name)
            for t_key, t in a.items():
                table_column_data.append(t_key)
                table_data.append(t)
            print(table_column_data)
            print(len(table_column_data))
            len_table_C_D = len(table_column_data)
            final_C_D = ' '.join([str(elem+",") for elem in table_column_data]) 
            final_C_D = final_C_D[:-1]
            print(table_data)
            final_T_D = table_data_arranged(table_data)
            # print("--")
            number_s = "%s,"*len_table_C_D
            number_s = number_s[:-1]
            q_ = "INSERT INTO " +title_+ " (" +final_C_D+ ") VALUES ("+number_s+")"
            print(q_)
            final_T_D = tuple(final_T_D)
            print(final_T_D)

            cur.execute(q_, final_T_D)

            con.commit()
            count = cur.rowcount
            print (count, "Record inserted successfully into mobile table")

            # print("--")

    
        cur.close()
        con.close()
        print("PostgreSQL connection is closed")
        return True
    except (Exception, psycopg2.Error) as error :
        if(con):
            print("Failed to insert record into mobile table: ", error)
            cur.close()
            con.close()
        return False


    finally:
        #closing database connection.
        if(con):
            cur.close()
            con.close()
            print("PostgreSQL connection is closed")
            return True
