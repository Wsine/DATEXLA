import sys,re
import matplotlib.pyplot as plt

markSty = ['.','o','+','*']
lineSty = ['-','--','-.',':']
colorSty = ['b','g','r','c']

FIGURE_COUNT = 0

def parseTime(s):
	t = re.split(':',s[11:-1]) 
	sec = float(t[0])*3600 + float(t[1])*60 + float(t[-1])
	return sec
	
def readFile(fileName):
	serviceDict = {}
	with open(fileName) as logFile:
		st = {} 
		for line in logFile.readlines():
			log = re.split('\s',line)[:-1]
			if not log[1] in serviceDict:
				serviceDict[log[1]] = {"time":[0.0],"cpu":[log[2]],"mem":[log[3]],
				"net":[(log[4],log[5])],"block":[(log[6],log[7])]}
				st[log[1]] = parseTime(log[0])
			else:
				serviceDict[log[1]]["time"].append(parseTime(log[0])-st[log[1]])
				serviceDict[log[1]]["cpu"].append(log[2])
				serviceDict[log[1]]["mem"].append(log[3])
				serviceDict[log[1]]["net"].append((log[4],log[5]))
				serviceDict[log[1]]["block"].append((log[6],log[7]))
	return  serviceDict

def plotPerLog(ty,log):
	global FIGURE_COUNT
	plt.figure(FIGURE_COUNT)
	FIGURE_COUNT = FIGURE_COUNT + 1
	plt.title(ty + ' usage')
	plt.xlabel('sec')
	plt.ylabel(ty + ' usage(%)')
	#plt.ylim(0,400)
	for (idx,task) in enumerate(log.keys()):
		plt.plot(log[task]["time"][1:],log[task][ty][1:],colorSty[idx]+lineSty[0],label=task)
	plt.legend()

def plotIOLog(ty,log):
	global FIGURE_COUNT
	plt.figure(FIGURE_COUNT)
	FIGURE_COUNT = FIGURE_COUNT + 1
	plt.title(ty + ' IO')
	plt.xlabel('sec')
	plt.ylabel(ty + ' IO(Bytes)')
	for (idx,task) in enumerate(log.keys()):
		ins = []
		outs = []
		for io in log[task][ty]:
			ins.append(io[0])
			outs.append(io[1])
		plt.plot(log[task]["time"][1:],ins[1:],colorSty[idx]+lineSty[0],label=task + '_in')
		plt.plot(log[task]["time"][1:],outs[1:],colorSty[idx]+lineSty[1],label=task + '_out')
	plt.legend()

def main():
	if len(sys.argv) < 2:
		print('Usage: ' + sys.argv[0] + ' logFile')
		exit(1)
	fileName = sys.argv[1]
	serviceDict = readFile(fileName)
	plotPerLog("cpu",serviceDict)
	plotPerLog("mem",serviceDict)
	plotIOLog("net",serviceDict)
	plotIOLog("block",serviceDict)
	plt.show()

if __name__ == '__main__':
	main()