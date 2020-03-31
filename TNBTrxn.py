import os
import pandas as pd
import datetime
import csv
import matplotlib.pyplot as plt
import numpy as np
import shutil
import cv2
from cv2 import VideoWriter, VideoWriter_fourcc


class Transaction:
	"""
	Toll transactions utilized in Lane and Facility classes. 

	:param dateTime_created: start time in datetime format for the transaction
	:param pmtTyp: payment type of transaction
	:param axel: number of vehicle axles
	:param trxID: transaction ID
	"""
	_dateTime = None
	_pmtTyp = None
	_axel = None
	_processing_time = None
	_time_remaining = None
	_complete = False
	_trxID = None
	datetime_second = datetime.timedelta(seconds=1)

	def __init__(self, dateTime_created, pmtTyp, axel, trxID):
		self._dateTime = dateTime_created
		self._axel = axel
		self._time_remaining = datetime.timedelta(seconds=0)
		self.setPmtTyp(pmtTyp)
		self._trxID = trxID

	def setProcessingTimeLane(self, datetime_value):
		"""
		Set value of the remaining time and processing time
		:param datetime_value: datetime object
		"""
		if datetime_value == None:
			raise ValueError('Invalid value')
		self.setTimeRemaining(datetime_value)
		self._processing_time = datetime_value

	def getTrxID(self):
		"""
		Returns transaction ID
		"""
		return self._trxID

	def getAxels(self):
		"""
		Returns axel count

		:returns: int
		"""
		return self._axel

	def advanceTimeTrxn(self):
		"""
		Advance transaction processing time by one second
		"""
		self.setTimeRemaining(self.getTimeRemaining() - self.datetime_second)
		if self.getTimeRemaining() <= datetime.timedelta(seconds=0):
			self._complete = True

	def isComplete(self):
		"""
		Whether transaction has been processed 
		:returns: boolean 
		"""
		return self._complete

	def getTyp(self):
		"""
		Returns transaction type
		:returns: String transaction type
		"""
		return self._pmtTyp

	def getDateTime(self):
		"""
		Returns when date when transaction was created
		:returns: datetime object
		"""
		return self._dateTime

	def setPmtTyp(self, pmtTyp):
		"""
		Set payment type
		:param pmtTyp: String of valid payment type
		"""
		if pmtTyp not in Util().getLaneTypes():
			raise ValueError
		self._pmtTyp = pmtTyp

	def getTimeRemaining(self):
		"""
		:returns: datetime object of time remaining
		"""
		return self._time_remaining

	def setTimeRemaining(self, datetime):
		"""
		Set payment type with datetime object
		:param datetime: datetime object
		"""

		######
		# add TypeError check for datetime or datetime.timedelta
		######
		#if type(datetime) is not datetime or type(datetime) is not datetime.timedelta:
		#	raise TypeError('Invalid Input Type')
		self._time_remaining = datetime

	def __str__(self):
		out = ''
		out += 'Transaction Information ' + '\n'
		out += 'TrxID: ' + str(self.getTrxID()) + '\n'
		out += 'Start Time: ' + str(self.getDateTime()) + '\n'
		out += 'Time Remaining: ' + str(self._time_remaining) + '\n'
		out += 'Payment Type: ' + str(self.getTyp()) + '\n'
		out += 'Complete: ' + str(self._complete) + '\n'
		out += 'Axels: ' + str(self.getAxels()) + '\n'
		return out





