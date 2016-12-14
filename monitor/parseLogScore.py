import sys, re, time
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

FIGURE_COUNT = 0

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

def plotCPU(name, data):
	global FIGURE_COUNT
	FIGURE_COUNT = FIGURE_COUNT + 1
	plt.figure(FIGURE_COUNT)
	plt.title(name + ' CPU Score')
	plt.xlabel('Service')
	plt.ylabel('CPU Score')
	# plt.ylim(0, 10)
	plt.plot(data, 'o--')

def plotMEM(name, data):
	global FIGURE_COUNT
	FIGURE_COUNT = FIGURE_COUNT + 1
	plt.figure(FIGURE_COUNT)
	plt.title(name + ' Memory Score')
	plt.xlabel('Service')
	plt.ylabel('Memory Score')
	# plt.ylim(0, 10)
	plt.plot(data, 'o--')

def plotTotal(name, data):
	global FIGURE_COUNT
	FIGURE_COUNT = FIGURE_COUNT + 1
	plt.figure(FIGURE_COUNT)
	plt.title(name + ' Total Score')
	plt.xlabel('Service')
	plt.ylabel('Total Score')
	# plt.ylim(0, 10)
	plt.plot(data, 'o--')

def plotCompare(data):
	global FIGURE_COUNT
	FIGURE_COUNT = FIGURE_COUNT + 1
	plt.figure(FIGURE_COUNT)
	plt.title('Compare Score')
	plt.xlabel('Node')
	plt.ylabel('Score')
	# plt.ylim(0, 10)
	nodes, scores = parseLastScore(data)
	ax = plt.gca()
	ax.set_xticks(np.linspace(0, 2, len(nodes)))
	ax.set_xticklabels(nodes)
	plt.plot(scores, 'o--')

def parseLastScore(data):
	scores = []
	nodes = []
	for item in data:
		nodes.append(item)
		scores.append(data[item]["score"][-1])
	scores = [x for (y, x) in sorted(zip(nodes, scores))]
	nodes.sort()
	return nodes, scores

def main():
	if len(sys.argv) < 2:
		print('Usage: ' + sys.argv[0] + ' logFile')
		exit(1)
	fileName = sys.argv[1]
	scoreDict = readFile(fileName)
	plotCPU("Slave3-1", scoreDict["slave3-1"]["cpuScore"])
	plotMEM("Slave3-1", scoreDict["slave3-1"]["memScore"])
	plotTotal("Slave3-1", scoreDict["slave3-1"]["score"])
	plotCompare(scoreDict)
	plt.show()

if __name__ == '__main__':
	main()