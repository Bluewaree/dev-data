from pymongo import MongoClient
import sys
from configparser import ConfigParser
import subprocess

sys.path.append('..')
import constants.constants as const

config = ConfigParser()
config.read('config.ini')

DB_HOST = config['mongodb']['host']
DB_PORT = config['mongodb']['port']
DB_NAME = config['mongodb']['name']

class MongoDB(object):

    def __init__(self, db_host = DB_HOST, db_port = DB_PORT, db_name = DB_NAME):
        self._db_host = db_host
        self._db_port = db_port
        self._db_name = db_name

    def connect(self):
        db_url = f"mongodb://{self._db.host}:{self._db.port}/"
        self._db_connection = MongoClient(db_url)
        self._db = self._db_connection.get_database(db_name)

    def restoreDB(self,bson_file,collection):
        host = f'{self._db_host}:{self._db_port}'
        try:
            command = ['mongorestore',
                '-h',
                host,
                '--db',
                self._db_name,
                '--collection',
                collection,
                bson_file
            ]
            subprocess.check_output(command)
        except subprocess.CalledProcessError as error:
            raise error
    def retrieve_users(self):
        pipeline = [
                {$group:{_id:"$login",count:{$sum:1},"data": { "$addToSet": "$$ROOT" }}},
                { "$unwind": "$data" },
                { "$project": {
                    "_id": 0,
                    "data": 1,
                    "count":1,
                    "isDuplicate": {"$gte": ["$count":2]},
                    "isNewest": {"$eq":["updated_at",{"$max":"updated_at"}]}
                }},
                { "$match": { "isNewest":true }}
        ]
        users = self._db.users.aggregate(pipeline, allowDiskUse=True)
        pipeline = [
                {$group:{_id:"$login",count:{$sum:1},"data": { "$addToSet": "$$ROOT" }}},
                { "$unwind": "$data" },
                { "$project": {
                    "_id": 0,
                    "data": 1,
                    "count":1,
                    "isDuplicate": {"$lt": ["$count":2]},
                    "isNewest": {"$eq":["updated_at",{"$max":"updated_at"}]}
                }},
                { "$match": { "isNewest":true }}
        ]
        users += self._db.users.aggregate(pipeline, allowDiskUse=True)
        return users
