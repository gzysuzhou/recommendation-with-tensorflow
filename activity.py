# -*- coding: UTF-8 -*-
from mysql import Mysql
from userIdTransfer import UserIDTransfer
import time
from prehandle import PreHandle
import pickle

class Activity:
      
    def newActivity(self, postID, userID, text):
        if not postID or not userID or not text:
            return False
        created_at =  time.strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO activity (`post_id`, `user_id`, `text`, `created_at`) VALUES(%s, %s, %s, %s)"
        affect = Mysql().insertOne(sql, (postID, userID, text, created_at))
        self.newUserIdMapping(userID)
        self.updateUserPostScoreRecord(postID, userID, text)
        return affect

    '''
    新增用户ID 数字与字符串对应关系
    '''
    def newUserIdMapping(self, userID):
        sql = "select `int` from user_id_map where string = %s"
        has = Mysql().getOne(sql, [userID])
        if not has:
            sql = "select max(`int`) as max from user_id_map"
            max = Mysql().getOne(sql)
            next = int(max['max']) + 1
            UserIDTransfer().incrData(next, userID)
            sql = "insert into user_id_map(`int`, `string`) VALUES(%s, %s)"
            Mysql().insertOne(sql, [next, userID])

    '''
    更新单个用户行为评分数据
    '''
    def updateUserPostScoreRecord(self, postID, userID, text):
        score = 0
        if text == "表白":
            score = 50
        elif (text == "分享"):
            score = 5
        elif (text == "首次表白"):
            score = 500
        elif (text == "发表评论"):
            score = 5
        elif (text == "发表图稿"):
            score = 60
        if score > 0:
            userID = UserIDTransfer().getUserIdByString(userID)
            data = PreHandle.redis.hget(PreHandle.userPostScoreHashKey, userID)
            data = pickle.loads(data)
            has = False
            if len(data) > 0:
                for index, item in enumerate(data):
                    if item['postID'] == postID:
                        has = True
                        data[index]['score'] = item['score'] + score #将用户对同一篇卡牌评分累计
                        break
                if not has:
                    data.append({"userID": userID, "postID": postID, "score": score})
                PreHandle.redis.hset(PreHandle.userPostScoreHashKey, userID, pickle.dumps(data))
            else:
                PreHandle.redis.hset(PreHandle.userPostScoreHashKey, userID, pickle.dumps([{"userID": userID, "postID": postID, "score": score}]))

