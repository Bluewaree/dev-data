from database.mongodb import MongoDB
from database.mysql import MySQL

def update_mysql():
    mongodb = MongoDB()
    users = mongodb.retrieve_users()
    mysql = MySQL()
    mysql.update_users(users)
