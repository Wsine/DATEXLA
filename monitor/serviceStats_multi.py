import sys, os, socket
import json, requests
import time

from multiprocessing import Pool
from multiprocessing import Manager
from multiprocessing.dummy import Pool as ThreadPool


from prettytable import PrettyTable
import humanfriendly

def getInput():
	# check for input
	if len(sys.argv) !=3:
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
	stream = 1	
	return ip, serviceName,stream

def getNodes(mip):
	url = "http://" + mip + ":4243/nodes"
	response = 	requests.get(url)
	nodes = response.json()
	nodeIDMap = {}
	for node in nodes:
		nodeId = node["ID"]
		hostName = node["Description"]["Hostname"]
		ip = node["Status"]["Addr"]
		if ip == "127.0.0.1":
			ip = mip
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
	nodeName = arg[1]
	containerID = arg[2]
	stream = arg[3]
	lock = arg[4]
	statsDict = arg[5]
	url = "http://" + ip + ":4243/containers/" + containerID + "/stats"
	playload = {'stream': stream}
	try:
		response = requests.get(url, params=playload,stream=bool(stream))
	except requests.ConnectionError as e:
		print e
	
	try:
		for line in response.iter_lines():
			if line:
				stat = json.loads(line)
				lock.acquire()
				stat["nodeName"] = nodeName
				statsDict[stat["name"]] = stat
				#print 'name:',stat["name"]
				#print 'process id:', os.getpid()
				lock.release()
	except:
		response.close()
		#raise e
		return



def collectStats(serviceName,tasks,nodeIDMap,stream):
	args = []
	manager = Manager()
	lock = manager.Lock()
	statsDict = manager.dict()
	for task in tasks:
		arg = [nodeIDMap[task.nodeID]["Ip"],nodeIDMap[task.nodeID]["HostName"],task.containerID,stream,lock,statsDict]
		args.append(arg)
	pool = Pool(len(tasks)+1)
	pool.apply_async(printStat,(serviceName,statsDict,lock))
	pool.map(collect,args)
	pool.close()
	pool.join()
				

def printStat(serviceName,statsDict,lock):
	while True:
		try:
			time.sleep(0.5)
			#print 'process id:', os.getpid()
			os.system('clear')
			table = PrettyTable(["name","node","cpu %", "mem %", "net I/O","block I/O"])
			table.align = "c"
			table.sortby = "name"
			#print "name cpu mem rx tx blkRead blkWrite"
			lock.acquire()
			if not statsDict:
				#print "empty" 
				print table
				lock.release()
				continue

			logg = open(serviceName,"a")

			for name,stat in statsDict.items():
				
				if stat["precpu_stats"].get("system_cpu_usage","") == "":
					continue
				cpu = calcCPUPer(stat["precpu_stats"]["cpu_usage"]["total_usage"],
						stat["precpu_stats"]["system_cpu_usage"],
						stat["cpu_stats"]["cpu_usage"]["total_usage"],
						stat["cpu_stats"]["system_cpu_usage"],
						len(stat["cpu_stats"]["cpu_usage"]["percpu_usage"]))
				cpuStr = "%.2f"%(cpu)
				mem = calcMemPer(stat["memory_stats"]["usage"],stat["memory_stats"]["limit"])
				memStr = "%.2f"%(mem)
				rx , tx = calcNetwork(stat["networks"])
				netStr = "%s / %s"%(humanfriendly.format_size(rx, binary=True),
								humanfriendly.format_size(tx, binary=True))
				blkRead , blkWrite = calcBlockIO(stat["blkio_stats"]["io_service_bytes_recursive"])
				blkStr = "%s / %s"%(humanfriendly.format_size(blkRead, binary=True),
								humanfriendly.format_size(blkWrite, binary=True))


				logStr =  "%s %s %.2f %.2f %.2f %.2f %.2f %.2f\n"%(stat["read"],name[1:len(name)-26],cpu,mem,rx,tx,blkRead,blkWrite)
				#print logStr
				logg.write(logStr)
				table.add_row([name[1:len(name)-26],stat["nodeName"],cpuStr,memStr,netStr,blkStr])				
				
			logg.close()
			print table
			#print statsDict
			lock.release()
		except:
			logg.close()
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
	collectStats(serviceName,tasks,nodeIDMap,stream)


if __name__ == '__main__':
 	main() 
