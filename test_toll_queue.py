import random
import toll_queue
import datetime
import pytest


class Constants():
    """
    Constant class with variables used for testing
    """
    datetime_midnight = datetime.datetime(2020, 1, 1)
    pmt_type_cash = 'CASH'
    pmt_type_credit = 'CC'
    pmt_type_ETC = 'ETC'
    pmt_type_mail = 'PMB'
    axel_cnt_2 = 2
    process_time_5_sec = datetime.timedelta(seconds=5)
    lane_type_list = ['GEN', 'CC', 'ETC', 'CASH', 'PMB']


class Test_Transaction():
    """
    Test creattion of transaction objects
    """

    def random_trx_id(self):
        """:return: random trxn id between 1 and 10,000"""
        return random.randint(1, 10000)

    def create_midnight_cash_trxn(self):
        """:return: Transaction of type cash, 2 axels, with start time at midnight"""
        rand_id = self.random_trx_id()
        trxn = toll_queue.Transaction(Constants.datetime_midnight, \
                                      Constants.pmt_type_cash, Constants.axel_cnt_2, \
                                      rand_id)
        return trxn

    def test_constructor(self):
        """Validate constructor and accessors"""
        trxn = self.create_midnight_cash_trxn()
        assert trxn.get_axels() == Constants.axel_cnt_2
        assert trxn.is_complete() == False
        assert trxn.get_type() == Constants.pmt_type_cash
        assert trxn.get_date_time() == Constants.datetime_midnight

    def test_check_invalid_processing_time(self):
        """Validate processing time method"""
        trxn = self.create_midnight_cash_trxn()
        invalid_input_str = ''
        invalid_input_int = 10
        with pytest.raises(TypeError):
            trxn.set_processing_time_trxn(invalid_input_str)
        with pytest.raises(TypeError):
            trxn.set_processing_time_trxn(invalid_input_int)

    def test_set_processing_time(self):
        """Validate processing time method"""
        trxn = self.create_midnight_cash_trxn()
        trxn.set_processing_time_trxn(Constants.process_time_5_sec)
        assert trxn.is_complete() == False
        assert trxn.get_time_remaining_trxn() == Constants.process_time_5_sec
        with pytest.raises(ValueError):
            trxn.set_processing_time_trxn(-Constants.process_time_5_sec)

    def test_process_single_trxn(self):
        """Validate creation and manual completion of single transaction"""
        trxn = self.create_midnight_cash_trxn()
        trxn.set_processing_time_trxn(Constants.process_time_5_sec)
        for i in range(4):
            trxn.advance_time_transaction()
            assert trxn.get_time_remaining_trxn() > datetime.timedelta()
        trxn.advance_time_transaction()
        assert trxn.is_complete() == True
        assert trxn.get_time_remaining_trxn() == datetime.timedelta()

    def test_incomplete_processing(self):
        """Validate incomplete processing of single transction"""
        trxn = self.create_midnight_cash_trxn()
        trxn.set_processing_time_trxn(Constants.process_time_5_sec)
        trxn.advance_time_transaction()
        assert trxn.is_complete() == False
        assert trxn.get_time_remaining_trxn() > datetime.timedelta()


