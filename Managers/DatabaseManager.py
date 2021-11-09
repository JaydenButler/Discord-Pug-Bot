import os
import pymongo
import certifi

CLIENT = pymongo.MongoClient(os.environ.get("MONGO_URL"), tlsCAFile=certifi.where())

DATABASE = CLIENT["6mans"]
RECORDS = DATABASE["Servers"]

def update_record(id, method, key, value):
    RECORDS.update_one({"_id": id}, {method: {key: value}})

def find_record(id):
    return RECORDS.find_one({"_id": id})

def insert_record(data):
    RECORDS.insert_one(data)