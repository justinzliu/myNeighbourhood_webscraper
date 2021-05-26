import pymongo

DATABASE_NAME = "mydatabase"

client = pymongo.MongoClient("mongodb://localhost:27017/")[DATABASE_NAME]

client.close()