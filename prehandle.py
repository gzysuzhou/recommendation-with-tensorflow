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
        self.createPostTag()
        self.conn.dispose()
        
    def createUserPostScore(self):
        sql = "SELECT * FROM activity"
        result = self.conn.getAll(sql)
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
        for (userID, scores) in user_post_score_dist.items():
            items = {}
            currentUserScores = []
            for index, score in enumerate(scores):
                if score['postID'] in items:
                    items[score['postID']] += score['score']
                else:
                    items[score['postID']] = score['score']
            for postID, score in items.items():
                currentUserScores.append({"userID": userID, "postID": postID, "score": score})
            #print(currentUserScores)
            PreHandle.redis.hset(PreHandle.userPostScoreHashKey, userID, pickle.dumps(currentUserScores))
        
    def createPostTag(self):
        sql = "SELECT * FROM post"
        result = self.conn.getAll(sql)
        for row in result:
            PreHandle.redis.hset(PreHandle.postTagHashKey, row['post_id'], row['tags'].encode("utf8"))
            
PreHandle().run()

