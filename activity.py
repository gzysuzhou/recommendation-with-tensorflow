from mysql import Mysql
from userIdTransfer import UserIDTransfer
import time

class Activity:
      
    def newActivity(self, postID, userID, text):
        if not postID or not userID or not text:
            return False
        created_at =  time.strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO activity (`post_id`, `user_id`, `text`, `created_at`) VALUES(%s, %s, %s, %s)"
        affect = Mysql().insertOne(sql, (postID, userID, text, created_at))
        self.newUserIdMapping(userID)
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