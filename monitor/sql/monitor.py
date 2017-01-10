# -*- coding: utf-8 -*-

'''
function: monitor the cluster state periodically
          write log data into a log file
          save recent data into local database
'''

import httplib
import json
import sys
import time
import threading
from multiprocessing import Process, Manager, Lock, Pool
import MySQLdb

PORT = 4243

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

	if len(json_data) == 0:
		return

	calc_time = json_data["calcTime"]
	cpu_score = json_data["cpuScore"]
	mem_score = json_data["memScore"]
	score = json_data["score"]
	node_id = node_map[node_ip][0]
	node_name = node_map[node_ip][1]
	result = (calc_time, node_name, node_id, score, cpu_score, mem_score)

	return result

if __name__ == "__main__":
	#input validation
	if len(sys.argv) != 2:
		print "Usage: monitor.py Manager IP Address"
		sys.exit(1)
	manager_ip = sys.argv[1]

	# collect all workers' ip addressess
	node_map = collect_worker_info(manager_ip)
	conn = MySQLdb.connect(user='root', passwd='crash', host='127.0.0.1', db='datexla_dcn')
	
	while True:
		# monitor the cluster
		pool = Pool(len(node_map))
		result_list = []
		for ip in node_map:
			result_list.append(pool.apply_async(probe_node, [ip]))
		pool.close()
		pool.join()

		# save data and write log
		log_file = open('cluster_score.log', 'a')
		cur = conn.cursor()
		sql_format = 'insert into ClusterInfo values(%s, %s, %s, %s, %s);'
		insert_values = []
		for res in result_list:
			r = res.get()
			calc_time, node_name, node_id, score, cpu_score, mem_score = r[0], r[1], r[2], r[3], r[4], r[5]
			# write log
			log_file.write("Calc_Time: %s Name: %s ID: %s Score: %f CPU_Score: %f Mem_Score: %f\n" % (calc_time, node_name, node_id, score, cpu_score, mem_score))
			# save data into database
			curr_value = (calc_time, node_id, score, cpu_score, mem_score)
			insert_values.append(curr_value)
			# print for debugging
			print("Calc_Time: %s Name: %s ID: %s Score: %f CPU_Score: %f Mem_Score: %f" % (calc_time, node_name, node_id, score, cpu_score, mem_score))
		cur.executemany(sql_format, insert_values)
		cur.close()
		conn.commit()
	
		time.sleep(7)
	# close database and log file
	conn.close()
	log_file.close()