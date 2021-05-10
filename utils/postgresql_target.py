import psycopg2   # import psycopg module
import json
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def test_postgresql_connection(host, port, user, password):
    try:
        con = psycopg2.connect(user=user, password=password, host=host, port=port, dbname='lyftrondata')
        con.close()
        return True
    except Exception as e:
        return False

def create_posgtgresql_db(db_name, connection):
    try:
        cursor = connection.cursor()
        #Preparing query to create a database
        sql = '''CREATE DATABASE {0};'''.format(db_name)
        #Creating a database
        cursor.execute(sql)
        print("Database created successfully........")
        #Closing the connection
        cursor.close()
        return True
    except Exception as e:
        if 'already exists' in str(e):
            return True
        return False


def replicate_to_target( host, port, user, password, structure, staging=None):    
    try:
        # connect to database
        con = psycopg2.connect(user=user, password=password, host=host, port=port, dbname='lyftrondata')
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        print('creating DB...')

        structure = json.loads(structure)
        
        if len(structure['stream_data']) == 0:
            return False
        db_name = structure['stream_data'][0]['tap_stream_id'].split('-')[0]
        if staging:
            db_name = '{}_staging'.format(db_name)
            db_created = create_posgtgresql_db(db_name, con)
        else:
            db_created = create_posgtgresql_db(db_name, con)
        if not db_created:
            return False
        con.close()
        con = psycopg2.connect(user=user, password=password, host=host, port=port, dbname=db_name)
        
        cur = con.cursor()
        table_ = ""

        # with open("playJson.json","r") as json_file:
        #     data = json.load(json_file)

        for t_ in structure['stream_data']:
                # print("")
                # print("-----")
                table_name = t_['table_name']
                table_+="CREATE TABLE IF NOT EXISTS "+table_name+"( "
                # print(t_['table_name'])
                for key_t_m, t_m in t_["metadata"]["properties"].items():
                    # print("-")
                    if 'user' == key_t_m:
                        key_t_m = 'user_'
                    table_+=key_t_m
                    # print(key_t_m)
                    for key_d_, d_ in t_m.items():
                        datatype = d_.lower()
                        if 'enum' in datatype:
                            try:
                                cur.execute('CREATE TYPE {}_enum AS {};'.format(key_t_m, datatype))
                            except Exception as e:
                                if 'already exists' in str(e):
                                    pass
                                return False
                            d_ = '{}_enum'.format(key_t_m)
                        # if 'decimal' in datatype:
                        #     d_ = 'decimal'
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


def replicate_to_staging_and_target(host, port, user, password, structure):    
    try:
        replicate_to_target(host, port, user, password, structure, staging=True)
        replicate_to_target(host, port, user, password, structure)
        return True
    except (Exception, psycopg2.Error) as error :
        return False

