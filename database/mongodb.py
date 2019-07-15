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
        self._db_connection = ""
        self._db = ""

    def connect(self):
        db_url = f"mongodb://{self._db_host}:{self._db_port}/"
        self._db_connection = MongoClient(db_url)       
        self._db = self._db_connection[self._db_name]
    
    def restore_db(self,bson_file,collection):
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
                {"$group":{"_id":"$login","count":{"$sum":1},"data": { "$addToSet": "$$ROOT" }}},
                { "$unwind": "$data" },
                { "$project": {
                    "_id": 0,
                    "data": 1,
                    "count":1,
                    "isDuplicate": {"$gte": ["$count",2]},
                    "isNewest": {"$eq":["updated_at",{"$max":"updated_at"}]}
                }},
                { "$match": { "isDuplicate": True,"isNewest":True }}
        ]
        users = list(self._db.github_users.aggregate(pipeline, allowDiskUse=True))
        pipeline = [
                {"$group":{"_id":"$login","count":{"$sum":1},"data": { "$addToSet": "$$ROOT" }}},
                { "$unwind": "$data" },
                { "$project": {
                    "_id": 0,
                    "data": 1,
                    "count":1,
                    "isDuplicate": {"$lt": ["$count",2]},
                    "isNewest": {"$eq":["updated_at",{"$max":"updated_at"}]}
                }},
                { "$match": { "isDuplicate": True,"isNewest":True }}
        ]
        users += list(self._db.github_users.aggregate(pipeline, allowDiskUse=True))
        return users
    
    def drop_database(self):
        self._db_connection.drop_database(self._db_name)
    
    def remove_duplicates(self):
        pipeline = [
                {"$group":{"_id":"$login","count":{"$sum":1},"dups": {"$addToSet": "$_id"}}},
                { "$project": {
                    "_id": 0,
                    "updated_at":1,
                    "count":1,
                    "dups": 1,
                    "isDuplicate": {"$gt": ["$count",1]}
                }},
                { "$match": { "isDuplicate": True }},
                { "$sort": {"updated_at":-1} }
        ]
        users = list(self._db.github_users.aggregate(pipeline, allowDiskUse=True))
        to_remove = []
        for user in users:
            dups = user['dups']
            dups.pop(0)
            to_remove += dups
        self._db.github_users.remove({"_id":{"$in":to_remove}})
    
    def remove_documents_with_null_values(self):
        query = {"name": { "$in": [ None, "" ] },"email": { "$in": [ None, "" ] }}
        self._db.github_users.delete_many(query)
    
    def export_users_schema(self,export_destination,collection):
        host = f'{self._db_host}:{self._db_port}'
        try:
            command = ['mongoexport',
                '--host',
                host,
                '--db',
                self._db_name,
                '--collection',
                collection,
                '--type=csv',
                '--out',
                export_destination,
                '--fields',
                'login,name,email',
                '--forceTableScan'
            ]
            subprocess.check_output(command)
        except subprocess.CalledProcessError as error:
            raise error
        

    def disconnect(self):
        self._db_connection.close()
        
