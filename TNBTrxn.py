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

	def __init__(self, dateTime,pmtTyp,axel, trxID):
		self._dateTime = dateTime
		self._axel = axel
		self.setPmtTyp(pmtTyp)
		self._trxID = trxID

	def setProcessingTime(self, datetime):
		if type(datetime) is not datetime:
			print('Invalid Input Type')
			raise TypeError
		self._dateTime = datetime
		self._time_remaining = datetime

	def getTrxID(self):
		return self._trxID

	def getAxels(self):
		return self._axel

	def advanceClock(self):
		self.setTimeRemaining(self.getTimeRemaining() - datetime_second)
		if self.getTimeRemaining() <= 0:
			isComplete = True

	def isComplete(self):
		return _complete

	def getTyp(self):
		return self._pmtTyp

	def getDateTime(self):
		return self._dateTime

	def setPmtTyp(self, pmtTyp):
		if pmtTyp not in Util().getLaneTypes():
			raise ValueError
		self._pmtTyp = pmtTyp

	def getTimeRemaining(self):
		return _time_remaining

	def setTimeRemaining(self, datetime):
		if type(datetime) is not datetime:
			print('Invalid Input Type')
			raise TypeError
		self._time_remaining = datetime
	def __str__(self):
		out = ''
		out += 'Transaction Information ' + '\n'
		out += 'TrxID: ' + str(self.getTrxID()) + '\n'
		out += 'Start Time: ' + str(self.getDateTime()) + '\n'
		out += 'Payment Type: ' + str(self.getTyp()) + '\n'
		out += 'Axels: ' + str(self.getAxels()) + '\n'
		return out





class Lane:
	_queue = []
	_lane_type = None
	_laneID = None

	def __init__(self, laneID, lane_type = 'GEN'):
		self.setLaneType(lane_type)
		self.setLaneID(laneID)
		

	def setProcessingTime(self, Transaction):
		"""
		Get processing time for various types of transactions. Varies
		based on whether transaction type matches lane type.
		:param pmtTyp: Type of payment
		:param datetime.datetime object for remaining processing time
		:raises TypeError: Transaction Class Type Required
		"""

		if type(Transaction) is not Transaction:
			print('Invalid Input')
			raise TypeError

		#credit in credit lane
		elif Transaction.getTyp() == 'CC' and self.getLaneType() == 'CC':
			Transaction.setProcessingTime(processingTimeCreditInCreditLane())

		#tag only lane
		elif Transaction.getTyp() == 'ETC' and self.getLaneType() == 'ETC':
			Transaction.setProcessingTime(processingTimeETCInETCLane())

		#cash in general lane
		elif Transaction.getTyp() == 'CASH' and self.getLaneType() == 'GEN':
			Transaction.setProcessingTime(processingTimeCashGen())

		#credit in general lane
		elif Transaction.getTyp() == 'CC' and self.getLaneType() == 'GEN':
			Transaction.setProcessingTime(processingTimeCreditGen())

		#pay-by mail general
		elif Transaction.getTyp() == 'PMB' and self.getLaneType() == 'GEN':
			Transaction.setProcessingTime(processingTimeMailGen())

		#tag general lane
		elif Transaction.getTyp() == 'ETC' and self.getLaneType() == 'GEN':
			Transaction.setProcessingTime(processingTimeETCGen())

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
		return out

	def getQueue(self):
		return self._queue

	def getQueueLength(self):
		return len(self._queue)


	def processingTimeCashGen(self):
		pass
	def processingTimeCreditGen(self):
		pass
	def processingTimeCreditInCreditLane(self):
		pass
	def processingTimeETCInETCLane(self):
		pass
	def processingTimeMailGen(self):
		pass
	def processingTimeETCGen(self):
		pass
	def setLaneType(self, lane_type):
		if lane_type not in Util().getLaneTypes():
			print('Invalid Value, does not match existing lane type')
			raise ValueError
		else:
			self._lane_type = lane_type
	def getLaneType(self):
		return self._lane_type
	def addTransaction(self, Transaction):
		if Transaction is not Transaction:
			print('Invalid input type')
			raise TypeError
		else:
			self._queue.append(Transaction)
	
class Facility:
	_start_time = None
	_total_queue = None
	_queue_by_lane = {}
	_trxID_counter = 0

	def	__init__(self, start_time):
		self.setStartTime(start_time)

	def addLane(self, lane):
		if type(lane) is not Lane:
			raise TypeError
		elif lane.getLaneID() in self._queue_by_lane:
			print('Lane ID already exists')
			raise ValueError
		self._queue_by_lane[lane.getLaneID()] = lane.getQueueLength()

	def addTransaction():
		pass
	def totalQueue():
		pass
	def queueByLane():
		pass
	def getNewTrxID():
		out = self._trxID_counter
		self._trxID_counter += 1
		return out
	def setStartTime(self, start_time):
		self._start_time = start_time
	def getStartTime(self):
		return self._start_time
	def __str__(self):
		out = ''
		out += 'Facility Information' + '\n'
		out += 'Start Time: ' + str(self.getStartTime()) + '\n'
		for n, i in enumerate(self._queue_by_lane):
			out += 'Lane ' + str(i) + ': ' + str(self._queue_by_lane[i])
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

all_files = os.listdir(os.getcwd())
filename = '01012018.csv'

df = pd.read_csv(filename)
df['trans date/time'] = pd.to_datetime(df['trans date/time'])
print(Util().getLaneTypes())
print(df.head(5))
item = df.iloc[1].tolist()

test_trxn = Transaction(item[0],item[2],item[3], 1)
print(test_trxn)

new_lane = Lane(1,'GEN')
new_lane.addTransaction(test_trxn)
print(new_lane)

start_time = datetime.datetime.now()
test_facility = Facility(start_time)
test_facility.addLane(new_lane)

print(test_facility)
