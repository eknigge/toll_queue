import os
import pandas as pd
import datetime

all_files = os.listdir(os.getcwd())
filename = '01012018.csv'

df = pd.read_csv(filename)
df['trans date/time'] = pd.to_datetime(df['trans date/time'])
print(df.head(5))

class Transaction:
	"""

	"""
	_dateTime = None
	_pmtTyp = None
	_axel = None
	_processing_time = None
	_time_remaining = None
	_complete = False
	datetime_second = datetime.timedelta(seconds=1)

	def __init__(self, dateTime,pmtTyp,axel):
		_dateTime = dateTime
		_axel = axel
		self.setPmtTyp(pmtTyp)

	def setProcessingTime(self, datetime):
		if type(datetime) is not datetime:
			print('Invalid Input Type')
			raise TypeError
		_dateTime = datetime
		_time_remaining = datetime

	def advanceClock(self):
		self.setTimeRemaining(self.getTimeRemaining() - datetime_second)
		if self.getTimeRemaining() <= 0:
			isComplete = True

	def isComplete(self):
		return _complete

	def getTyp(self):
		return _pmtTyp

	def setPmtTyp(self, pmtTyp):
		if pmtTyp not in Util.getLaneTypes():
			raise ValueError
		_pmtTyp = pmtTyp

	def getTimeRemaining(self):
		return _time_remaining

	def setTimeRemaining(self, datetime):
		if type(datetime) is not datetime:
			print('Invalid Input Type')
			raise TypeError
		_time_remaining = datetime





class Lane:
	_queue = []
	_lane_type = None

	def __init__(self, lane_type = 'GEN'):
		setLaneType(lane_type)
		

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
			Transaction.setProcessingTime(processingTimeCreditInCreditLane()

		#tag only lane
		elif Transaction.getTyp() == 'ETC' and self.getLaneType() = 'ETC':
			Transaction.setProcessingTime(processingTimeETCInETCLane())

		#cash in general lane
		elif Transaction.getTyp() == 'CASH' and self.getLaneType() = 'GEN':
			Transaction.setProcessingTime(processingTimeCashGen())

		#credit in general lane
		elif Transaction.getTyp() == 'CC' and self.getLaneType() = 'GEN':
			Transaction.setProcessingTime(processingTimeCreditGen())

		#pay-by mail general
		elif Transaction.getTyp() == 'PMB' and self.getLaneType() = 'GEN':
			Transaction.setProcessingTime(processingTimeMailGen())

		#tag general lane
		elif Transaction.getTyp() == 'ETC' and self.getLaneType() = 'GEN':
			Transaction.setProcessingTime(processingTimeETCGen())

		


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
		if lane_type not in _lane_types:
			print('Invalid Value, does not match existing lane type')
			raise ValueError
		_lane_type = lane_type
	def getLaneType(self):
		return _lane_type
	
class Facility:
	_system_time = None
	_total_queue = None
	_queue_by_lane = {}

	def	__init__(self):
		pass


class Util:
	"""
	Utility class with methods and fields to support Facility,
	Transaction, and Lane classes
	"""
	_lane_types = ['GEN','CC','ETC','CASH','PMB']

	def getLaneTypes(self):
		return _lane_types

