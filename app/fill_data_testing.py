import pymongo
import os

client = pymongo.MongoClient(os.environ["MONGODB_TEST_URI"])
db = client['main']
document = db.database


def insert_entry(DICT):
    document.insert_one(DICT)


if __name__ == "main":
    insert_entry({})
