#! usr/bin/python

import psycopg2

from os.path import exists
from os import makedirs
import os

import urlparse

urlparse.uses_netloc.append('postgres')
url = urlparse.urlparse(os.environ.get('DATABASE_URL',"***"))

det = "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname)

def connect():
	return psycopg2.connect(det)

class db(object):
    def connect(self, tid, uid):
        con = connect()
        c = con.cursor()
        q = "select * from slack_list where tid='%s' and uid='%s'" % (tid, uid)
        c.execute(q)
        record = c.fetchone()
        row = []
        if not record:
            return row
        for r in record:
            row.append(r)
        con.close()
        return row
    def signup(self, tid, uid, tname, turl, uname, lists):
		q = "insert into slack_list (tid, uid, tname, turl, uname, channels) values('%s','%s','%s','%s','%s', '%s')" % (tid, uid, tname, turl, uname, lists)
		con = connect()
		c = con.cursor()
		c.execute(q)
		con.commit()
		con.close()
