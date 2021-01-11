import psycopg2   # import psycopg module
import json


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

def insert_data_into_target(host, port, user, password):
    ar_ = []
    with open("database.json","r") as json_file:
            for d_ in json_file:
                if '{"type": "RECORD",'in d_:
                    # ar_.append("'"+d_+"'")
                    ar_.append(d_)
    # print(ar_)                
    with open('data_properties.json', "r") as jsonFile:
        file_data = json.load(jsonFile)
        database = file_data['streams'][0]['tap_stream_id'].split('-')[0]

    try:
        # connect to database
        connection = psycopg2.connect(user = user,
                                    password = password,
                                    host = host,
                                    port = port,
                                    database = database)

        cursor = connection.cursor()

    


        for a in ar_:
            # print(a)
            data = json.loads(a)
            table_data = []
            table_column_data = []
            table_name = data['stream']
            print(table_name)
            for ad_k , ad_data in data['record'].items():
                print(ad_k, ad_data)
                table_column_data.append(ad_k)
                table_data.append(ad_data)
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
            q_ = "INSERT INTO " +table_name+ " (" +final_C_D+ ") VALUES ("+number_s+")"
            print(q_)
            final_T_D = tuple(final_T_D)
            print(final_T_D)

            cursor.execute(q_, final_T_D)

            connection.commit()
            count = cursor.rowcount
            print (count, "Record inserted successfully into mobile table")
            return True
            # print("--")
    except (Exception, psycopg2.Error) as error :
        if(connection):
            print("Failed to insert record into mobile table", error)
        return False

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
