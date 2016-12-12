import sys, os, socket
import json, requests
import time

from multiprocessing import Pool
from multiprocessing import Manager
from multiprocessing.dummy import Pool as ThreadPool


import curses

def getInput():
	# check for input
	if len(sys.argv) != 4:
		print "Usage:", sys.argv[0], "master_ip", "serviceName" , "stream"
		sys.exit(1)
	ip = sys.argv[1]
	# check valid ip
	try:
		socket.inet_aton(ip)
	except socket.error:
		print "error: ip is invalid"
		exit(1)
	serviceName = sys.argv[2]
	stream = sys.argv[3]
	return ip, serviceName,stream

def getNodes(ip):
	url = "http://" + ip + ":4243/nodes"
	response = 	requests.get(url)
	nodes = response.json()
	nodeIDMap = {}
	for node in nodes:
		nodeId = node["ID"]
		hostName = node["Description"]["Hostname"]
		ip = node["Status"]["Addr"]
		nodeIDMap[nodeId] = {"Ip": ip, "HostName": hostName}
	return nodeIDMap

class  Task():
	def __init__(self, taskID,nodeID,containerID,state):
		self.taskID = taskID
		self.nodeID = nodeID
		self.containerID = containerID
		self.state = state
		
def getTasks(ip,serviceName):
	tasks = []
	url = "http://" + ip + ":4243/tasks?filters={\"service\":[\"" + serviceName + "\"]}"
	response = requests.get(url)
	ignoreState = ("rejected", "preparing","failed")
	for i in response.json():
		task = Task(i["ID"],i["NodeID"],
				i["Status"]["ContainerStatus"]["ContainerID"],
				i["Status"]["State"])
		if task.state in ignoreState:
			continue
		tasks.append(task)
	return tasks

def collect(arg):
	ip = arg[0]
	containerID = arg[1]
	stream = arg[2]
	lock = arg[3]
	statsDict = arg[4]
	url = "http://" + ip + ":4243/containers/" + containerID + "/stats"
	playload = {'stream': stream}
	response = requests.get(url, params=playload,stream=bool(stream))
	
	try:
		for line in response.iter_lines():
			if line:
				stat = json.loads(line)
				lock.acquire()
				statsDict[stat["name"]] = stat
				#print 'name:',stat["name"]
				#print 'process id:', os.getpid()
				lock.release()
	except:
		#raise e
		return



def collectStats(tasks,nodeIDMap,stream):
	args = []
	manager = Manager()
	lock = manager.Lock()
	statsDict = manager.dict()
	for task in tasks:
		arg = [nodeIDMap[task.nodeID]["Ip"],task.containerID,stream,lock,statsDict]
		args.append(arg)

	pool = Pool(len(tasks)+1)
	pool.apply_async(printStat,(statsDict,lock))
	pool.map(collect,args)
	pool.close()
	pool.join()
				

def printStat(statsDict,lock):
	while True:
		try:
			time.sleep(0.5)
			#print 'process id:', os.getpid()
			os.system('clear')
			print "name cpu mem rx tx blkRead blkWrite"
			lock.acquire()
			if not statsDict:
				#print "empty" 
				lock.release()
				continue
			
			for name,stat in statsDict.items():
				
				if stat["precpu_stats"].get("system_cpu_usage","") == "":
					continue
				cpu = calcCPUPer(stat["precpu_stats"]["cpu_usage"]["total_usage"],
							stat["precpu_stats"]["system_cpu_usage"],
							stat["cpu_stats"]["cpu_usage"]["total_usage"],
							stat["cpu_stats"]["system_cpu_usage"],
							len(stat["cpu_stats"]["cpu_usage"]["percpu_usage"]))
				mem = calcMemPer(stat["memory_stats"]["usage"],stat["memory_stats"]["limit"])
				rx , tx = calcNetwork(stat["networks"])
				blkRead , blkWrite = calcBlockIO(stat["blkio_stats"]["io_service_bytes_recursive"])
				print name, cpu, mem , rx , tx
			
			#print statsDict
			lock.release()
		except:
			break


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
	ip, serviceName,stream = getInput()
	nodeIDMap = getNodes(ip)
	tasks = getTasks(ip,serviceName)
	collectStats(tasks,nodeIDMap,stream)


if __name__ == '__main__':
 	main() 