class Test_Lane():
    """Test Lane class functionality"""

    def random_trx_id(self):
        """:returns: random transaction id between 1 and 10,000"""
        return random.randint(1, 10000)

    def rand_lane_id(self):
        """:returns: random int between 1 and 10"""
        return random.randint(1, 10)

    def rand_lane_type(self, lane_type_list):
        """:returns: random lane type based on Constant class"""
        n = len(lane_type_list)
        index = random.randint(0, n - 1)
        return lane_type_list[index]

    def create_midnight_cash_trxn(self):
        """:returns: Transaction of type cash with 2 axel starting at midnight"""
        rand_id = self.random_trx_id()
        trxn = toll_queue.Transaction(Constants.datetime_midnight, \
                                      Constants.pmt_type_cash, Constants.axel_cnt_2, \
                                      rand_id)
        timedelta_5_seconds = datetime.timedelta(seconds=5)
        trxn.set_processing_time_trxn(timedelta_5_seconds)
        return trxn

    def create_random_lane(self):
        """:returns: random Lane type with random id"""
        lane_id = self.rand_lane_id()
        lane_type = self.rand_lane_type(Constants.lane_type_list)
        return toll_queue.Lane(lane_id, lane_type)

    def test_lane_constructor(self):
        """Validate lane constructor and accessors"""
        lane_id = self.rand_lane_id()
        lane_type = self.rand_lane_type(Constants.lane_type_list)
        lane = toll_queue.Lane(lane_id, lane_type)
        assert lane.get_lane_id() == lane_id
        assert lane.get_lane_type() == lane_type

    def test_empty_lane(self):
        """Validate empty lane constructor"""
        lane = self.create_random_lane()
        assert len(lane.get_queue()) == 0
        assert lane.get_queue_length() == 0
        assert lane.get_wait_time() == datetime.timedelta()

    def test_add_single_transaction(self):
        """Validate adding single transaction to empty lane"""
        lane = self.create_random_lane()
        trxn = self.create_midnight_cash_trxn()
        lane.add_transaction(trxn)
        assert len(lane.get_queue()) == 1
        assert lane.get_queue_length() == 1

    def test_add_multiple_transaction(self):
        """Validate adding multiple transaction to lane and that
        wait time within bounds or normal distribution function.
        """
        n = 5
        lane = self.create_random_lane()
        for i in range(n):
            trxn = self.create_midnight_cash_trxn()
            lane.add_transaction(trxn)
        assert lane.get_queue_length() == n
        assert lane.get_wait_time() <= datetime.timedelta(seconds= \
                                                              n * (13.5 + 3 * 2.5))

    def test_processing_time_cash_gen_lane(self):
        """Validate normal distribution time output for cash in gen lane"""
        lane = self.create_random_lane()
        range_low = datetime.timedelta(seconds=13.5 - 4 * 2.5)
        range_high = datetime.timedelta(seconds=13.5 + 4 * 2.5)
        for i in range(100):
            process_time = lane.processing_time_credit_gen_lane()
            assert process_time >= range_low
            assert process_time <= range_high

    def test_processing_time_credit_gen_lane(self):
        """Validate normal distribution time output for credit in gen lane"""
        lane = self.create_random_lane()
        range_low = datetime.timedelta(seconds=13.5 - 4.0 * 2.5)
        range_high = datetime.timedelta(seconds=13.5 + 4.0 * 2.5)
        for i in range(100):
            process_time = lane.processing_time_credit_gen_lane()
            assert process_time >= range_low
            assert process_time <= range_high

    def test_processing_time_credit_credit_lane(self):
        """Validate normal distribution time output for credit in credit lane"""
        lane = self.create_random_lane()
        range_low = datetime.timedelta(seconds=13 - 4.0 * 2.5)
        range_high = datetime.timedelta(seconds=13 + 4.0 * 2.5)
        for i in range(100):
            process_time = lane.processing_time_credit_credit_lane()
            assert process_time >= range_low
            assert process_time <= range_high

    def test_processing_time_etc_etc_lane(self):
        """Validate normal distribution time output for etc in etc lane"""
        lane = self.create_random_lane()
        range_low = datetime.timedelta(seconds=5 - 4 * 1)
        range_high = datetime.timedelta(seconds=5 + 4 * 1)
        for i in range(100):
            process_time = lane.processing_time_etc_etc_lane()
            assert process_time >= range_low
            assert process_time <= range_high

    def test_processing_time_mail_gen_lane(self):
        """Validate normal distribution time output for mail in gen lane"""
        lane = self.create_random_lane()
        range_low = datetime.timedelta(seconds=7 - 4 * 1)
        range_high = datetime.timedelta(seconds=7 + 4 * 1)
        for i in range(100):
            process_time = lane.processing_time_mail_gen_lane()
            assert process_time >= range_low
            assert process_time <= range_high

    def test_processing_time_etc_gen_lane(self):
        """Validate normal distribution time output for etc in gen lane"""
        lane = self.create_random_lane()
        range_low = datetime.timedelta(seconds=6 - 4 * 1)
        range_high = datetime.timedelta(seconds=6 + 4 * 1)
        for i in range(100):
            process_time = lane.processing_time_etc_gen_lane()
            assert process_time >= range_low
            assert process_time <= range_high

    def test_set_lane_type(self):
        """Validate set lane type method"""
        lane = self.create_random_lane()
        lane.set_lane_type('GEN')
        assert lane.get_lane_type() == 'GEN'
        with pytest.raises(ValueError):
            lane.set_lane_type('TEST')


