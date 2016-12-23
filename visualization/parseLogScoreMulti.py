import sys, re, time
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import math

FIGURE_COUNT = 0
scoreDict1 = {}
scoreDict2 = {}
lineType1 = 'b^-'
lineType2 = 'ro-'
label1 = ''
label2 = ''
meanList1, stdVarList1 = [], []
meanList2, stdVarList2 = [], []

def readFile(fileName):
	scoreDict = {}
	# Read logs from log file
	with open(fileName) as logFile:
		# ignore the last empty line
		for line in logFile.readlines()[:-1]:
			log = re.split('[\[\]]*', line)
			tag = re.sub('\s+', ' ', log[1].strip())
			content = log[2].strip().split(',')
			if tag == 'score print':
				hostName = content[0].split()[1]
				score = float(content[1].split()[1])
				cpuScore = float(content[2].split()[1])
				memScore = float(content[3].split()[1])
				if not hostName in scoreDict:
					scoreDict[hostName] = {"score": [score], "cpuScore": [cpuScore], "memScore": [memScore]}
				else:
					scoreDict[hostName]["score"].append(score)
					scoreDict[hostName]["cpuScore"].append(cpuScore)
					scoreDict[hostName]["memScore"].append(memScore)
	return scoreDict

def plotSingle(data1, data2, nodeName1, nodeName2, typ):
	nodeName1 = nodeName1.capitalize()
	nodeName2 = nodeName2.capitalize()
	global FIGURE_COUNT
	FIGURE_COUNT = FIGURE_COUNT + 1
	plt.figure(FIGURE_COUNT)
	plt.xlabel('Service')
	plt.title(typ + ' Score')
	plt.ylabel(typ + ' Score')
	plt.plot(data1, lineType1, label=label1+' '+nodeName1)
	plt.plot(data2, lineType2, label=label2+' '+nodeName2)
	ax = plt.gca()
	ax.legend(loc = "lower right")

def calculateVariance(data, label, pos=-1):
	nodes, scores = parseScore(data, pos)
	narray = np.array(scores)
	sum1 = narray.sum()
	narray2 = narray * narray
	sum2 = narray2.sum()
	mean = sum1 / len(scores)
	var = sum2 / len(scores) - mean ** 2
	stdVar = math.sqrt(var)
	print "[" + label + "]: Mean = " + str(mean) + " Variance = " + str(var) + " Standard = " + str(stdVar)
	return mean, stdVar

def compareVariance(data1, data2, pos=-1):
	mean, stdVar = calculateVariance(data1, label1, pos)
	meanList1.append(mean)
	stdVarList1.append(stdVar)
	mean, stdVar = calculateVariance(data2, label2, pos)
	meanList2.append(mean)
	stdVarList2.append(stdVar)

def plotCompare(data1, data2, pos=-1):
	global FIGURE_COUNT
	FIGURE_COUNT = FIGURE_COUNT + 1

	plt.figure(FIGURE_COUNT)
	if pos == -1:
		ser_cnt = len(data1['slave1-1']['score'])
	else:
		ser_cnt = pos + 1
	plt.title('Placement Quality\n' + "Service Count = " + str(ser_cnt))
	plt.xlabel('Node')
	plt.ylabel('Load')
	nodes, scores = parseScore(data1, pos)
	print label1
	print scores
	
	ax = plt.gca()
	ax.set_xticks(np.linspace(0, 11, len(nodes)))
	ax.set_xticklabels(nodes)

	max_y= max(scores)
	max_x = scores.index(max_y)
	upper = max_y
	lower = min(scores)
	plt.annotate('SwarmKit PQ = ' + str(round(max_y, 2)), xy=(max_x,max_y), xytext=(max_x+0.5, max_y+8), arrowprops=dict(facecolor='black', shrink=0.001))
	plt.plot(scores, lineType1, label=label1)

	nodes, scores = parseScore(data2, pos)
	print label2
	print scores
	max_y= max(scores)
	max_x = scores.index(max_y)
	if max_y > upper:
		upper = max_y
	if min(scores) < lower:
		lowe = min(scores)
	plt.annotate('Datexla PQ = ' + str(round(max_y, 2)), xy=(max_x,max_y), xytext=(max_x+0.5, max_y+8), arrowprops=dict(facecolor='black', shrink=0.001))
	plt.ylim(lower * 0.9, upper * 1.1)
	plt.plot(scores, lineType2, label=label2)
	plt.grid()
	ax.legend(loc = "lower right")

def parseScore(data, pos=-1):
	scores = []
	nodes = []
	for item in data:
		nodes.append(item)
		scores.append(data[item]["score"][pos])
	scores = [x for (y, x) in sorted(zip(nodes, scores))]
	nodes.sort()
	return nodes, scores

def plotCMT(mode, nodeName1, nodeName2):
	plotSingle(scoreDict1[nodeName1]["cpuScore"], scoreDict2[nodeName2]["cpuScore"], nodeName1, nodeName2, 'CPU')
	plotSingle(scoreDict1[nodeName1]["memScore"], scoreDict2[nodeName2]["memScore"], nodeName1, nodeName2, 'Memory')
	plotSingle(scoreDict1[nodeName1]["score"], scoreDict2[nodeName2]["score"], nodeName1, nodeName2, 'Total')

	plt.savefig(nodeName1 + " vs " + nodeName2 + '.jpg')

