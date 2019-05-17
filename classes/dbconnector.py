"""Connector to the MongoDB database """
from pymongo import MongoClient, DESCENDING
from pymongo.errors import DuplicateKeyError

from flask import jsonify

class DBConnector:

    def __init__(self, MONGO_DB_URI, db_name):
        self.db = MongoClient(MONGO_DB_URI)[db_name]
        
    def addToCollection(self, collection_name, record):
        """Adds a collection to the mongoDB database """
        collection = self.db[collection_name]
        collection.create_index([("cohort", DESCENDING), ("search", DESCENDING)], unique=True) 

        return collection.insert_one(record).inserted_id

    def isRecordInCollection(self, collection_name, searchDic):
        """Returns the record in collection (dict) if it exists, else returns false. """
        try:
            return self._lookupRecordInCollection(collection_name, searchDic) 
        except IndexError:
            return False

    def listCollections(self):
        """Returns a list of the collection names """
        return self.db.list_collection_names()
    
    def _lookupRecordInCollection(self, collection_name, searchDic):
        """Returns the record in the collection """
        return self.db[collection_name].find(searchDic)[0]

    def updateToCollection(self, collection_name, query, newResultArr):
        collection = self.db[collection_name]

        newvalues = { "$set": { "result": newResultArr} }
        return collection.update_one(query, newvalues)


if __name__ == "__main__":
    print("Testing...")
    import sys
    sys.path.append("..")
    from secret import MONGO_DB_URI

    dbC = DBConnector(MONGO_DB_URI,'leetmommy')

    code_snip1 = {"cohort": "r10",
            "search": "flask",
            "result": ["www.google.com", "www.facebook.com", "www.blah.com"]}
    # print(dbC.addToCollection('code_snips', code_snip1))
    print(dbC.isRecordInCollection('code_snips',{'cohort':'r11','search':'flask'}))

