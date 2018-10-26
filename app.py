from flask import Flask
from flask import request
import json
from post import Post
from activity import Activity
from recommand import Recommand
app = Flask(__name__)


@app.route('/')
def hello_world():
    print("name:")
    print(request.args.get("name"))
    print("all:")
    print(json.dumps(request.args))
    return json.dumps(request.args)
@app.route('/post')
def new_post():
    postID = request.args.get('postID')
    postName = request.args.get("postName")
    postTags = request.args.get('postTags')
    res = Post().newPost(postID, postName, postTags)
    if not res:
        return 'error'
    return 'success'
@app.route('/activity')
def new_activity():
    postID = request.args.get('postID')
    userID = request.args.get('userID')
    text = request.args.get('text')
    res = Activity().newActivity(postID, userID, text)
    if not res:
        return 'error'
    return 'success'
@app.route('/recommand/<int:userID>', methods=["GET"])
def get_recommandation(userID):
    return Recommand().getRecommand(userID)
