"""
Toll Booth Queue Simulator
Author: Eric Knigge
"""
import os
import datetime
import shutil
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
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
    _date_time = None
    _pmt_type = None
    _axel = None
    _processing_time = None
    _time_remaining = None
    _complete = False
    _trx_id = None
    _datetime_second = datetime.timedelta(seconds=1)

    def __init__(self, dateTime_created, pmtTyp, axel, trxID):
        self._date_time = dateTime_created
        self._axel = axel
        self._time_remaining = datetime.timedelta(seconds=0)
        self.set_pmt_type(pmtTyp)
        self._trx_id = trxID

    def set_processing_time_trxn(self, datetime_value):
        """
        Set value of the remaining time and processing time. Process
        time does not change.
        :param datetime_value: datetime.timedelta object
        """
        if not isinstance(datetime_value, datetime.timedelta):
            raise TypeError('Invalid value')
        if datetime_value < datetime.timedelta():
            raise ValueError('negative processing time, invalid input')
        self.set_time_remaining_trxn(datetime_value)
        self._processing_time = (datetime_value)

    def get_trx_id(self):
        """
        Returns transaction ID
        """
        return self._trx_id

    def get_axels(self):
        """
        Returns axel count
        :returns: int
        """
        return self._axel

    def advance_time_transaction(self, time=datetime.timedelta(seconds=1)):
        """
        Advance transaction processing time input.
        :param time: datetime.timedelta value. Default is 1 second.
        """
        if not isinstance(time, datetime.timedelta):
            raise TypeError('invalid input type')
        self.set_time_remaining_trxn(self.get_time_remaining_trxn() - time)
        if self.get_time_remaining_trxn() <= datetime.timedelta(seconds=0):
            self._complete = True

    def is_complete(self):
        """
        Whether transaction has been processed
        :returns: boolean
        """
        return self._complete

    def get_type(self):
        """
        Returns transaction type
        :returns: String transaction type
        """
        return self._pmt_type

    def get_date_time(self):
        """
        Returns when date when transaction was created
        :returns: datetime object
        """
        return self._date_time

    def set_pmt_type(self, pmt_type):
        """
        Set payment type
        :param pmt_type: String of valid payment type
        """
        if pmt_type not in Util().get_lane_types():
            raise ValueError
        self._pmt_type = pmt_type

    def get_time_remaining_trxn(self):
        """
        :returns: datetime object of time remaining
        """
        return self._time_remaining

    def get_process_time(self):
        """
        :returns: tuple, process time for transaction
        """
        return self._processing_time

    def set_time_remaining_trxn(self, date_time_value):
        """
        Set remaining time
        :param date_time_value: datetime object
        """

        ######
        # add TypeError check for datetime or datetime.timedelta
            ######
        # if type(datetime) is not datetime or type(datetime) is not datetime.timedelta:
        #   raise TypeError('Invalid Input Type')
        self._time_remaining = date_time_value

    def __str__(self):
        out = ''
        out += 'Transaction Information ' + '\n'
        out += 'TrxID: ' + str(self.get_trx_id()) + '\n'
        out += 'Start Time: ' + str(self.get_date_time()) + '\n'
        out += 'Time Remaining: ' + str(self._time_remaining) + '\n'
        out += 'Payment Type: ' + str(self.get_type()) + '\n'
        out += 'Complete: ' + str(self._complete) + '\n'
        out += 'Axels: ' + str(self.get_axels()) + '\n'
        return out


