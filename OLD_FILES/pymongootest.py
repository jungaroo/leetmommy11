from pymongo import MongoClient
from secret import MONGO_DB_URI
client = MongoClient(MONGO_DB_URI)
db = client.test
# post = {"author": "Mike",
#          "text": "My first blog post!",
#          "tags": ["mongodb", "python", "pymongo"],         
#          "date": 'asfd'}
# posts = db.posts
# post_id = posts.insert_one(post).inserted_id
# db.list_collection_names()

client = MongoClient(MONGO_DB_URI)

HTML_DB = client.html
# post = {"author": "Mike",
#          "text": "My first blog post!",
#          "tags": ["mongodb", "python", "pymongo"],         
#          "date": 'asfd'}
# posts = HTML_DB.posts
# post_id = posts.insert_one(post).inserted_id
HTML_DB.list_collection_names()

# print(HTML_DB.linkResults.find({},{'HomeTown':1}))