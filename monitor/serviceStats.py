import sys, os, socket
import urllib, json

def getInput():
	# check for input
	if len(sys.argv) != 3:
		print "Usage:", sys.argv[0], "master_ip", "serviceName"
		sys.exit(1)
	ip = sys.argv[1]
	# check valid ip
	try:
		socket.inet_aton(ip)
	except socket.error:
		print "error: ip is invalid"
		exit(1)
	serviceName = sys.argv[2]
	return ip, serviceName

def getNodes(ip):
	url = "http://" + ip + ":4243/nodes"
	response = urllib.urlopen(url)
	nodes = json.loads(response.read())
	nodeIDMap = {}
	for node in nodes:
		nodeId = node["ID"]
		hostName = node["Description"]["Hostname"]
		ip = node["Status"]["Addr"]
		nodeIDMap[nodeId] = {"Ip": ip, "HostName": hostName}
	return nodeIDMap

def getTask(ip, serviceName):
	url = "http://" + ip + ":4243/tasks?name=" + serviceName
	response = urllib.urlopen(url)
	tasks = json.loads(response.read())
	taskList = []
	ignoreState = ("rejected", "preparing")
	for task in tasks:
		taskDict = {}
		taskDict["State"] = task["Status"]["State"]
		if taskDict["State"] in ignoreState:
			continue
		taskDict["TaskID"] = task["ID"]
		taskDict["NodeID"] = task["NodeID"]
		taskDict["ContainerID"] = task["Status"]["ContainerStatus"]["ContainerID"]
		taskList.append(taskDict)
	return taskList

def printStats(taskList, nodeIDMap):
	print "taskID nodeName cpu mem"
	for task in taskList:
		if task["State"] != "running":
			print task["TaskID"], nodeIDMap[task["NodeID"]]["HostName"], "--", "--"
			continue
		ip = nodeIDMap[task["NodeID"]]["Ip"]
		if ip == "127.0.0.1":
			continue
		containerID = task["ContainerID"]
		url = "http://" + ip + ":4243/containers/" + containerID + "/stats?stream=0"
		response = urllib.urlopen(url)
		stat = json.loads(response.read())
		cpu = stat["cpu_stats"]["cpu_usage"]["total_usage"]
		mem = stat["memory_stats"]["usage"]
		print task["TaskID"], nodeIDMap[task["NodeID"]]["HostName"], cpu, mem

def main():
	ip, serviceName = getInput()
	nodeIDMap = getNodes(ip)
	taskList = getTask(ip, serviceName)
	printStats(taskList, nodeIDMap)

if __name__ == '__main__':
	main()