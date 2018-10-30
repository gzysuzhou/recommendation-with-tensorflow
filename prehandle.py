import csv
from mysql import Mysql

class PreHandle(object):

    def __init__(self):
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
        try:
            sql = "SELECT * FROM activity"
            result = self.conn.getAll(sql)
            user_post = []
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
                user_post.append(item)
            self.createDictCSV("user_score.csv", user_post)
        except:
            self.conn.dispose()

    def createPostTagCsv(self):
        try:
            sql = "SELECT * FROM post"
            result = self.conn.getAll(sql)
            fieldnames =['postID','name','tag']
            item = {}
            with open("postTag.csv", "w", encoding='utf8', newline='') as f:
                csvWriter = csv.DictWriter(f, fieldnames=fieldnames)
                csvWriter.writeheader()
                for row in result:
                    item['postID'] = row['post_id']
                    item['name'] = row['name']
                    item['tag'] = row['tags']
                    csvWriter.writerow(item)
                f.close()
        except:
            self.conn.dispose()
