#! usr/bin/python

#App Imports
import os
from flask import Flask, request, render_template, json, Response, session, redirect, url_for, Markup
from werkzeug import secure_filename

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
        code = Markup(code).striptags()
        url = 'https://slack.com/api/oauth.access?'+'code='+code+'&client_id=3111086527.3259178475&client_secret=fd3641ce49e6e2fa94a0bffafd3b57ad'
        resp = json.load(urllib2.urlopen(url))
        return resp

    except Exception as exp:
        return render_template('error.html')



#Flask Server
if __name__ == "__main__":
    app.run(debug=True)
