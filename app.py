#! usr/bin/python

#App Imports
import os
from flask import Flask, request, render_template, json, Response, session, redirect, url_for, Markup
from werkzeug import secure_filename
import urllib2

#App Settings
app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(25)
slack_id = '3259978903.3264616612'
slack_sec = '0387e1dc50dd6e816d855270bdadb339'

#Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth')
def auth():
    try:
        code = request.args.get('code')
        resp = urllib2.urlopen("https://slack.com/api/oauth.access?"+'code='+code+'&client_id='+slack_id+'&client_secret='+slack_sec).read()
        js = resp
        sp = js.split('&')
        token = sp[0].split('=')
        return token[1]

    except Exception as exp:
        return exp



#Flask Server
if __name__ == "__main__":
    app.run(debug=True)
