import psycopg2   # import psycopg module
import json

def replicate_to_target(host, port, user, password, structure):    
    try:
        # connect to database
        con = psycopg2.connect(user = user,
                                    password = password,
                                    host = host,
                                    port = port,
                                    database = 'abc')
        cur = con.cursor()
        table_ = ""

        # with open("playJson.json","r") as json_file:
        #     data = json.load(json_file)

        for t_ in structure:
                # print("")
                # print("-----")
                table_+="CREATE TABLE IF NOT EXISTS "+t_['table_name']+"( "
                # print(t_['table_name'])
                for key_t_m, t_m in t_["metadata"]["properties"].items():
                    # print("-")
                    table_+=key_t_m
                    # print(key_t_m)
                    for key_d_, d_ in t_m.items():
                        table_+=" "+d_
                        # print(d_)
                    table_+=","
                table_+=" );"
                table_ = table_.replace(", );"," );")
                print(table_)        

                cur.execute(table_)
                    
                con.commit()
                
                print("Table created successfully") 
                table_ = ""
        return True
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
        return False
    finally:
        #closing database connection.
                if(con):
                    cur.close()
                    con.close()
                    print("PostgreSQL connection is closed")
