#! usr/bin/python
# -*- coding: utf-8 -*-

#App Imports
import os
from flask import Flask, request, render_template, json, Response, session, redirect, url_for, Markup
from werkzeug import secure_filename
import urllib2
import json
from operator import itemgetter
import db
import re

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
    db_obj = db.db()
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
        session["uname"] = records[4].capitalize()
        session["tname"] = records[2].capitalize()
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
        session["uname"] = uname.capitalize()
        session["tname"] = tname.capitalize()
        session["channels"] = lists
        return redirect(url_for('home'))
    except Exception:
        return "Error"

@app.route('/home')
def home():
    if 'auth' not in session:
        return redirect(url_for('index'))
    return render_template('home.html')

@app.route('/feed')
def feed():
    channels = request.args.get('ch')
    ch = channels.split('|m|')
    i = 0
    cl = []
    feed = []
    while i < len(ch):
        tmp = ch[i].split('-_-')
        response = urllib2.urlopen('https://slack.com/api/channels.history?token='+session["auth"]+'&channel='+tmp[0])
        cn = tmp[1][0]
        cn = cn.upper()
        data = json.load(response)
        j = 0
        while j < len(data["messages"]):
            if data["messages"][j]["text"] == "":
                ts = data["messages"][j]["ts"]
                text = data["messages"][j]["attachments"][0]["text"]
                matches = re.findall(r'\<(.+?)\>',text)
                k = 0
                while k < len(matches):
                    tag = matches[k].split("|")
                    code = "<a href=\""+tag[0]+"\" target=\"_blank\">"+tag[1]+"</a>"
                    text = text.replace('<'+matches[k]+'>',code)
                    k = k + 1
                pretext = data["messages"][j]["attachments"][0]["fallback"]
                matches = re.findall(r'\<(.+?)\>',pretext)
                k = 0
                while k < len(matches):
                    tag = matches[k].split("|")
                    code = "<a href=\""+tag[0]+"\" target=\"_blank\">"+tag[1]+"</a>"
                    pretext = pretext.replace('<'+matches[k]+'>',code)
                    k = k + 1
                feed.append({"ts":float(ts), "text": text, "pretext": pretext, "cn": cn, "fcn": tmp[1].capitalize()})
            j = j + 1
        i = i + 1
    if not feed:
        data = {"status":0,"data":"Failed!"}
        js = json.dumps(data)
        resp = Response(js, status = 200, mimetype = 'application/json')
        return resp
    nfeed = sorted(feed, key=itemgetter('ts'), reverse=True)
    data = {"status":1,"data":nfeed}
    js = json.dumps(data)
    resp = Response(js, status = 200, mimetype = 'application/json')
    return resp

@app.route('/logout')
def logout():
    session.pop('auth', None)
    session.pop('tid', None)
    session.pop('turl', None)
    session.pop('tname', None)
    session.pop('channels', None)
    session.pop('uid', None)
    session.pop('uname', None)
    return redirect(url_for('index'))

#Flask Server
if __name__ == "__main__":
    app.run(debug=True)
