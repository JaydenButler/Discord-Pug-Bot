import os
import pymongo
import certifi
from dotenv import load_dotenv

load_dotenv(".env")

CLIENT = pymongo.MongoClient(os.environ.get("MONGO_URL"), tlsCAFile=certifi.where())

DATABASE = CLIENT["6mans"]
RECORDS = DATABASE["Servers"]

def update_record(id, method, key, value):
    RECORDS.update_one({"_id": id}, {method: {key: value}})

def report_existing_match(id, value):
    index = int(value["matchNum"] - 1)
    RECORDS.update_one({"_id": id}, {"$set": {f"matches.{index}.winner": value["winner"]}})
    RECORDS.update_one({"_id": id}, {"$set": {f"matches.{index}.reported": value["reported"]}})
    RECORDS.update_one({"_id": id}, {"$set": {f"matches.{index}.reportedBy": value["reportedBy"]}})

def find_record(id):
    return RECORDS.find_one({"_id": id})

def delete_record(id):
    return RECORDS.delete_one({"_id": id})

def insert_record(data):
    RECORDS.insert_one(data)