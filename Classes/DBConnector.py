from pymongo import MongoClient, DESCENDING
from pymongo.errors import DuplicateKeyError
from secret import MONGO_DB_URI

from flask import jsonify
class DBConnector():

    def __init__(self, MONGO_DB_URI, db_name):
        self.db = MongoClient(MONGO_DB_URI)[db_name]
        
    def addToCollection(self, collection_name, record):
        collection = self.db[collection_name]
        collection.create_index([("cohort", DESCENDING),("search", DESCENDING)], unique=True) 


        return collection.insert_one(record).inserted_id

    def isRecordInCollection(self,collection_name,searchDic):
        try:
            return self._lookupRecordInCollection(collection_name,searchDic) 
        except IndexError:
            return False

    def listCollections(self):
        return self.db.list_collection_names()
    
    def _lookupRecordInCollection(self, collection_name, searchDic):
        return self.db[collection_name].find(searchDic)[0]


# dbC = DBConnector(MONGO_DB_URI,'leetmommy')

# code_snip1 = {"cohort": "r10",
#           "search": "flask",
#           "result": ["www.google.com", "www.facebook.com", "www.blah.com"]}
# # print(dbC.addToCollection('code_snips', code_snip1))
# print(dbC.isRecordInCollection('code_snips',{'cohort':'r11','search':'flask'}))

