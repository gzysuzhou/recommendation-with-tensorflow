
import math
import json
import csv
from operator import itemgetter
#https://www.jianshu.com/p/0d84b8fc9063
class recommender(object):
    
    def load_data(self, path_activity, path_post, path_tag, path_tag_post):
        with open(path_activity, encoding='utf-8') as f:
             activitys = json.load(f)
        user_post = []
        userID = 0
        userIDStrings = {}
        for activity in activitys["results"]:
            item = {}
            if (activity["user"]["objectId"] in userIDStrings):
                item["userID"] = userIDStrings[activity["user"]["objectId"]]
            else:
                userID +=1
                userIDStrings[activity["user"]["objectId"]] = userID
                item["userID"] = userID
            item["postID"] = activity["post"]["objectId"]
            if (activity["text"] == "表白"):
                item["score"] = 50
            elif (activity["text"] == "分享"):
                item["score"] = 5
            elif (activity["text"] == "首次表白"):
                item["score"] = 500
            elif (activity["text"] == "发表评论"):
                item["score"] = 5
            elif (activity["text"] == "发表图稿"):
                item["score"] = 60
            user_post.append(item)
        print(userIDStrings)
        self.createDictCSV("user_score.csv", user_post)
        #加载作品标签
        with open(path_post, encoding='utf-8') as pf:
            p = json.load(pf)
            posts = []
            for post in p["results"]:
                item = {}
                item["postID"] = post["objectId"]
                item["name"] = post["name"]
                posts.append(item)
            #print(posts)
        with open(path_tag, encoding='utf-8') as tf:
            t = json.load(tf)
            tags = {}
            for tag in t["results"]:
                tags[tag["objectId"]] = tag["name"]
        #print(tags)
        with open(path_tag_post, encoding='utf-8') as ptf:
            r = json.load(ptf)
            relations = {}
            for relation in r["results"]:
                if (relation["owningId"] in relations):
                    relations[relation["owningId"]].append(tags[relation["relatedId"]])
                else:
                    relations[relation["owningId"]] = [tags[relation["relatedId"]]]
        #print(relations["5b01a4fea22b9d0045147144"])
        #生成post-tag.csv
        post_tag = []
        for post in posts:
            item = {}
            item["postID"] = post["postID"]
            item["name"] = post["name"]
            if(post["postID"] in relations):
                item["tag"] = "|".join(relations[post["postID"]])
            else:
                item["tag"] = ""
            post_tag.append(item)
        self.createPostTagCsv("postTag.csv", post_tag)


    def createPostTagCsv(self, fileName="", dataList=[]):
        fieldnames =['postID','name','tag']
        item = {}
        with open(fileName, "w", encoding='utf8', newline='') as f:
            csvWriter = csv.DictWriter(f, fieldnames=fieldnames)
            csvWriter.writeheader()
            for dataDict in dataList:
                   item['postID'] = dataDict["postID"]
                   item['name'] = dataDict["name"]
                   item['tag'] = dataDict["tag"]
                   csvWriter.writerow(item)
            f.close()


    def createDictCSV(self, fileName="", dataList=[]):
        fieldnames =['userID','postID','score']
        item = {}
        with open(fileName, "w", encoding='utf8', newline='') as f:
            csvWriter = csv.DictWriter(f, fieldnames=fieldnames)
            csvWriter.writeheader()
            for dataDict in dataList:
                   item['userID'] = dataDict["userID"]
                   item['postID'] = dataDict["postID"]
                   item['score'] = dataDict["score"]
                   csvWriter.writerow(item)
            f.close()
    def __init__(self,path_activity, path_post, path_tag, path_tag_post):
        self.load_data(path_activity, path_post, path_tag, path_tag_post)

path_activity = '.\\source\\Activity.json'
path_post = '.\\source\\Post.json'
path_tag = '.\\source\\Tag.json'
path_tag_post = '.\\source\\_Join_Tag_tags_Post.json'
r = recommender(path_activity, path_post, path_tag, path_tag_post)