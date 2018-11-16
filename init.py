
# -*- coding: UTF-8 -*-
import math
import json
import csv
from operator import itemgetter
from mysql import Mysql
import time
import os
#https://www.jianshu.com/p/0d84b8fc9063
class initLeanCloudData(object):

    def load_activity(self, path_activity):
        with open(path_activity, encoding='utf-8') as f:
             activitys = json.load(f)
        userID = 0
        userIDStrings = {}
        userIDMapValues = []
        activityValues = []
        i = 1 
        for activity in activitys["results"]:
            item = {}
            if activity["user"]["objectId"] in userIDStrings:
                item["userID"] = userIDStrings[activity["user"]["objectId"]]
            else:
                userID +=1
                userIDStrings[activity["user"]["objectId"]] = userID
                item["userID"] = userID
                userIDMapValues.append((str(userID), activity["user"]["objectId"]))
            item["postID"] = activity["post"]["objectId"]
            activityValues.append((activity["post"]["objectId"], activity["user"]["objectId"], activity["text"], time.strftime('%Y-%m-%d %H:%M:%S')))
            #分批次每次插入1000条
            if i % 100 == 0:
                sql_activity = "INSERT INTO activity(`post_id`, `user_id`, `text`, `created_at`) VALUES(%s, %s, %s, %s)" 
                Mysql().insertMany(sql_activity, activityValues)
                activityValues = []
            i += 1
        sql = "INSERT INTO user_id_map (`int`, `string`) VALUES(%s, %s)"
        Mysql().insertMany(sql, userIDMapValues)
        #插入剩下不足1000个的部分
        sql_activity = "INSERT INTO activity(`post_id`, `user_id`, `text`, `created_at`) VALUES(%s, %s, %s, %s)"
        Mysql().insertMany(sql_activity, activityValues)

    
    def load_post(self, path_post, path_tag, path_tag_post, path_character, path_character_post):
        #加载作品标签
        with open(path_post, encoding='utf-8') as pf:
            p = json.load(pf)
            posts = []
            for post in p["results"]:
                item = {}
                item["postID"] = post["objectId"]
                item["name"] = post["name"]
                posts.append(item)

        #标签名
        with open(path_tag, encoding='utf-8') as tf:
            t = json.load(tf)
            tags = {}
            for tag in t["results"]:
                tags[tag["objectId"]] = tag["name"]

        #角色属性字典
        with open(path_character, encoding='utf-8') as tf:
            t = json.load(tf)
            character_attr = {}
            for character in t["results"]:
                character_attr[character["objectId"]] = {}
                character_attr[character["objectId"]]['array'] = []
                character_attr[character["objectId"]]['string'] = ''
                character_attr[character["objectId"]]['array'].append(character["name"])
                if "properties" in character:
                    if '性别' in character["properties"]:
                        character_attr[character["objectId"]]['array'].append(character["properties"]['性别'])
                    if '萌属性' in character["properties"]:
                        character_attr[character["objectId"]]['array'].append(character["properties"]['萌属性'].replace('、', '|'))
                if len(character_attr[character["objectId"]]['array']) == 1:
                    character_attr[character["objectId"]]['string'] = character_attr[character["objectId"]]['array'][0]
                elif len(character_attr[character["objectId"]]['array']) > 1:
                    character_attr[character["objectId"]]['string'] = "|".join(character_attr[character["objectId"]]['array'])
                

        #作品ID关联的标签名称 一对多
        with open(path_tag_post, encoding='utf-8') as ptf:
            r = json.load(ptf)
            relations = {}
            for relation in r["results"]:
                if (relation["owningId"] in relations):
                    relations[relation["owningId"]].append(tags[relation["relatedId"]])
                else:
                    relations[relation["owningId"]] = [tags[relation["relatedId"]]]
        
        #作品ID关联角色属性 一对多
        with open(path_character_post, encoding='utf-8') as ptf:
             r = json.load(ptf)
             relations_character = {}
             for relation in r["results"]:
                if relation["owningId"] in relations_character and character_attr[relation["relatedId"]]['string']:
                    relations_character[relation["owningId"]] += "|" 
                    relations_character[relation["owningId"]] += character_attr[relation["relatedId"]]['string']
                    relations_character[relation["owningId"]] = "|".join(list(set(relations_character[relation["owningId"]].split("|"))))
                else:
                    relations_character[relation["owningId"]] = character_attr[relation["relatedId"]]['string']

        data = []
        j = 1
        for post in posts:
            item = {}
            d = ()
            item["postID"] = post["postID"]
            item["name"] = post["name"]
            #标签字段
            if post["postID"] in relations:
                item["tag"] = "|".join(relations[post["postID"]])
            else:
                item["tag"] = ""
            #角色属性字段
            if post["postID"] in relations_character:
                if relations_character[post["postID"]]:
                    item["character_attr"] = relations_character[post["postID"]]
                else:
                    item["character_attr"] = ""
            else:
                item["character_attr"] = ""
            d = (post["postID"], post["name"], str(item["tag"]), str(item["character_attr"]), time.strftime('%Y-%m-%d %H:%M:%S'))
            data.append(d)
            if j % 100 == 0:
                sql = "INSERT INTO post(`post_id`, `name`, `tags`, `character_attr`, `created_at`) VALUES (%s, %s, %s, %s, %s)"
                Mysql().insertMany(sql, data)
                data = []
            j += 1
        if len(data) > 0:
            sql = "INSERT INTO post(`post_id`, `name`, `tags`, `character_attr`, `created_at`) VALUES (%s, %s, %s, %s, %s)"
            Mysql().insertMany(sql, data)

    def __init__(self,path_activity, path_post, path_tag, path_tag_post, path_character, path_character_post):
        self.load_activity(path_activity)
        self.load_post(path_post, path_tag, path_tag_post, path_character, path_character_post)
        

path_activity = 'source'+os.sep+'calicali-dev'+os.sep+'Activity.json'
path_post = 'source'+os.sep+'calicali-dev'+os.sep+'Post.json'
path_tag = 'source'+os.sep+'calicali-dev'+os.sep+'Tag.json'
path_tag_post = 'source'+os.sep+'calicali-dev'+os.sep+'_Join_Tag_tags_Post.json'
path_character = 'source'+os.sep+'calicali-dev'+os.sep+'Character.json'
path_character_post = 'source'+os.sep+'calicali-dev'+os.sep+'_Join_Character_characters_Post.json'
r = initLeanCloudData(path_activity, path_post, path_tag, path_tag_post, path_character, path_character_post)