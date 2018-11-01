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
新增作品同步接口
'''
@app.route('/post')
def new_post():
    postID = request.args.get('postID')
    postName = request.args.get("postName")
    postTags = request.args.get('postTags')
    res = Post().newPost(postID, postName, postTags)
    if not res:
        return 'error'
    return 'success'

'''
用户行为记录同步接口
'''    
@app.route('/activity')
def new_activity():
    postID = request.args.get('postID')
    userID = request.args.get('userID')
    text = request.args.get('text')
    res = Activity().newActivity(postID, userID, text)
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
    result = Recommand().getRecommand(userIDNumber, skip, limit)
    if result:
        return json.dumps(result)
    else:
        return json.dumps([])

if __name__ == '__main__':
    app.run(port=80)


