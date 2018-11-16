# -*- coding: UTF-8 -*-
from mysql import Mysql
import time
import json

class Post:
        
    def newPost(self, postID, postName, postTags, relatedCharactersName, relatedCharactersAttr):
        created_at =  time.strftime('%Y-%m-%d %H:%M:%S')
        character_attr = []
        character = ''
        if relatedCharactersName:
            if "|" in relatedCharactersName:
                temp = relatedCharactersName.split("|")
            else:
                temp = [relatedCharactersName]
            relatedCharactersName = "|".join(list(set(temp)))
            character_attr.append(relatedCharactersName)
        if relatedCharactersAttr:
            if "|" in relatedCharactersAttr:
                temp = relatedCharactersAttr.split("|")
            else:
                temp = [relatedCharactersAttr]
            attr = []
            for item in temp:
                item = json.loads(item)
                if "性别" in item:
                    attr.append(item["性别"])
                if "萌属性" in item:
                    attr.append(item["萌属性"].replace("、", "|"))
            if len(attr) > 0:
                attr = list(set("|".join(attr).split("|")))
                character_attr.append("|".join(attr))
        if len(character_attr) > 0:
            characterNameAndAttr = "|".join(character_attr)
        sql = "INSERT INTO post (`post_id`, `name`, `tags`, `character_attr`, `created_at`) VALUES(%s, %s, %s, %s, %s)"
        affect = Mysql().insertOne(sql, (postID, postName, postTags, characterNameAndAttr, created_at))
        return affect
        