class Lane:
    """
    Lane used to for queueing transactions and as a componenent of Facility class.

    :param landID: unique lane ID number
    :param lane_type: String of lane type, must be contained in Util types
    """
    _queue = []
    _lane_type = None
    _lane_id = None

    def __init__(self, laneID, lane_type):
        self._queue = []
        self._lane_type = None
        self._lane_id = None

        self.set_lane_type(lane_type)
        self.set_lane_id(laneID)

    def get_wait_time(self):
        """
        Uses current lane queue to calculate wait time

        :returns: datetime.timedelta wait time for lane
        """
        out = datetime.timedelta(seconds=0)
        for transaction in self._queue:
            out += transaction.get_time_remaining_trxn()
        return out

    def set_processing_time_lane_and_trxn(self, transaction):
        """
        Set processing time for various types of transactions. Matches
        processing time to transaction and lane type.

        :param transaction: Transaction object
        :returns: None
        :raises TypeError: Transaction Class Type Required
        """

        if not isinstance(transaction, Transaction):
            raise TypeError('Invalid Input')

        # credit in credit lane
        if transaction.get_type() == 'CC' and self.get_lane_type() == 'CC':
            transaction.set_processing_time_trxn(self.processing_time_credit_credit_lane())

        # tag only lane
        elif transaction.get_type() == 'ETC' and self.get_lane_type() == 'ETC':
            transaction.set_processing_time_trxn(self.processing_time_etc_etc_lane())

        # cash in general lane
        elif transaction.get_type() == 'CASH' and self.get_lane_type() == 'GEN':
            transaction.set_processing_time_trxn(self.processing_time_cash_gen_lane())

        # credit in general lane
        elif transaction.get_type() == 'CC' and self.get_lane_type() == 'GEN':
            transaction.set_processing_time_trxn(self.processing_time_credit_gen_lane())

        # pay-by mail general
        elif transaction.get_type() == 'PMB' and self.get_lane_type() == 'GEN':
            transaction.set_processing_time_trxn(self.processing_time_mail_gen_lane())

        # tag general lane
        elif transaction.get_type() == 'ETC' and self.get_lane_type() == 'GEN':
            transaction.set_processing_time_trxn(self.processing_time_etc_gen_lane())

    def set_lane_id(self, lane_id):
        """
        Set lane ID
        :param lane_id: int
        """
        if not isinstance(lane_id, int):
            raise TypeError('input not int')
        self._lane_id = lane_id

    def get_lane_id(self):
        """
        :returns: laneID
        """
        return self._lane_id

    def __str__(self):
        out = ''
        out += 'Lane Information' + '\n'
        out += 'Lane ID: ' + str(self.get_lane_id()) + '\n'
        out += 'Lane Type: ' + str(self.get_lane_type()) + '\n'
        out += 'Queue Length: ' + str(len(self.get_queue())) + '\n'
        out += '\n'
        return out

    def get_queue(self):
        """
        :returns: list of Transaction objects
        """
        return self._queue

    def get_queue_length(self):
        """
        :returns: int of queue length
        """
        return len(self._queue)

    def processing_time_cash_gen_lane(self):
        """
        Calculates processing time for cash in general purpose
        manual toll lane. Utilizes normal probaility distribution.
        Mean 13.5, stdev 2.5.

        :returns: datetime.timedelta object with processing time in seconds
        """
        process_time = np.random.normal(loc=13.5, scale=2.5)
        return datetime.timedelta(seconds=process_time)

    def processing_time_credit_gen_lane(self):
        """
        Calculates processing time for credit in general purpose
        manual toll lane. Utilizes normal probaility distribution.
        Mean 13.5, stdev 2.5.

        :returns: datetime.timedelta object with processing time in seconds
        """
        process_time = np.random.normal(loc=13, scale=2.5)
        return datetime.timedelta(seconds=process_time)

    def processing_time_credit_credit_lane(self):
        """
        Calculates processing time for credit in credit-only manual toll lane.
        Utilizes normal probaility distribution.
        Mean 13.0, stdev 2.5.

        :returns: datetime.timedelta object with processing time in seconds
        """
        process_time = np.random.normal(loc=13, scale=2.5)
        return datetime.timedelta(seconds=process_time)

    def processing_time_etc_etc_lane(self):
        """
        Calculates processing time for ETC in manual toll lane.
        Utilizes normal probaility distribution.
        Mean 5, stdev 1.

        :returns: datetime.timedelta object with processing time in seconds
        """
        process_time = np.random.normal(loc=5, scale=1)
        return datetime.timedelta(seconds=process_time)

    def processing_time_mail_gen_lane(self):
        """
        Calculates processing time for pay-by-mail transaction in manual toll lane.
        Utilizes normal probaility distribution.
        Mean 7.0, stdev 1.0.

        :returns: datetime.timedelta object with processing time in seconds
        """
        process_time = np.random.normal(loc=7, scale=1)
        return datetime.timedelta(seconds=process_time)

    def processing_time_etc_gen_lane(self):
        """
        Calculates processing time for ETC in general purpose manual toll lane.
        Utilizes normal probaility distribution.
        Mean 6, stdeev 1.

        :returns: datetime.timedelta object with processing time in seconds
        """
        process_time = np.random.normal(loc=6, scale=1)
        return datetime.timedelta(seconds=process_time)

    def set_lane_type(self, lane_type):
        """
        Set lane type

        :param lane_type: String, valid lane type
        """
        if lane_type not in Util().get_lane_types():
            raise ValueError('Invalid Value, does not match existing lane type')
        self._lane_type = lane_type

    def get_lane_type(self):
        """
        :returns: lane type
        """
        return self._lane_type

    def add_transaction(self, transaction):
        """
        Add transaction to lane. Calculates processing time based on
        lane and transaction types. Adds processing time to lane wait time.
        """
        if not isinstance(transaction, Transaction):
            raise TypeError('input not Transaction')

        self.set_processing_time_lane_and_trxn(transaction)
        self._queue.append(transaction)

    def advance_time_lane(self, time):
        """
        Advance time for all transactions in lane
        :param input_time: datetime.timedelta value for advancing time
        """
        try:
            self._queue[0].advance_time_transaction(time=time)
            if self._queue[0].is_complete():
                self._queue.remove(self._queue[0])
        except IndexError:
            pass


