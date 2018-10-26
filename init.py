
import math
import json
import csv
from operator import itemgetter
import pymysql
import time
db = pymysql.Connect(
    host='localhost',
    port=3306,
    user='root',
    passwd='root',
    db='calicali',
    charset='utf8'
)
cursor = db.cursor()
#https://www.jianshu.com/p/0d84b8fc9063
class initLeanCloudData(object):
    
    def load_data(self, path_activity, path_post, path_tag, path_tag_post):
        with open(path_activity, encoding='utf-8') as f:
             activitys = json.load(f)
        userID = 0
        userIDStrings = {}
        userIDMapValues = ''
        activityValues = ''
        i = 1 
        for activity in activitys["results"]:
            item = {}
            if (activity["user"]["objectId"] in userIDStrings):
                item["userID"] = userIDStrings[activity["user"]["objectId"]]
            else:
                userID +=1
                userIDStrings[activity["user"]["objectId"]] = userID
                item["userID"] = userID
                userIDMapValues += "("+str(userID)+','+ "'"+activity["user"]["objectId"]+"'" "),"
            item["postID"] = activity["post"]["objectId"]
            activityValues += "('"+activity["post"]["objectId"] + "','"+activity["user"]["objectId"] + "','" + activity["text"] + "','" + time.strftime('%Y-%m-%d %H:%M:%S') + "'),"
            if (i % 1000 == 0):
                activityValues = activityValues[: -1]
                sql_activity = "INSERT INTO activity(`post_id`, `user_id`, `text`, `created_at`) VALUES " + activityValues
                cursor.execute(sql_activity)
                activityValues = ''
            i += 1
        userIDMapValues = userIDMapValues[: -1]
        sql = "INSERT INTO user_id_map (`int`, `string`) VALUES " + userIDMapValues
        cursor.execute(sql)
        activityValues = activityValues[: -1]
        sql_activity = "INSERT INTO activity(`post_id`, `user_id`, `text`, `created_at`) VALUES " + activityValues
        cursor.execute(sql_activity)
        #加载作品标签
        with open(path_post, encoding='utf-8') as pf:
            p = json.load(pf)
            posts = []
            for post in p["results"]:
                item = {}
                item["postID"] = post["objectId"]
                item["name"] = post["name"]
                posts.append(item)
        with open(path_tag, encoding='utf-8') as tf:
            t = json.load(tf)
            tags = {}
            for tag in t["results"]:
                tags[tag["objectId"]] = tag["name"]
        
        with open(path_tag_post, encoding='utf-8') as ptf:
            r = json.load(ptf)
            relations = {}
            for relation in r["results"]:
                if (relation["owningId"] in relations):
                    relations[relation["owningId"]].append(tags[relation["relatedId"]])
                else:
                    relations[relation["owningId"]] = [tags[relation["relatedId"]]]
       
        post_tag = []
        data = []
        j = 1
        for post in posts:
            item = {}
            d = ()
            item["postID"] = post["postID"]
            item["name"] = post["name"]
            if(post["postID"] in relations):
                item["tag"] = "|".join(relations[post["postID"]])
                d = (post["postID"], post["name"], "|".join(relations[post["postID"]]), time.strftime('%Y-%m-%d %H:%M:%S'))
            else:
                item["tag"] = ""
                d = (post["postID"], post["name"], "", time.strftime('%Y-%m-%d %H:%M:%S'))
            post_tag.append(item)
            data.append(d)
            if (j % 1000 == 0):
                sql = "INSERT INTO post(`post_id`, `name`, `tags`, `created_at`) VALUES (%s, %s, %s, %s)"
                cursor.executemany(sql, data)
                data = []
            j += 1
        if (len(data) > 0):
            sql = "INSERT INTO post(`post_id`, `name`, `tags`, `created_at`) VALUES (%s, %s, %s, %s)"
            cursor.executemany(sql, data)

    def __init__(self,path_activity, path_post, path_tag, path_tag_post):
        self.load_data(path_activity, path_post, path_tag, path_tag_post)
        

path_activity = '.\\source\\Activity.json'
path_post = '.\\source\\Post.json'
path_tag = '.\\source\\Tag.json'
path_tag_post = '.\\source\\_Join_Tag_tags_Post.json'
r = initLeanCloudData(path_activity, path_post, path_tag, path_tag_post)
cursor.close()
db.close()