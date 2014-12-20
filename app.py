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
    if 'auth' in session:
        return redirect(url_for('home'))
    return render_template('index.html')

@app.route('/problem')
def error():
    return render_template('error.html')

@app.route('/auth')
def auth():
    if 'auth' in session:
        return redirect(url_for('home'))
    code = request.args.get('code')
    response = urllib2.urlopen('https://slack.com/api/oauth.access?code='+code+'&client_id='+slack_id+'&client_secret='+slack_sec)
    data = json.load(response)
    auth_code = 'xoxp-3259978903-3259978905-3263464205-9e2605'#'xoxp-3259978903-3259978905-3263464205-9e2605'#data["access_token"].encode('utf-8')
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
        return render_template('join.html', tid = tid, uid = uid, turl = turl, tname = tname, uname = uname, channels = channels, auth = auth_code)
    else:
        session["auth"] = auth_code
        session["tid"] = records[1]
        session["uid"] = records[3]
        session["turl"] = records[5]
        session["uname"] = records[4]
        session["tname"] = records[2]
        session["channels"] = records[6]
        return redirect(url_for('home'))

@app.route('/create', methods = ["POST"])
def create():
    if 'auth' in session:
        return redirect(url_for('home'))
    tid = request.form["tid"]
    uid = request.form["uid"]
    tname = request.form["tname"]
    turl = request.form["turl"]
    uname = request.form["uname"]
    chlist = request.form.getlist("chlist")
    auth = request.form["auth"]
    lists = ''
    for ch in chlist:
        if lists == '':
            lists = lists + ch
        else:
            lists = lists + '|m|' + ch
    try:
        db_obj = db.db()
        db_obj.signup(tid, uid, tname, turl, uname, lists)
        session["auth"] = auth
        session["tid"] = tid
        session["uid"] = uid
        session["turl"] = turl
        session["uname"] = uname
        session["tname"] = tname
        session["channels"] = lists
        return redirect(url_for('home'))
    except Exception:
        return "Error"

@app.route('/home')
def home():
    if 'auth' not in session:
        return redirect(url_for('index'))
    return render_template('home.html')

@app.route('/logout')
def logout():
    app.secret_key = os.urandom(25)
    return redirect(url_for('index'))

#Flask Server
if __name__ == "__main__":
    app.run(debug=True)
