from mysql import Mysql
import time

class Post:
        
    def newPost(self, postID, postName, postTags):
        if not postID  or not postName:
            return False
        created_at =  time.strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO post (`post_id`, `name`, `tags`, `created_at`) VALUES(%s, %s, %s, %s)"
        affect = Mysql().insertOne(sql, (postID, postName, postTags, created_at))
        return affect
        
