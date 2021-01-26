#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import (
    DeleteRowsEvent,
    UpdateRowsEvent,
    WriteRowsEvent,
    RowsEvent,
    TableMapEvent,
)

data = None
with open('config_source.json',"r") as json_file:
        data = json.load(json_file)

MYSQL_SETTINGS = {
    'host': data['host'], 'port': int(data['port']),
    'user': data['user'], 'passwd': data['password']
}


def main():
    stream = BinLogStreamReader(
        connection_settings=MYSQL_SETTINGS,
        server_id=3,
        blocking=True,resume_stream=True)

    # print(stream)

    dd = []
    for binlogevent in stream:
        binlogevent.dump()  
        sys.stdout.flush()    
            

    stream.close()

if __name__ == "__main__":
    main()


