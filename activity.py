from mysql import Mysql
import time

class Activity:
        
    def newActivity(self, postID, userID, text):
        if not postID or not userID or not text:
            return False
        created_at =  time.strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO activity (`post_id`, `user_id`, `text`, `created_at`) VALUES(%s, %s, %s, %s)"
        affect = Mysql().insertOne(sql, (postID, userID, text, created_at))
        return affect