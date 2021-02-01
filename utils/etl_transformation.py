import psycopg2
import pandas as pd
import sys
import numpy as np
from sqlalchemy import create_engine
from copy import deepcopy
import psycopg2.extras

# Connection parameters, yours will be different

def connect_staging(params_dic):
    """ Connect to the PostgreSQL database server """
    conn = None
    connection_dict = deepcopy(params_dic)

    connection_dict['database'] = '{}_staging'.format(connection_dict['database'])
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**connection_dict)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1) 
    print("Connection successful")
    return conn

def postgresql_to_dataframe(conn, select_query, column_names):
    """
    Tranform a SELECT query into a pandas dataframe
    """
    cursor = conn.cursor()
    try:
        cursor.execute(select_query)
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        cursor.close()
        return 1
    
    # Naturally we get a list of tupples
    tupples = cursor.fetchall()
    cursor.close()
    
    # We just need to turn it into a pandas dataframe
    df = pd.DataFrame(tupples, columns=column_names)
    return df 


def postgresql_to_dataframe_column(conn, select_query):
    """
    Tranform a SELECT query into a pandas dataframe
    """
    cursor = conn.cursor()
    try:
        cursor.execute(select_query)
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        cursor.close()
        return 1
    
    # Naturally we get a list of tupples
    
    # We just need to turn it into a pandas dataframe
    return cursor 

    
           



def connect_target(param_dic_target):
    """ Connect to the PostgreSQL database server """
    conn_t = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn_t = psycopg2.connect(**param_dic_target)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1) 
    print("Connection successful")
    return conn_t

def insert_into_target_etl(connection_param, query):
    # Connect to the database
    # query = "Select id,name , number+1 as number from test"
    print(query)
    conn = connect_staging(connection_param)
    field_names = postgresql_to_dataframe_column(conn,query)
    column_names = [i[0] for i in field_names.description]
    print(column_names)

    table_q = """SELECT
            TABLE_NAME
        FROM
            INFORMATION_SCHEMA.COLUMNS
        """

    print(postgresql_to_dataframe_column(conn,table_q))
    # first we have to run the query to find the column then we have to run it in panda
    df = postgresql_to_dataframe(conn, query, column_names)
    list_df = df
    # print(list_df)
    # list_data = []

    table_name = query.split(" ")[-1:]
    table_name = ''.join(x for x in table_name)
    list_data = []

    for index, row in df.iterrows():
        # print(row['meta_id'], row['comment_id'])
        tuple_str = []
        for i in column_names:
            # print(row[i])
            tuple_str.append(row[i])

        # tuple_str = tuple_str[:-1]    
        list_data.append(tuple(tuple_str))
    print(list_data)
    
    conn_t = connect_target(connection_param)
    cursor = conn_t.cursor()

    column_value = ','.join(x for x in column_names)
    number_s = "%s,"*len(column_names)
    number_s = number_s[:-1]
    print(number_s)
    print(column_value)
    print(table_name)
    q_ = "INSERT INTO " +table_name+ " (" +column_value+ ") VALUES ("+number_s+")"
    
    # cursor.executemany(q_, list_data)
    psycopg2.extras.execute_batch(cursor, q_, list_data)
    conn_t.commit()
    count = cursor.rowcount
    print (count, "Record inserted successfully into "+table_name+" table")
    conn_t.close()
    conn.close()