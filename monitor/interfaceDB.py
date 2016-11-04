#!/usr/bin/python
# -*- coding: UTF-8 -*-

from flask import Flask, json
from flaskext.mysql import MySQL

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'crash'
app.config['MYSQL_DATABASE_DB'] = 'datexla_dcn'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

def dictfetchall(cursor):
	"""Returns all rows from a cursor as a list of dicts"""
	desc = cursor.description
	return [dict(itertools.izip([col[0] for col in desc], row)) for row in cursor.fetchall()]

@app.route('/')
def home():
	return 'Welcome'

@app.route('/docker/stats')
def api_stats():
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT * FROM docker_stats")
	results = dictfetchall(cursor)
	return json.dumps(results)

if __name__ == '__main__':
	app.run()