class Lane:
	"""
	Lane used to for queueing transactions and as a componenent of Facility class.

	:param landID: unique lane ID number
	:param lane_type: String of lane type, must be contained in Util types 
	"""
	_queue = []
	_lane_type = None
	_laneID = None

	def __init__(self, laneID, lane_type):
		self._queue = []
		self._lane_type = None
		self._laneID = None

		self.setLaneType(lane_type)
		self.setLaneID(laneID)
		

	def getWaitTime(self):
		"""
		Uses current lane queue to calculate wait time

		:returns: datetime.timedelta object with wait time for lane
		"""
		out = datetime.timedelta(seconds=0)
		for i in self._queue:
			out += i.getTimeRemaining()
		return out


	def setProcessingTime(self, transaction):
		"""
		Set processing time for various types of transactions. Matches
		processing time to transaction and lane type. 

		:param transaction: Transaction object
		:returns: None
		:raises TypeError: Transaction Class Type Required
		"""

		if type(transaction) is not Transaction:
			raise TypeError('Invalid Input')


		#credit in credit lane
		elif transaction.getTyp() == 'CC' and self.getLaneType() == 'CC':
			transaction.setProcessingTimeLane(self.processingTimeCreditInCreditLane())

		#tag only lane
		elif transaction.getTyp() == 'ETC' and self.getLaneType() == 'ETC':
			transaction.setProcessingTimeLane(self.processingTimeETCInETCLane())

		#cash in general lane
		elif transaction.getTyp() == 'CASH' and self.getLaneType() == 'GEN':
			transaction.setProcessingTimeLane(self.processingTimeCashGen())

		#credit in general lane
		elif transaction.getTyp() == 'CC' and self.getLaneType() == 'GEN':
			transaction.setProcessingTimeLane(self.processingTimeCreditGen())

		#pay-by mail general
		elif transaction.getTyp() == 'PMB' and self.getLaneType() == 'GEN':
			transaction.setProcessingTimeLane(self.processingTimeMailGen())

		#tag general lane
		elif transaction.getTyp() == 'ETC' and self.getLaneType() == 'GEN':
			transaction.setProcessingTimeLane(self.processingTimeETCGen())

	def setLaneID(self,laneID):
		"""
		Set lane ID
		"""
		self._laneID = laneID

	def getLaneID(self):
		"""
		:returns: laneID
		"""
		return self._laneID

	def __str__(self):
		out = ''
		out += 'Lane Information' + '\n'
		out += 'Lane ID: ' + str(self.getLaneID()) + '\n'
		out += 'Lane Type: ' + str(self.getLaneType()) + '\n'
		out += 'Queue Length: ' + str(len(self.getQueue())) + '\n'
		out += '\n'
		return out

	def getQueue(self):
		"""
		:returns: list of Transaction objects
		"""
		return self._queue

	def getQueueLength(self):
		"""
		:returns: int of queue length
		"""
		return len(self._queue)

	def processingTimeCashGen(self):
		"""
		Calculates processing time for cash in general purpose 
		manual toll lane. Utilizes normal probaility distribution.  

		:returns: datetime.timedelta object with processing time in seconds 
		"""
		return datetime.timedelta(seconds=15)

	def processingTimeCreditGen(self):
		"""
		Calculates processing time for credit in general purpose 
		manual toll lane. Utilizes normal probaility distribution.  

		:returns: datetime.timedelta object with processing time in seconds 
		"""
		return datetime.timedelta(seconds=15)

	def processingTimeCreditInCreditLane(self):
		"""
		Calculates processing time for credit in credit-only manual toll lane.
		Utilizes normal probaility distribution.  

		:returns: datetime.timedelta object with processing time in seconds 
		"""
		return datetime.timedelta(seconds=15)

	def processingTimeETCInETCLane(self):
		"""
		Calculates processing time for ETC in manual toll lane.
		Utilizes normal probaility distribution.  

		:returns: datetime.timedelta object with processing time in seconds 
		"""
		return datetime.timedelta(seconds=15)

	def processingTimeMailGen(self):
		"""
		Calculates processing time for pay-by-mail transaction in manual toll lane.
		Utilizes normal probaility distribution.  

		:returns: datetime.timedelta object with processing time in seconds 
		"""
		return datetime.timedelta(seconds=15)

	def processingTimeETCGen(self):
		"""
		Calculates processing time for ETC in general purpose manual toll lane.
		Utilizes normal probaility distribution.  

		:returns: datetime.timedelta object with processing time in seconds 
		"""
		return datetime.timedelta(seconds=15)

	def setLaneType(self, lane_type):
		"""
		Set lane type 

		:param lane_type: String, valid lane type
		"""
		if lane_type not in Util().getLaneTypes():
			raise ValueError('Invalid Value, does not match existing lane type')
		else:
			self._lane_type = lane_type

	def getLaneType(self):
		"""
		:returns: lane type
		"""
		return self._lane_type

	def addTransaction(self, transaction):
		if type(transaction) is not Transaction:
			raise TypeError('Invalid input type')
		else:
			self.setProcessingTime(transaction)
			self._queue.append(transaction)
	
