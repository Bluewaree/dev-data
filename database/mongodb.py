from pymongo import MongoClient
from bson import BSON, decode_all
import sys
from configparser import ConfigParser

sys.path.append('..')
import constants.constants as const

config = ConfigParser()
config.read('config.ini')

DB_HOST = config['mongodb']['host']
DB_PORT = config['mongodb']['port']
DB_NAME = config['mongodb']['name']

class MongoDB(object):

    def __init__(self, db_host = DB_HOST, db_port = DB_PORT):
        self._db_host = db_host
        self._db_port = db_port

    def connect(self, db_name = DB_NAME):
        db_url = f"mongodb://{self._db.host}:{self._db.port}/"
        self._db_connection = MongoClient(db_url)
        self._db = self._db_connection.get_database(db_name)
    
    def restoreDB(self,bson_file,collection):
        collection = self._db[collection] 
        with open(bson_file, 'rb') as f:
            collection.insert(decode_all(f.read()))