class Facility:
    """
    Facility is the highest level contrainer for storing transactions. A
    Facility is made up of Lanes, and Lanes contain transactions.
    The *start_time* provided is the start of the simulation.
    :param start_time: datetime object
    """
    _start_time = None
    _current_time = None
    _total_queue = None
    _queue_by_lane = {}
    _all_lanes = []
    _trx_ID_counter = 0
    _queue_summary = {}

    def __init__(self, start_time):
        self.set_start_time(start_time)

    def get_total_wait_time(self):
        """
        :returns: datetime.timedelta for total wait time for facility
        """
        total_wait_time = datetime.timedelta()
        for lane in self._all_lanes:
            total_wait_time += lane.get_wait_time()
        return total_wait_time

    def update_queue_summary(self):
        """
        Updates queue summary dictionary with total queue length (vehicles)
        and total wait time.
        """
        current_time = self.get_current_time()
        queue_length = self.total_queue()
        total_wait_time = self.get_total_wait_time()
        self._queue_summary[current_time] = [queue_length, total_wait_time]

    def export_queue_summary_to_csv(self, name='queue_summary.csv'):
        """
        Writes toll queue summary to CSV file
        """
        dict_index = list(self._queue_summary)
        dict_values = self._queue_summary.values()
        column_names = ['Queue_Length', 'Total_Wait_Time']
        df_out = pd.DataFrame(data=dict_values, index=dict_index,\
                              columns=column_names)
        df_out.to_csv(name)

    def add_lane(self, lane):
        """
        Add Lane to Facility
        :param lane: Lane object
        """
        if not isinstance(lane, Lane):
            raise TypeError('Incorrect type')
        if lane in self._all_lanes:
            raise ValueError('Lane already exists in system')
        self._all_lanes.append(lane)

    def advance_time_facility(self, input_time=datetime.timedelta(seconds=1)):
        """
        Advance time one second for transactions being processed
        and for facility time.
        :param input_time: datetime.timedelta value for advancing time.
        Default value is 1 second.
        """
        # advance time for facility
        self._current_time = self._current_time + input_time

        # advance time for first transaction in lane
        for lane in self._all_lanes:
            lane.advance_time_lane(time=input_time)

        #update queue summary
        self.update_queue_summary()

    def add_transaction(self, transaction):
        """
        Add transaction to facility. Transaction is added to shortest
        eligible queue. For example, credit card transaction may utilize
        a credit-only lane or general purpose manual toll lane, but will
        always choose the line with the shortest wait time.

        :param transaction: Transaction object
        """
        if not isinstance(transaction, Transaction):
            raise TypeError('Incorrect type')

        # create list with matching lane type or GEN lane
        possible_lane = []
        for lane in self._all_lanes:
            if lane.get_lane_type() == transaction.get_type() or \
                    lane.get_lane_type() == 'GEN':
                possible_lane.append(lane)

        # raise error if no matching lane
        if not possible_lane:
            raise TypeError('No applicable lane to process trxn')

        # select the fastest lane
        fastest_lane = possible_lane[0]  # default to first lane in list
        for lane in possible_lane:
            if lane.get_wait_time() < fastest_lane.get_wait_time():
                fastest_lane = lane

        # add to fastest lane
        fastest_lane.add_transaction(transaction)

    def total_queue(self):
        """
        :returns: int of total queue length
        """
        self.calculate_queue_by_lane()
        values = self._queue_by_lane.values()
        output = 0

        for value in values:
            output += value
        return output

    def calculate_queue_by_lane(self):
        """
        Calculates and updates lane queues
        """
        for lane in self._all_lanes:
            self._queue_by_lane[lane.get_lane_id()] = lane.get_queue_length()

    def get_lane_queue(self):
        """
        :returns: Dictionary object with queue by lane
        """
        self.calculate_queue_by_lane()
        return self._queue_by_lane

    def set_start_time(self, start_time):
        """
        :param start_time: datetime.datetime start time for Facility
        :returns: None
        """
        if not isinstance(start_time, datetime.datetime):
            raise TypeError('invalid input type, must be datetime.datetime')
        self._start_time = start_time
        self._current_time = start_time

    def get_start_time(self):
        """
        :returns: datetime.datetime start time
        """
        return self._start_time

    def get_current_time(self):
        """
        :returns: datetime.datetime of current time for facility
        """
        return self._current_time

    def __str__(self):
        out = ''
        out += 'Facility Information' + '\n'
        out += 'Start Time: ' + str(self.get_start_time()) + '\n'
        out += 'Current Time: ' + str(self._current_time) + '\n'

        self.calculate_queue_by_lane()
        for lane in self._queue_by_lane:
            out += 'Lane ' + str(lane) + ': ' + str(self._queue_by_lane[lane]) + '\n'
        return out


