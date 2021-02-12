import json
import psycopg2
import pickle


class Recod():
    __creds = None
    def __init__(self):
        with open('config_target.json',"r") as json_file:
            self.__creds = json.load(json_file)
        # print(self.__creds)
    
    def __connect(self):
        try:
            user = self.__creds.get('user', None)
            password = self.__creds.get('password', None)
            host = self.__creds.get('host', None)
            port = self.__creds.get('port', None)
            database = self.__creds.get('database', None)
            # host = '18.210.27.21'
            # port = '5432'
            # user = 'asim'
            # password = 'DevOpsAtInvozone1982'
            # database = 'poc_demo'
            connection = psycopg2.connect(user=user, password=password, host=host, port=port, database=database)
            return connection
        except Exception as e:
            print(str(e))
    
    def read(self, table_name, where=None, limit=1):
        try:
            query = 'SELECT * FROM {}'.format(table_name)
            if where:
                for column, value in where.items():
                    value = self.__get_str_value(value)
                    query += ' WHERE {}={}'.format(column, value)
            query += ' LIMIT {}'.format(limit)
            connection = self.__connect()
            if not connection:
                return False
            with connection.cursor() as cursor:
                cursor = connection.cursor()
                cursor.execute(query)
                try:
                    field_names = [i[0] for i in cursor.description]
                    count = cursor.fetchall()
                    records = []
                    for record in count:
                        dict_record = {}
                        for key, value in zip(field_names, record):
                            dict_record[key] = value
                        records.append(dict_record)
                    connection.close()
                    data = records
                    with open('results.p', 'wb') as f:
                        pickle.dump(data, f)
                    return data
                except Exception as e:
                    print(e)
                    return False
        except Exception as e:
            print(e)
    
    def __get_str_value(self, value):
        if type(value) == str:
            if value != 'null':
                value = '\'{}\''.format(value)
                return value 
        return value

    def __get_update_query(self, table_name, values, where=None):
        try:
            query = 'UPDATE {} SET'.format(table_name)
            qoma_checked = False
            for column, value in values.items():
                value = self.__get_str_value(value)
                if qoma_checked:
                    query += ','
                query += ' {}={}'.format(column, value)
                qoma_checked = True
            if where:
                for column, value in where.items():
                    value = self.__get_str_value(value)
                    query += ' WHERE {}={}'.format(column, value)
            else:
                query += ' WHERE meta_id=3'
            return query
        except Exception as e:
            print(e)

    def update(self, table_name, values, where=None):
        try:
            query = self.__get_update_query(table_name, values, where)
            if not query:
                return False
            print(query)
            ####
            connection = self.__connect()
            if not connection:
                return False
            with connection.cursor() as cursor:
                cursor = connection.cursor()
                cursor.execute(query)
                try:
                    field_names = [i[0] for i in cursor.description]
                    count = cursor.fetchall()
                except Exception as e:
                    connection.commit()
                    count = cursor.rowcount
                    if count == -1 or count > 0:
                        data = {'data': '{} record(s) has been modified '.format(count)}
                        connection.close()
                        with open('results.p', 'wb') as f:
                            pickle.dump(data, f)
                        return data
        except Exception as e:
            print(e)

    def __get_delete_query(self, table_name, where=None):
        try:
            query = 'DELETE FROM {}'.format(table_name)
            if where:
                for column, value in where.items():
                    value = self.__get_str_value(value)
                    query += ' WHERE {}={}'.format(column, value)
            else:
                query += ' WHERE meta_id=5'
            return query
        except Exception as e:
            print(e)
    
    def delete(self, table_name, where=None):
        try:
            query = self.__get_delete_query(table_name, where)
            if not query:
                return False
            print(query)
            ####
            connection = self.__connect()
            if not connection:
                return False
            with connection.cursor() as cursor:
                cursor = connection.cursor()
                cursor.execute(query)
                try:
                    field_names = [i[0] for i in cursor.description]
                    count = cursor.fetchall()
                except Exception as e:
                    connection.commit()
                    count = cursor.rowcount
                    if count == -1 or count > 0:
                        data = {'data': '{} record(s) has been modified '.format(count)}
                        connection.close()
                        with open('results.p', 'wb') as f:
                            pickle.dump(data, f)
                        return data
        except Exception as e:
            print(e)


    def __get_insert_query(self, table_name, values):
        try:
            if not values:
                return False
            columns = ','.join(values.keys())
            column_values = values.values()
            values_str = ''
            qoma_checked = False
            for value in column_values:
                if qoma_checked:
                    values_str += ','
                str_value = self.__get_str_value(value)
                values_str += '{}'.format(str_value)
                value = self.__get_str_value(value)
                qoma_checked = True
            query = 'INSERT INTO {} ({}) VALUES ({})'.format(table_name, columns, values_str)
            return query
        except Exception as e:
            print(e)
    
    def insert(self, table_name, values):
        try:
            query = self.__get_insert_query(table_name, values)
            if not query: return False
            print(query)
            ####
            connection = self.__connect()
            if not connection:
                return False
            with connection.cursor() as cursor:
                cursor = connection.cursor()
                cursor.execute(query)
                try:
                    field_names = [i[0] for i in cursor.description]
                    count = cursor.fetchall()
                except Exception as e:
                    connection.commit()
                    count = cursor.rowcount
                    if count == -1 or count > 0:
                        data = {'data': '{} record(s) has been modified '.format(1 if count == -1 else count)}
                        connection.close()
                        with open('results.p', 'wb') as f:
                            pickle.dump(data, f)
                        return data
        except Exception as e:
            print(e)





# if __name__ == '__main__':
#     record = Recod()
    # rows = record.read('wp_commentmeta', where={'meta_id': 6}, limit=10)
    # rows = record.read('wp_commentmeta', limit=10)
    # for row in rows:
    #     print(row)
    # record_status = record.update(
    #     'wp_commentmeta', {'meta_key': 'testing', 'meta_value': 1123123},
    #     where={'meta_id': 4}
    # )
    # delete_status = record.delete('wp_commentmeta', where={'meta_id': 3})

    # print(delete_status)
