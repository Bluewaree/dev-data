from pymongo import MongoClient
from bson import BSON, decode_all
import sys
from configparser import ConfigParser

sys.path.append('..')
import constants.constants as const

config = ConfigParser()
config.read('config.ini')

DATABASE_URL = f"mongodb://{config['mongodb']['host']}:{config['mongodb']['port']}/"
DATABASE_NAME = config['mongodb']['name']

class MongoDB(object):

    def __init__(self, db_name = DATABASE_NAME):
        self._db_connection = MongoClient(DATABASE_URL)
        self._db = self._db_connection.get_database(db_name)
    
    def restoreDB(self,bson_file,collection):
        collection = self._db[collection] 
        with open(bson_file, 'rb') as f:
            collection.insert(decode_all(f.read()))