class Test_Facility():
    """Validate functionality of Facility class"""

    def random_trx_id(self):
        """:returns: random transaction id between 1 and 10,000"""
        return random.randint(1, 10000)

    def rand_lane_id(self):
        """:returns: random lane id between 1 and 10"""
        return random.randint(1, 10)

    def create_midnight_cash_trxn(self):
        """:returns: Transaction type cash, axle count 2, start time midnight"""
        rand_id = self.random_trx_id()
        midnight_today = datetime.datetime.now().date()
        trxn = toll_queue.Transaction(midnight_today,\
              Constants.pmt_type_cash, Constants.axel_cnt_2,\
              rand_id)
        return trxn

    def create_midnight_etc_trxn(self):
        """:returns: Transaction type etc, axle count 2, start time midnight"""
        rand_id = self.random_trx_id()
        midnight_today = datetime.datetime.now().date()
        trxn = toll_queue.Transaction(midnight_today, \
                                      Constants.pmt_type_ETC, Constants.axel_cnt_2, \
                                      rand_id)
        return trxn

    def create_test_facility_w_todays_date(self):
        """:returns: Facility with start date of today, time midnight"""
        datetime_today = datetime.datetime.now()
        midnight_today = datetime.datetime(datetime_today.year, \
                                           datetime_today.month, datetime_today.day)
        return toll_queue.Facility(midnight_today)

    def create_lane(self, lane_type):
        """:returns: Lane with random id and type"""
        lane_id = self.rand_lane_id()
        lane_type = self.rand_lane_type(Constants.lane_type_list)
        return toll_queue.Lane(lane_id, lane_type)

    def test_constructor(self):
        """Validate Facility constructor and accessors"""
        datetime_now = datetime.datetime.now()
        add_seconds = random.randint(1, 100)
        rand_int = random.randint(1, 100)
        incorrect_time = datetime_now + datetime.timedelta(seconds=add_seconds)
        test_facility = toll_queue.Facility(datetime_now)
        assert test_facility.get_start_time() == datetime_now
        assert test_facility.get_start_time() != incorrect_time
        with pytest.raises(TypeError):
            toll_queue.Facility(rand_int)

    def test_advance_time_facility_second(self):
        """
        Validate advance time method for facility, increment by 1
        second
        """
        datetime_now = datetime.datetime.now()
        add_timedelta_second = datetime.timedelta(seconds=1)
        test_facility = toll_queue.Facility(datetime_now)
        test_facility.advance_time_facility()
        assert test_facility.get_current_time() == datetime_now + add_timedelta_second

    def test_advance_time_facility(self):
        """
        Validate advance time of facility by random increment
        """
        datetime_now = datetime.datetime.now()
        add_timedelta_random = datetime.timedelta(seconds=random.randint(1, 100))
        test_facility = toll_queue.Facility(datetime_now)
        test_facility.advance_time_facility(input_time=add_timedelta_random)
        assert test_facility.get_current_time() == datetime_now + add_timedelta_random

    def test_add_etc_trxn_etc_lane(self):
        """
        Validate adding etc transaction to etc lane, and that processing
        time falls within expected time range.
        """
        n = 10  # transaction count
        test_facility = self.create_test_facility_w_todays_date()
        test_facility.add_lane(toll_queue.Lane(1, 'ETC'))
        for i in range(n):
            test_facility.add_transaction(self.create_midnight_etc_trxn())
            assert test_facility.total_queue() == (i + 1)

        # total time within expected range
        low_expected = datetime.timedelta(seconds=n * (5 - 4 * 1))
        high_expected = datetime.timedelta(seconds=n * (5 + 4 * 1))
        assert test_facility.get_total_wait_time() >= low_expected and \
               test_facility.get_total_wait_time() <= high_expected

        # process transactions
        t = n * (5 + 4 * 1)
        for i in range(t):
            test_facility.advance_time_facility()
        assert test_facility.get_total_wait_time() == datetime.timedelta()
        assert test_facility.total_queue() == 0

    def test_add_cash_to_ETC_lane(self):
        """Validate TypeError for invalid transaction being added to a lane"""
        test_facility = self.create_test_facility_w_todays_date()
        test_facility.add_lane(toll_queue.Lane(1, 'ETC'))
        cash_trxn = self.create_midnight_cash_trxn()
        with pytest.raises(TypeError):
            test_facility.add_transaction(cash_trxn)
