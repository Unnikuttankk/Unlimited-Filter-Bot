import os
import pymongo

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config
 
myclients = pymongo.MongoClient(Config.DATABASE_URI)
mydbs = myclients[Config.DATABASE_NAME]
mycols = mydbs['USERS']



async def add_user(id, username, name, dcid):
    data = {
        '_id': id,
        'username' : username,
        'name' : name,
        'dc_id' : dcid
    }
    try:
        mycols.update_one({'_id': id},  {"$set": data}, upsert=True)
    except:
        pass


async def all_users():
    count = mycols.count()
    return count


async def find_user(id):
    query = mycols.find( {"_id":id})

    try:
        for file in query:
            name = file['name']
            username = file['username']
            dc_id = file['dc_id']
        return name, username, dc_id
    except:
        return None, None, None
