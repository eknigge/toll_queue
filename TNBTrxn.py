import os
import pandas as pd
import datetime
import csv


class Transaction:
	"""
	"""
	_dateTime = None
	_pmtTyp = None
	_axel = None
	_processing_time = None
	_time_remaining = None
	_complete = False
	_trxID = None
	datetime_second = datetime.timedelta(seconds=1)

	def __init__(self, dateTime_created,pmtTyp,axel, trxID):
		self._dateTime = dateTime_created
		self._axel = axel
		self._time_remaining = datetime.timedelta(seconds=0)
		self.setPmtTyp(pmtTyp)
		self._trxID = trxID

	def setProcessingTimeLane(self, datetime_value):
		if datetime_value == None:
			raise ValueError('Invalid value')
		self._time_remaining = datetime_value
		self._processing_time = datetime_value

	def getTrxID(self):
		return self._trxID

	def getAxels(self):
		return self._axel

	def advanceTimeTrxn(self):
		self.setTimeRemaining(self.getTimeRemaining() - self.datetime_second)
		if self.getTimeRemaining() <= datetime.timedelta(seconds=0):
			isComplete = True

	def isComplete(self):
		return self._complete

	def getTyp(self):
		return self._pmtTyp

	def getDateTime(self):
		return self._dateTime

	def setPmtTyp(self, pmtTyp):
		if pmtTyp not in Util().getLaneTypes():
			raise ValueError
		self._pmtTyp = pmtTyp

	def getTimeRemaining(self):
		return self._time_remaining

	def setTimeRemaining(self, datetime):
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
		out += 'Axels: ' + str(self.getAxels()) + '\n'
		return out





class Lane:
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
		out = datetime.timedelta(seconds=0)
		for i in self._queue:
			out += i.getTimeRemaining()
		return out


	def setProcessingTime(self, transaction):
		"""
		Get processing time for various types of transactions. Varies
		based on whether transaction type matches lane type.
		:param pmtTyp: Type of payment
		:param datetime.datetime object for remaining processing time
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
		self._laneID = laneID

	def getLaneID(self):
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
		return self._queue

	def getQueueLength(self):
		return len(self._queue)

	def processingTimeCashGen(self):
		return datetime.timedelta(seconds=1)

	def processingTimeCreditGen(self):
		return datetime.timedelta(seconds=1)

	def processingTimeCreditInCreditLane(self):
		return datetime.timedelta(seconds=1)

	def processingTimeETCInETCLane(self):
		return datetime.timedelta(seconds=1)

	def processingTimeMailGen(self):
		return datetime.timedelta(seconds=1)

	def processingTimeETCGen(self):
		return datetime.timedelta(seconds=1)

	def setLaneType(self, lane_type):
		if lane_type not in Util().getLaneTypes():
			raise ValueError('Invalid Value, does not match existing lane type')
		else:
			self._lane_type = lane_type

	def getLaneType(self):
		return self._lane_type

	def addTransaction(self, transaction):
		if type(transaction) is not Transaction:
			raise TypeError('Invalid input type')
		else:
			self.setProcessingTime(transaction)
			self._queue.append(transaction)
	
class Facility:
	_start_time = None
	_current_time = None
	_total_queue = None
	_queue_by_lane = {}
	_all_lanes = []
	_trxID_counter = 0

	def	__init__(self, start_time):
		self.setStartTime(start_time)

	def addLane(self, lane):
		if type(lane) is not Lane:
			raise TypeError('Incorrect type')
		elif lane in self._all_lanes:
			raise ValueError('Lane already exists in system')
		else:
			self._all_lanes.append(lane)

	def advanceTimeFacility(self):
		#advance time for facility
		self._current_time = self._current_time + datetime.timedelta(seconds=1)

		#advance time for each transaction
		for lane in self._all_lanes:
			for j in lane._queue:
				j.advanceTimeTrxn()
				if j.isComplete():
					lane.remove(j)

	def addTransaction(self, transaction):
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
		values = _queue_by_lane.values()
		output = 0

		for i in values:
			output += i
		return output

	def queueByLane(self):
		for lane in self._all_lanes:
			self._queue_by_lane[lane.getLaneID()] = lane.getQueueLength()

	def getNewTrxID():
		out = self._trxID_counter
		self._trxID_counter += 1
		return out

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
		return self._lane_types

	#create plot from Facility queueByLane method

	def getTransactionsToAdd(self, dataframe, datetime):
		df = dataframe
		df = df[df['trans date/time'] < datetime]
		return df

	def addTransactionsFromDataframe(self, Facility, dataframe):
		df = dataframe
		n = df.shape[0]
		for i in range(n):
			df_row = df.iloc[i]
			new_transaction = Transaction(df_row[0], df_row[2], df_row[3], i)
			Facility.addTransaction(new_transaction)



all_files = os.listdir(os.getcwd())
filename = '01012018.csv'

df = pd.read_csv(filename)
df['trans date/time'] = pd.to_datetime(df['trans date/time'])
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

for i in range(10):
	print(test_facility)
	test_facility.advanceTimeFacility()
