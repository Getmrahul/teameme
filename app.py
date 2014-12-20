#! usr/bin/python

#App Imports
import os
from flask import Flask, request, render_template, json, Response, session, redirect, url_for, Markup
from werkzeug import secure_filename
import urllib2
import json
import db

#App Settings
app = Flask(__name__)
app.secret_key = os.urandom(25)
slack_id = '3259978903.3264616612'
slack_sec = '0387e1dc50dd6e816d855270bdadb339'
db_obj = db.db()

#Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth')
def auth():
    code = request.args.get('code')
    response = urllib2.urlopen('https://slack.com/api/oauth.access?code='+code+'&client_id='+slack_id+'&client_secret='+slack_sec)
    data = json.load(response)
    auth_code = data["access_token"].encode('utf-8')
    response = urllib2.urlopen('https://slack.com/api/auth.test?token='+auth_code)
    data = json.load(response)
    tid = data["team_id"]
    uid = data["user_id"]
    records = db_obj.connect(tid, uid)
    if not records:
        return render_template('join.html', token = auth_code)
    else:
        return "Existing user"



#Flask Server
if __name__ == "__main__":
    app.run(debug=True)
