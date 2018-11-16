# -*- coding: UTF-8 -*-
from flask import Flask
from flask import request
import json
from post import Post
from activity import Activity
from recommand import Recommand
from userIdTransfer import UserIDTransfer
app = Flask(__name__)


@app.route('/')
def hello_world():
    print("name:")
    print(request.args.get("name"))
    print("all:")
    print(json.dumps(request.args))
    return json.dumps(request.args)

'''
用户行为记录/新增作品同步接口
'''    
@app.route('/activity', methods=["POST","GET"])
def new_activity():
    postID = request.args.get('postID')
    postName = str(request.args.get("postName"))
    userID = request.args.get('userID')
    text = str(request.args.get('text'))
    tags = str(request.args.get('tags'))
    charactersName = str(request.args.get('charactersName'))
    charactersAttr = str(request.args.get('charactersAttr'))
    res = Activity().newActivity(postID, postName, userID, text, tags, charactersName, charactersAttr)
    if not res:
        return 'error'
    return 'success'

'''
获取推荐作品接口
'''
@app.route('/recommand/<string:userID>/<int:skip>/<int:limit>', methods=["GET"])
def get_recommandation(userID, skip, limit):
    userIDNumber = UserIDTransfer().getUserIdByString(userID)
    if not userIDNumber:
        return json.dumps([])
    recommandations, totalCount, hasNextPage, nextCursor = Recommand().getRecommand(userIDNumber, skip, limit)
    if recommandations:
        return json.dumps({"totalCount": totalCount, "pageInfo": {"hasNextPage": hasNextPage, "nextCursor": nextCursor}, "nodes": recommandations})
    else:
        return json.dumps({"totalCount": 0, "pageInfo": {"hasNextPage": False, "nextCursor": 0}, "nodes": []})

if __name__ == '__main__':
    app.run(port=80)


