#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
function: monitor the cluster state periodically
          write log data into a log file
          save recent data into local database
'''

import httplib, json, sys, time
from multiprocessing import Pool
from pymongo import MongoClient

PORT = 4243
DB_CONFIG = {
	"host" : "localhost",
	"port" : 27017,
	"user" : "datexla",
	"pwd"  : "datexla"
}

# return type: node map, whose data is in the format <- "node ip": (node id, node name) ->
def collect_worker_info(manager_ip):
	conn = httplib.HTTPConnection(manager_ip, PORT)
	conn.request("GET", "/nodes")
	response = conn.getresponse()
	data = response.read()
	json_data = json.loads(data)

	node_map = {}
	for data in json_data:
		if data["Spec"]["Role"] == "manager":
			node_ip = manager_ip
		else:
			node_ip = data["Status"]["Addr"]
		node_id = data["ID"]
		node_name = data["Description"]["Hostname"]
		curr_node_info = (node_id, node_name)
		node_map[node_ip] = curr_node_info
	
	return node_map

# probe the node's status, given it's ip address
def probe_node(node_ip):
	conn = httplib.HTTPConnection(node_ip, PORT)
	conn.request("GET", "/containers/all/stats")
	response = conn.getresponse()
	data = response.read()
	json_data = json.loads(data)
	json_data["hostName"] = node_map[node_ip][1]
	json_data["nodeID"] = node_map[node_ip][0]
	json_data["ip"] = node_ip
	return json_data

if __name__ == "__main__":
	#input validation
	if len(sys.argv) != 2:
		print "Usage: monitor.py Manager_IP_Address"
		sys.exit(1)
	manager_ip = sys.argv[1]

	# collect all workers' ip addressess
	node_map = collect_worker_info(manager_ip)
	client = MongoClient(DB_CONFIG["host"], DB_CONFIG["port"])
	db = client.datexla
	collection = db.cluster
	
	with open('cluster_score.log', 'w') as log_file:
		while True:
			# monitor the cluster
			pool = Pool(len(node_map))
			result_list = []
			for ip in node_map:
				result_list.append(pool.apply_async(probe_node, [ip]))
			pool.close()
			pool.join()
			# save data and write log
			insert_values = []
			for res in result_list:
				r = res.get()
				if "score" not in r:
					continue
				# save to database
				insert_values.append(r)
				# save to log file
				log = "%s [score print] hostName: %s, score: %f, cpuScore: %f, memScore: %f, nodeID: %s, ip: %s\n" % (r["calcTime"], r["hostName"], r["score"], r["cpuScore"], r["memScore"], r["nodeID"], r["ip"])
				log_file.write(log)
				print(log)
			# insert into database
			collection.insert(insert_values)
			time.sleep(7)