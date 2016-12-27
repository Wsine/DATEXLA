#!/usr/bin/python
# -*- coding: UTF-8 -*-

from flask import Flask, json
from pymongo import MongoClient

app = Flask(__name__)
DB_CONFIG = {
	"host" : "localhost",
	"port" : 27017,
	"user" : "datexla",
	"pwd"  : "datexla"
}
client = MongoClient(DB_CONFIG["host"], DB_CONFIG["port"])
db = client.datexla
collection = db.cluster

@app.route('/')
def home():
	return 'Welcome to DATEXLA monitor\n'

@app.route('/cluster/<hostName>/score')
def host_score(hostName):
	docs = collection.find({"hostName":hostName}, {"score":1})
	scores = map(lambda x : x["score"], docs)
	result = sum(scores) / len(scores)
	return json.dumps(result)

if __name__ == '__main__':
	try:
		app.run()
	finally:
		client.close()
		print("Close the mongodb connection")
