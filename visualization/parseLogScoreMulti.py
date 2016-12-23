from __future__ import print_function
import sys, re, time, os.path
import matplotlib.pyplot as plt

FIGURE_COUNT = 0

def readFile(fileNames):
	scoreDicts = []
	# Read logs from log files
	for fileName in fileNames:
		scoreDict = {}
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
		scoreDicts.append(scoreDict)
	return scoreDicts

def parseArgv():
	fileNames = []
	argvLen = len(sys.argv)
	if argvLen < 2:
		print('Usage: ' + sys.argv[0] + ' logFiles...')
		exit(1)
	for i in range(argvLen)[1:]:
		if not os.path.exists(sys.argv[i]):
			print(sys.argv[i] + " does not exist...")
			exit(1)
		fileNames.append(sys.argv[i])
	return fileNames

def main():
	fileNames = parseArgv()
	scoreDicts = readFile(fileNames)
	labels = map(lambda x: x.split('.')[0], fileNames)


if __name__ == '__main__':
	main()
