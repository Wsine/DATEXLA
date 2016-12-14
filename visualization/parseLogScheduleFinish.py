import sys, re, time
import matplotlib.pyplot as plt
from datetime import datetime

TAGS = ('service come', 'schedule finish')

def readFile(fileName):
	finishDict = {}
	# Read logs from log file
	with open(fileName) as logFile:
		# ignore the last empty line
		for line in logFile.readlines()[:-1]:
			log = re.split('[\[\]]*', line)
			timestamp = log[0].strip()
			tag = re.sub('\s+', ' ', log[1].strip())
			content = log[2].strip()
			if tag == 'service come':
				serviceID = content.split(',')[0].split()[1]
				timeCome = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
				finishDict[serviceID] = {"start": timeCome}
			elif tag == 'schedule finish':
				serviceID = content.split(',')[0].split()[1]
				timeFinish = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
				if serviceID in finishDict:
					finishDict[serviceID]["end"] = timeFinish
	return finishDict

def calcScheduleTime(dictionary, reversedd=False):
	timeList = []
	tuplee = sorted(dictionary.items(), key=lambda item:item[1]["start"], reverse=reversedd)
	for item in tuplee:
		value  = item[1]
		if "end" in value:
			start = value["start"]
			end = value["end"]
			elapsed = end - start
			timeList.append(elapsed.total_seconds())
	return timeList

def plot(data):
	plt.title('DATEXLA Response Time')
	plt.xlabel('Service')
	plt.ylabel('Response Time(s)')
	plt.ylim(0, 10)
	plt.plot(data, 'o--')
	plt.show()

def main():
	if len(sys.argv) < 2:
		print('Usage: ' + sys.argv[0] + ' logFile')
		exit(1)
	fileName = sys.argv[1]
	finishDict = readFile(fileName)
	timeList = calcScheduleTime(finishDict)
	plot(timeList)

if __name__ == '__main__':
	main()