def PltCalcCompare(data1, data2, pos=-1):
	if pos == -1:
		print "\nService Count = " + str(len(data1['slave1-1']['score']))
	else:
		print "\nService Count = " + str(pos+1)
	plotCompare(scoreDict1, scoreDict2, pos)
	compareVariance(scoreDict1, scoreDict2, pos)

def plotErrBar(x, y1, errorY1, y2, errorY2, serviceLabel):
	global FIGURE_COUNT
	FIGURE_COUNT = FIGURE_COUNT + 1

	plt.figure(FIGURE_COUNT)
	
	mean_values = y1
	variance = errorY1
	
	ax = plt.gca()

	plt.bar(x-0.15, y1, width=0.3, yerr=errorY1, align='center', color='b', alpha=0.6, label=label1, error_kw={'linewidth':2})
	plt.bar(x+0.15, y2, width=0.3, yerr=errorY2, align='center', color='r', alpha=0.6, label=label2, error_kw={'linewidth':2})

	max_y = max(zip(mean_values, variance))
	#plt.ylim([0, (max_y[0] + max_y[1]) * 1.1])
	 
	plt.ylabel('System Score')
	plt.xlabel('Service Count')

	x_pos = np.arange(len(serviceLabel))
	plt.xticks(x_pos, serviceLabel)

	plt.title('Load Balance Degree')
	ax.legend(loc = "upper left")

	plt.grid()

def plotSysPQ(data1, data2, category):
	tit = ''
	if category == 'score':
		tit = 'Total'
	elif category == 'cpuScore':
		tit = 'CPU'
	elif category == 'memScore':
		tit = 'Memory'

	nodes = []
	for item in data1:
		nodes.append(item)

	ser_cnt1 = len(data1["slave1-1"]["score"])
	ser_cnt2 = len(data2["slave1-1"]["score"])
	ser_cnt = min(ser_cnt1, ser_cnt2)
	
	pq1, pq2 = [], []

	for i in range(0, ser_cnt-1):
		max_s1, max_s2 = -1, -1
		for node in nodes:
			s1 = data1[node][category][i]
			s2 = data2[node][category][i]
			if s1 > max_s1:
				max_s1 = s1
			if s2 > max_s2:
				max_s2 = s2
		pq1.append(max_s1)
		pq2.append(max_s2)
   
	global FIGURE_COUNT
	FIGURE_COUNT = FIGURE_COUNT + 1
	plt.figure(FIGURE_COUNT)
	
	ax = plt.gca()
	plt.plot(pq1, lineType1, label='SwarmKit')
	plt.plot(pq2, lineType2, label='Datexla')
	plt.xlabel('Service')
	plt.ylabel('Score')
	plt.title('System Placement Quality (' + tit + ')')
	ax.legend(loc = "lower right")

	if category == "score":
		print pq1
		print pq2

def main():
	fileName1, fileName2 = '', ''
	mode = 0

	if len(sys.argv) == 3:
		fileName1 = sys.argv[1]
		fileName2 = sys.argv[2]
		mode = 2
	elif len(sys.argv) == 2:
		fileName1 = sys.argv[1]
		mode = 1
	else:
		print('Usage: ' + sys.argv[0] + ' logFile')
		exit(1)

	global scoreDict1
	scoreDict1 = readFile(fileName1)
	global label1
	label1 = fileName1.split('.')[0]
	if mode == 2:
		global scoreDict2
		scoreDict2 = readFile(fileName2)
		global label2
		label2 = fileName2.split('.')[0]

	# plotCMT(mode, "slave1-2", "tor1")

	serviceCnt = len(scoreDict1["slave1-1"]["score"])
	curr_ser_id = serviceCnt / 8
	PltCalcCompare(scoreDict1, scoreDict2, curr_ser_id)
	curr_ser_id = serviceCnt / 3
	PltCalcCompare(scoreDict1, scoreDict2, curr_ser_id)
	curr_ser_id = serviceCnt / 2
	PltCalcCompare(scoreDict1, scoreDict2, curr_ser_id)
	PltCalcCompare(scoreDict1, scoreDict2)

	serviceId = [serviceCnt / 8 + 1, serviceCnt / 3 + 1, serviceCnt / 2 + 1, serviceCnt]
	plotErrBar(np.arange(len(meanList1)), meanList1, stdVarList1, meanList2, stdVarList2, serviceId)

	plotSysPQ(scoreDict1, scoreDict2, "cpuScore")
	plotSysPQ(scoreDict1, scoreDict2, "memScore")
	plotSysPQ(scoreDict1, scoreDict2, "score")

	plt.show()

	serviceCnt1 = len(scoreDict1["slave1-1"]["score"])
	print serviceCnt1
	serviceCnt2 = len(scoreDict2["slave1-1"]["score"])
	print serviceCnt2

if __name__ == '__main__':
	main()
