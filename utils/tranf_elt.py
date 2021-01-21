import psycopg2   # import psycopg module
import json


def _do_transformation(host, port, user, password, query):

    # Sql_vari = "Select * from wp_users"

    try:
        # connect to database
        connection = psycopg2.connect(user = user,
                                    password = password,
                                    host = host,
                                    port = port,
                                    database = "Postgres_")
        with connection.cursor() as cursor:
            cursor = connection.cursor()
            cursor.execute(query)
            try:
                count = cursor.fetchall()
                connection.close()
                data = {'data': count}
                return data
            except:
                connection.commit()
                count = cursor.rowcount
                if (count == -1):
                    data = {'data': 'Command executed successfully'}
                    connection.close()
                    return data
        # print(type(cursor))
    except (Exception, psycopg2.Error) as error :
        if(connection):
            data = {'error': str(error)}
            connection.close()
            return data
    finally:
        #closing database connection.
        if(connection):
            connection.close()
            print("PostgreSQL connection is closed")