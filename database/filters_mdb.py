import os
import re
import pymongo

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config
 
myclient = pymongo.MongoClient(Config.DATABASE_URI)
mydb = myclient[Config.DATABASE_NAME]



async def add_filter(grp_id, text, reply_text, btn, file, alert):
    mycol = mydb[str(grp_id)]
    # mycol.create_index([('text', 'text')])

    data = {
        'text':str(text),
        'reply':str(reply_text),
        'btn':str(btn),
        'file':str(file),
        'alert':str(alert)
    }

    try:
        mycol.update_one({'text': str(text)},  {"$set": data}, upsert=True)
    except:
        print('Couldn`t Save, Check Your DB')
             
     
async def find_filter(group_id, name):
    mycol = mydb[str(group_id)]
    
    query = mycol.find( {"text":name})
    # query = mycol.find( { "$text": {"$search": name}})
    try:
        for file in query:
            reply_text = file['reply']
            btn = file['btn']
            fileid = file['file']
            try:
                alert = file['alert']
            except:
                alert = None
        return reply_text, btn, alert, fileid
    except:
        return None, None, None, None


async def get_filters(group_id):
    mycol = mydb[str(group_id)]

    texts = []
    query = mycol.find()
    try:
        for file in query:
            text = file['text']
            texts.append(text)
    except:
        pass
    return texts


async def delete_filter(message, text, group_id):
    mycol = mydb[str(group_id)]
    
    myquery = {'text':text }
    query = mycol.count_documents(myquery)
    if query == 1:
        mycol.delete_one(myquery)
        await message.reply_text(
            f"'`{text}`' **Deleted. I'll Not Respond To That Filter Anymore.**",
            quote=True,
            parse_mode="md"
        )
    else:
        await message.reply_text("**🛂 Couldn't Find That Filter !**", quote=True)


async def del_all(message, group_id, title):
    if str(group_id) not in mydb.list_collection_names():
        await message.edit_text(f"Nothing to remove in {title}!")
        return
        
    mycol = mydb[str(group_id)]
    try:
        mycol.drop()
        await message.edit_text(f"**🛂 All Filters From {title} Has Been Removed**")
    except:
        await message.edit_text(f"**🛂 Couldn't Remove All Filters From Group !**")
        return


async def count_filters(group_id):
    mycol = mydb[str(group_id)]

    count = mycol.count()
    if count == 0:
        return False
    else:
        return count


async def filter_stats():
    collections = mydb.list_collection_names()

    if "CONNECTION" in collections:
        collections.remove("CONNECTION")
    if "USERS" in collections:
        collections.remove("USERS")

    totalcount = 0
    for collection in collections:
        mycol = mydb[collection]
        count = mycol.count()
        totalcount = totalcount + count

    totalcollections = len(collections)

    return totalcollections, totalcount