class Facility:
	"""
	Facility consits of several Lanes, lanes queue transactions.
	The *start_time* provided is the start of the simulation.


	:param start_time: datetime object 
	"""
	_start_time = None
	_current_time = None
	_total_queue = None
	_queue_by_lane = {}
	_all_lanes = []
	_trxID_counter = 0

	def	__init__(self, start_time):
		self.setStartTime(start_time)

	def addLane(self, lane):
		"""
		Add Lane to Facility

		:param lane: Lane object
		"""
		if type(lane) is not Lane:
			raise TypeError('Incorrect type')
		elif lane in self._all_lanes:
			raise ValueError('Lane already exists in system')
		else:
			self._all_lanes.append(lane)

	def advanceTimeFacility(self):
		"""
		Advance time one second for transactions being processed 
		and for facility time. 
		"""
		#advance time for facility
		self._current_time = self._current_time + datetime.timedelta(seconds=1)

		#advance time for first transaction in lane
		#remove transaction if complete
		for lane in self._all_lanes:
			try:
				lane._queue[0].advanceTimeTrxn()
				if lane._queue[0].isComplete():
					lane._queue.remove(lane._queue[0])
			except IndexError:
				pass

	def addTransaction(self, transaction):
		"""
		Add transaction to facility. Transaction is added to shortest
		eligible queue. For example, credit card transaction may utilize
		a credit-only lane or general purpose manual toll lane, but will 
		always choose the line with the shortest wait time.

		:param transaction: Transaction object
		"""
		if type(transaction) is not Transaction:
			raise TypeError('Incorrect type')

		#create list with matching lane type or GEN lane
		possible_lane = []
		for i in self._all_lanes:
			if i.getLaneType() == transaction.getTyp() or\
					i.getLaneType() == 'GEN':
						possible_lane.append(i)
				
		#raise error if no matching lane
		if len(possible_lane) == 0:
			raise ValueError('No applicable lane to process trxn')

		#select the fastest lane 
		fastest_lane = possible_lane[0] #default to first lane in list
		for i in possible_lane:
			if i.getWaitTime() < fastest_lane.getWaitTime():
				fastest_lane = i

		#add to fastest lane
		fastest_lane.addTransaction(transaction)


	def totalQueue():
		"""
		:returns: int of total queue length
		"""
		values = _queue_by_lane.values()
		output = 0

		for i in values:
			output += i
		return output

	def queueByLane(self):
		for lane in self._all_lanes:
			self._queue_by_lane[lane.getLaneID()] = lane.getQueueLength()

	def getLaneQueue(self):
		"""
		:returns: Dictionary object with queue by lane
		"""
		self.queueByLane()
		return self._queue_by_lane

	def setStartTime(self, start_time):
		self._start_time = start_time
		self._current_time = start_time

	def getStartTime(self):
		return self._start_time

	def __str__(self):
		out = ''
		out += 'Facility Information' + '\n'
		out += 'Start Time: ' + str(self.getStartTime()) + '\n'
		out += 'Current Time: ' + str(self._current_time) + '\n'

		self.queueByLane()
		for n, i in enumerate(self._queue_by_lane):
			out += 'Lane ' + str(i) + ': ' + str(self._queue_by_lane[i]) + '\n'
		return out


class Util:
	"""
	Utility class with methods and fields to support Facility,
	Transaction, and Lane classes
	"""
	_lane_types = ['GEN','CC','ETC','CASH','PMB']


	def getLaneTypes(self):
		"""
		:returns: list of lane types
		"""
		return self._lane_types

	def getTransactionsToAdd(self, dataframe, datetime_value):
		"""
		Filters dataframe for elegible transactions 
		to add to a Facility.  

		:param dataframe: dataframe object
		:param datetime_value: datetime value for filtering dataframe
		:returns: dataframe of transaction to add
		"""
		df = dataframe
		df = df[(df['trans date/time'] < datetime_value)]
		return df

	def addTransactionsFromDataframe(self, facility, dataframe):
		"""
		Add elegible transactions from dataframe to Facility

		:param facility: Facility object to add transaction
		:param dataframe: dataframe of transactions to add
		"""
		df = dataframe
		n = df.shape[0]
		for i in range(n):
			df_row = df.iloc[i]
			new_transaction = Transaction(df_row[0], df_row[2], df_row[3], i)
			facility.addTransaction(new_transaction)

	def plotLaneQueues(self, lane_list, lane_queue_dict, simulation_time):
		"""
		Plot lane queues

		:param lane_list: list of lanes
		:param lane_queue_dict: dictionary of lanes and queue length
		:param simulation_time: datetime object when data generated
		:returns: outputs png file
		"""
		######
		# need to add value validation to this method
		######
		lanes = lane_list
		data = lane_queue_dict
		time = simulation_time

		#get labels
		labels = []
		for i in lanes:
			labels.append(int(i[0]))

		values = data.values()

		fig, ax = plt.subplots()
		ax.bar(labels, values)
		plt.title('Plaza Queue   ' + str(time))
		plt.ylim(0,100)
		ax.set_ylabel('Queue Length')
		ax.set_xlabel('Lane Number')

		#save fig
		name = self.fmtDate(time.year) + self.fmtDate(time.month) +\
				self.fmtDate(time.day) + 'T' + self.fmtDate(time.hour) +\
				self.fmtDate(time.minute) + self.fmtDate(time.second) +\
				'.png'
		plt.savefig(name)
		plt.close()

	def fmtDate(self, value):
		string = str(value)
		if(len(string) == 1):
			string = '0' + string
		return string

		



