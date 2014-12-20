#! usr/bin/python
# -*- coding: utf-8 -*-

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
    auth_code = data["access_token"]#'xoxp-3259978903-3259978905-3263464205-9e2605'#
    response = urllib2.urlopen('https://slack.com/api/auth.test?token='+auth_code)
    data = json.load(response)
    tid = data["team_id"]
    uid = data["user_id"]
    records = db_obj.connect(tid, uid)
    if not records:
        response = urllib2.urlopen('https://slack.com/api/channels.list?token='+auth_code)
        turl = data["url"]
        tname = data["team"]
        uname = data["user"]
        data = json.load(response)
        channels = ''
        i = 0
        while i < len(data["channels"]):
            if channels == '':
                channels = channels + data["channels"][i]["id"]+'-_-'+data["channels"][i]["name"]
            else:
                channels = channels + '|m|'+ data["channels"][i]["id"]+'-_-'+data["channels"][i]["name"]
            i = i+1
        return render_template('join.html', tid = tid, uid = uid, turl = turl, tname = tname, uname = uname, channels = channels)
    else:
        return "Existing user"

@app.route('/create', methods = ["POST"])
def create():
    tid = request.form["tid"]
    uid = request.form["uid"]
    tname = request.form["tname"]
    turl = request.form["turl"]
    uname = request.form["uname"]
    chlist = request.form.getlist("chlist")
    lists = ''
    while (i<len(chlist)):
        if lists == '':
            lists = lists + chlist[i]
        else:
            lists = lists + '|m|' + chlist[i]
        i = i + 1
    return lists

#Flask Server
if __name__ == "__main__":
    app.run(debug=True)
