import os
import pymongo

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config
 
myclients = pymongo.MongoClient(Config.DATABASE_URI)
mydbs = myclients[Config.DATABASE_NAME]
mycols = mydbs['CONNECTION']   


async def add_connection(group_id, user_id):
    querye = mycols.find_one(
        { "_id": user_id },
        { "_id": 0, "active_group": 0 }
    )
    if querye is not None:
        group_ids = []
        for x in querye["group_details"]:
            group_ids.append(x["group_id"])

        if group_id in group_ids:
            return False

    group_details = {
        "group_id" : group_id
    }

    data = {
        '_id': user_id,
        'group_details' : [group_details],
        'active_group' : group_id,
    }
    
    if mycols.count_documents( {"_id": user_id} ) == 0:
        try:
            mycols.insert_one(data)
            return True
        except:
            print('Some error occured!')

    else:
        try:
            mycolss.update_one(
                {'_id': user_id},
                {
                    "$push": {"group_details": group_details},
                    "$set": {"active_group" : group_id}
                }
            )
            return True
        except:
            print('Some error occured!')

        
async def active_connection(user_id):

    querye = mycols.find_one(
        { "_id": user_id },
        { "_id": 0, "group_details": 0 }
    )
    if querye:
        group_id = querye['active_group']
        if group_id != None:
            return int(group_id)
        else:
            return None
    else:
        return None


async def all_connections(user_id):
    querye = mycols.find_one(
        { "_id": user_id },
        { "_id": 0, "active_group": 0 }
    )
    if querye is not None:
        group_ids = []
        for x in querye["group_details"]:
            group_ids.append(x["group_id"])
        return group_ids
    else:
        return None


async def if_active(user_id, group_id):
    querye = mycols.find_one(
        { "_id": user_id },
        { "_id": 0, "group_details": 0 }
    )
    if querye is not None:
        if querye['active_group'] == group_id:
            return True
        else:
            return False
    else:
        return False


async def make_active(user_id, group_id):
    update = mycols.update_one(
        {'_id': user_id},
        {"$set": {"active_group" : group_id}}
    )
    if update.modified_count == 0:
        return False
    else:
        return True


async def make_inactive(user_id):
    update = mycols.update_one(
        {'_id': user_id},
        {"$set": {"active_group" : None}}
    )
    if update.modified_count == 0:
        return False
    else:
        return True


async def delete_connection(user_id, group_id):

    try:
        update = mycols.update_one(
            {"_id": user_id},
            {"$pull" : { "group_details" : {"group_id":group_id} } }
        )
        if update.modified_count == 0:
            return False
        else:
            querye = mycols.find_one(
                { "_id": user_id },
                { "_id": 0 }
            )
            if len(querye["group_details"]) >= 1:
                if querye['active_group'] == group_id:
                    prvs_group_id = querye["group_details"][len(querye["group_details"]) - 1]["group_id"]

                    mycols.update_one(
                        {'_id': user_id},
                        {"$set": {"active_group" : prvs_group_id}}
                    )
            else:
                mycols.update_one(
                    {'_id': user_id},
                    {"$set": {"active_group" : None}}
                )                    
            return True
    except Exception as e:
        print(e)
        return False

