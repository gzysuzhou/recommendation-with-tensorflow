# -*- coding: UTF-8 -*-
import csv
import redis
import pickle
from mysql import Mysql

class PreHandle(object):
    redis = None
    userPostScoreHashKey = "userPostScoreHash"
    postTagHashKey = "postTagHash"

    def __init__(self):
        PreHandle.redis = redis.Redis(host='127.0.0.1', port=6379, db=0)
        self.conn = Mysql()

    def run(self):
        self.createUserPostScore()
        self.createPostTagCsv()
        self.conn.dispose()
        
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
        
    def createUserPostScore(self):
        sql = "SELECT * FROM activity"
        result = self.conn.getAll(sql)
        user_post = []
        user_post_score_dist = {}
        userID = 0
        userIDStrings = {}
        for  row in result:
            item = {}
            if row['user_id'] in userIDStrings:
                item["userID"] = userIDStrings[row['user_id']]
            else:
                userID +=1
                userIDStrings[row['user_id']] = userID
                item["userID"] = userID
            item["postID"] = row['post_id']
            if (row['text'] == "表白"):
                item["score"] = 50
            elif (row['text'] == "分享"):
                item["score"] = 5
            elif (row['text'] == "首次表白"):
                item["score"] = 500
            elif (row['text'] == "发表评论"):
                item["score"] = 5
            elif (row['text'] == "发表图稿"):
                item["score"] = 60
            if userID in user_post_score_dist:
                user_post_score_dist[userID].append(item)
            else:
                user_post_score_dist[userID] = [item]
            user_post.append(item)
        #PreHandle.redis.hgetall(PreHandle.userPostScoreHashKey)
        #PreHandle.redis.delete(PreHandle.userPostScoreHashKey)
        for (userID, scores) in user_post_score_dist.items():
            PreHandle.redis.hset(PreHandle.userPostScoreHashKey, userID, pickle.dumps(scores))
        self.createDictCSV("user_score.csv", user_post)
        


    def createPostTagCsv(self):
        sql = "SELECT * FROM post"
        result = self.conn.getAll(sql)
        fieldnames =['postID','name','tag']
        item = {}
        PreHandle.redis.delete(PreHandle.postTagHashKey)
        with open("postTag.csv", "w", encoding='utf8', newline='') as f:
            csvWriter = csv.DictWriter(f, fieldnames=fieldnames)
            csvWriter.writeheader()
            for row in result:
                item['postID'] = row['post_id']
                item['name'] = row['name']
                item['tag'] = row['tags']
                csvWriter.writerow(item)
                PreHandle.redis.hset(PreHandle.postTagHashKey, row['post_id'], row['tags'].encode("utf8"))
            f.close()

PreHandle().run()

