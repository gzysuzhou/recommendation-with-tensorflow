# -*- coding: UTF-8 -*-
import redis
from mysql import Mysql

class UserIDTransfer(object):

    redis = None

    def __init__(self):
        UserIDTransfer.redis = redis.Redis(host='127.0.0.1', port=6379, db=0)


    #首次加载入缓存
    def loadData(self):
        sql = "select * from user_id_map"
        userIDs = Mysql().getAll(sql)
        for it in userIDs:
            UserIDTransfer.redis.hset("user_id_transfer", str(it["string"]), str(it["int"]))


    #新增用户ID 加入缓存
    def incrData(self, userID, userIDString):
        UserIDTransfer.redis.hset("user_id_transfer", userIDString, str(userID))


    def getUserIdByString(self, stringUserId):
        number = UserIDTransfer.redis.hget("user_id_transfer", stringUserId)
        if number:
            return int(number)
        else:
            sql = "select * from user_id_map where string = %s "
            row = Mysql().getOne(sql, [stringUserId])
            if not row:
                return False
            number = row["int"]
            if number:
                self.incrData(number, stringUserId)
                return int(number)
            else:
                return False

if __name__ == '__main__':
    UserIDTransfer().loadData()