#Test simulation
if __name__ == '__main__':
	script_runtime_start = datetime.datetime.now()

	#simulation time represents, current time while running model 
	start_time = datetime.datetime(2018,1,1,hour = 0, minute = 0)
	simulation_time = start_time
	one_second = datetime.timedelta(seconds = 1)
	seconds_in_day = 60 * 60 * 24
	seconds_in_day = 60 * 3


	#import test data
	sample_data = '01012018.csv'
	df = pd.read_csv(sample_data)
	df['trans date/time'] = pd.to_datetime(df['trans date/time'])

	#create test facility
	test_facility = Facility(start_time)

	#add lanes
	lane_list = [ (1,'GEN'), (2,'GEN'), (3,'GEN'),\
			(4,'GEN'), (5,'GEN'), (6,'GEN') ]
	for i in lane_list:
		test_facility.addLane(Lane(i[0], i[1]))


	###################
	#main loop
	###################

	#animation directory setup
	all_files = os.listdir()
	if 'images' in all_files:
		shutil.rmtree('images')
	os.mkdir('images')
	os.chdir('images')


	#increment time for analysis day
	for i in range(seconds_in_day):
		print(i)

		#add transactions to facility 
		df_add = Util().getTransactionsToAdd(df, simulation_time)
		#remove added transactions from dataframe
		df = df.drop(df_add.index)
		Util().addTransactionsFromDataframe(test_facility, df_add)

		#create output graphic
		Util().plotLaneQueues(lane_list, test_facility.getLaneQueue(), simulation_time)

		#advance facility and simulation time
		simulation_time = simulation_time + one_second
		test_facility.advanceTimeFacility()

	#create video file
	width = 640
	height = 480
	FPS = 30
	seconds = seconds_in_day / 30
	seconds = 60 * 3

	fourcc = VideoWriter_fourcc(*'MP42')
	video = VideoWriter('test.avi', fourcc, float(FPS), (width, height))

	img_files = os.listdir()
	for i in img_files:
		print(i)
		img = cv2.imread(i)
		video.write(img)
	video.release()

	#remove img files
	img_files = os.listdir()
	for i in img_files:
		if 'png' in i:
			os.remove(i)
	print('Runtime: ' + str(datetime.datetime.now() - script_runtime_start))

		



	"""
	OLD CODE

	print(df.head(15))
	item = df.iloc[1].tolist()
	item_2 = df.iloc[2].tolist()
	item_3 = df.iloc[3].tolist()
	item_4 = df.iloc[5].tolist()

	test_trxn = Transaction(item[0],item[2],item[3], 1)
	test_trxn_2 = Transaction(item_2[0],item_2[2],item_2[3], 2)
	test_trxn_3 = Transaction(item_3[0],item_3[2],item_3[3], 3)
	test_trxn_4 = Transaction(item_4[0],item_4[2],item_4[3], 5)

	new_lane = Lane(1,'GEN')
	new_lane_2 = Lane(2, 'GEN')
	new_lane_3 = Lane(3, 'ETC')

	#used to build facility and for plotting
	lane_list = [ (1, 'GEN'), (2, 'GEN'), (3, 'ETC')]


	start_time = datetime.datetime(2018,1,1,minute = 15)
	test_facility = Facility(start_time)

	test_facility.addLane(new_lane)
	test_facility.addLane(new_lane_2)
	test_facility.addLane(new_lane_3)
	test_facility.addTransaction(test_trxn_2)
	test_facility.addTransaction(test_trxn_3)

	#add ETC
	test_facility.addTransaction(test_trxn_4)



	df_small = Util().getTransactionsToAdd(df, start_time)
	df_small.to_csv('temp.csv')
	Util().addTransactionsFromDataframe(test_facility, df_small)

	test_facility.queueByLane()
	Util().plotLaneQueues(lane_list, test_facility.getLaneQueue(), start_time)

	test_facility.advanceTimeFacility()
	test_facility.queueByLane()
	print(test_facility.getLaneQueue())

	for i in range(15):
		test_facility.advanceTimeFacility()
		test_facility.queueByLane()
		Util().plotLaneQueues(lane_list, test_facility.getLaneQueue(), test_facility._current_time)

	seconds_gen = np.random.normal(loc = 15, scale = 3)
	print(seconds_gen)
	print(datetime.timedelta(seconds = seconds_gen))
	"""
