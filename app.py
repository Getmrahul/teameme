#! usr/bin/python

#App Imports
import os
from flask import Flask, request, render_template, json, Response, session, redirect, url_for, Markup
from werkzeug import secure_filename

#App Settings
app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(25)


#Routes
@app.route('/')
def index():
    return 'login'



#Flask Server
if __name__ == "__main__":
    app.run(debug=True)
