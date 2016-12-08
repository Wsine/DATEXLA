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
	url = "http://" + ip + ":4243/tasks?filters={\"service\":[\"" + serviceName + "\"]}"
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
	print "taskID nodeName cpu mem rx tx blkRead blkWrite"
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
		cpu = calcCPUPer(stat["precpu_stats"]["cpu_usage"]["total_usage"],
			stat["precpu_stats"]["system_cpu_usage"],
			stat["cpu_stats"]["cpu_usage"]["total_usage"],
			stat["cpu_stats"]["system_cpu_usage"],
			len(stat["cpu_stats"]["cpu_usage"]["percpu_usage"]))
		mem = calcMemPer(stat["memory_stats"]["usage"],stat["memory_stats"]["limit"])
		rx , tx = calcNetwork(stat["networks"])
		blkRead , blkWrite = calcBlockIO(stat["blkio_stats"]["io_service_bytes_recursive"])
		print task["TaskID"], nodeIDMap[task["NodeID"]]["HostName"], cpu, mem , rx , tx

def calcMemPer(usage,limit):
	return float(usage) / float(limit) * 100.0

def calcCPUPer(preUsage,preSys,usage,sys,coreNum):
	cpuPercent = 0.0
	cpuDelta = float(usage) - float(preUsage)
	sysDelta = float(sys) - float(preSys)
	if cpuDelta > 0.0 and sysDelta > 0.0:
		cpuPercent = (cpuDelta / sysDelta) * float(coreNum) * 100.0
	return cpuPercent

def calcNetwork(networks):
	rx = 0.0
	tx = 0.0
	for i in networks:
		rx += float(networks[i]["rx_bytes"])
		tx += float(networks[i]["tx_bytes"])
	return rx , tx 

def calcBlockIO(blkIO):
	blkRead = 0.0
	blkWrite = 0.0
	for record in blkIO:
		if cmp(record["op"],"Read") == 0:
			blkRead += float(record["value"])
		elif cmp(record["op"],"Write") == 0:
			blkWrite += float(record["value"])
	return blkRead , blkWrite

def main():
	ip, serviceName = getInput()
	nodeIDMap = getNodes(ip)
	taskList = getTask(ip, serviceName)
	printStats(taskList, nodeIDMap)

if __name__ == '__main__':
	main()