class Util:
    """
    Utility class with methods and fields to support Facility,
    Transaction, and Lane classes
    """
    _lane_types = ['GEN', 'CC', 'ETC', 'CASH', 'PMB', 'PBM']

    def get_lane_types(self):
        """
        :returns: list of lane types
        """
        return self._lane_types

    def get_transaction_to_add(self, dataframe, datetime_value):
        """
        Filters dataframe for elegible transactions
        to add to a Facility.

        :param dataframe: dataframe object
        :param datetime_value: datetime value for filtering dataframe
        :returns: dataframe of transaction to add
        """
        df_out = dataframe
        df_out = df_out[(df_out['trans date/time'] < datetime_value)]
        return df_out

    def add_transaction_from_dataframe(self, facility, dataframe):
        """
        Add elegible transactions from dataframe to Facility

        :param facility: Facility object to add transaction
        :param dataframe: dataframe of transactions to add
        """
        df_out = dataframe
        n = df_out.shape[0]
        for i in range(n):
            df_row = df_out.iloc[i]
            new_transaction = Transaction(df_row[0], df_row[2], df_row[3], i)
            facility.add_transaction(new_transaction)

    def plot_lane_queues(self, lane_list, lane_queue_dict, simulation_time):
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

        # get labels
        labels = []
        for lane in lanes:
            labels.append(int(lane[0]))

        values = data.values()

        fig, ax = plt.subplots()
        ax.bar(labels, values)
        plt.title('Plaza Queue   ' + str(time))
        plt.ylim(0, 100)
        ax.set_ylabel('Queue Length')
        ax.set_xlabel('Lane Number')

        # save fig
        name = self.fmt_date(time.year) + self.fmt_date(time.month) + \
               self.fmt_date(time.day) + 'T' + self.fmt_date(time.hour) + \
               self.fmt_date(time.minute) + self.fmt_date(time.second) + \
               '.png'
        plt.savefig(name)
        plt.close()

    def fmt_date(self, value):
        """
        Format dates to include leading 0
        """
        string = str(value)
        if len(string) == 1:
            string = '0' + string
        return string


# Test simulation
if __name__ == '__main__':
    SCRIPT_RUNTIME_START = datetime.datetime.now()

    # simulation time represents, current time while running model
    START_TIME = datetime.datetime(2019, 5, 4, hour=0, minute=0)
    SIMULATION_TIME = START_TIME
    ONE_SECOND = datetime.timedelta(seconds=1)
    SECONDS_IN_DAY = 60 * 60 * 24
    SECONDS_IN_DAY = 60 * 3

    # import test data
    SAMPLE_DATA = '20190504.csv'
    DF = pd.read_csv(SAMPLE_DATA)
    DF['trans date/time'] = pd.to_datetime(DF['trans date/time'])

    # create test facility
    TEST_FACILITY = Facility(START_TIME)

    # add lanes
    LANE_LIST = [(1, 'GEN'), (2, 'GEN'), (3, 'GEN'), \
                 (4, 'GEN'), (5, 'GEN'), (6, 'GEN')]
    for i in LANE_LIST:
        TEST_FACILITY.add_lane(Lane(i[0], i[1]))

    ###################
    # main loop
    ###################

    # animation directory setup
    ALL_FILES = os.listdir()
    if 'output' in ALL_FILES:
        shutil.rmtree('output')
    os.mkdir('output')
    os.chdir('output')

    # increment time for analysis day
    for i in range(SECONDS_IN_DAY):
        print(i)

        # add transactions to facility
        df_add = Util().get_transaction_to_add(DF, SIMULATION_TIME)
        # remove added transactions from dataframe
        DF = DF.drop(df_add.index)
        Util().add_transaction_from_dataframe(TEST_FACILITY, df_add)

        # create output graphic
        Util().plot_lane_queues(LANE_LIST, TEST_FACILITY.get_lane_queue(), SIMULATION_TIME)

        # advance facility and simulation time
        SIMULATION_TIME = SIMULATION_TIME + ONE_SECOND
        TEST_FACILITY.advance_time_facility()

    #output queue summary
    TEST_FACILITY.export_queue_summary_to_csv()

    # create video file
    WIDTH = 640
    HEIGHT = 480
    FPS = 30
    SECONDS = SECONDS_IN_DAY / 30

    FOURCC = VideoWriter_fourcc(*'MP42')
    VIDEO = VideoWriter('test.avi', FOURCC, float(FPS), (WIDTH, HEIGHT))

    IMG_FILES = os.listdir()
    for i in IMG_FILES:
        print(i)
        img = cv2.imread(i)
        VIDEO.write(img)
    VIDEO.release()

    # remove img files
    IMG_FILES = os.listdir()
    for i in IMG_FILES:
        if 'png' in i:
            os.remove(i)
    print('Runtime: ' + str(datetime.datetime.now() - SCRIPT_RUNTIME_START))
