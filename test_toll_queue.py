import toll_queue
import random
import datetime
import pytest

class test_constants():
    datetime_midnight = datetime.datetime(2020,1,1)
    pmt_type_cash = 'CASH'
    pmt_type_credit = 'CC'
    pmt_type_ETC = 'ETC'
    pmt_type_mail = 'PMB'
    axel_cnt_2 = 2
    process_time_5_sec = datetime.timedelta(seconds=5)
    lane_type_list = ['GEN', 'CC', 'ETC', 'CASH', 'PMB']

class Test_Transaction():

    def random_trx_id(self):
        return random.randint(1,10000)

    def create_midnight_cash_trxn(self):
        rand_id = self.random_trx_id() 
        trxn = toll_queue.Transaction(test_constants.datetime_midnight,\
                test_constants.pmt_type_cash, test_constants.axel_cnt_2,\
                rand_id)
        return trxn

    def test_trxn_accessors(self):
        trxn = self.create_midnight_cash_trxn()
        assert trxn.get_axels() == test_constants.axel_cnt_2
        assert trxn.is_complete() == False
        assert trxn.get_type() == test_constants.pmt_type_cash
        assert trxn.get_date_time() == test_constants.datetime_midnight

    def test_check_invalid_processing_time(self):
        trxn = self.create_midnight_cash_trxn()
        invalid_input_str = ''
        invalid_input_int = 10
        with pytest.raises(TypeError):
            trxn.set_processing_time_trxn(invalid_input_str)
        with pytest.raises(TypeError):
            trxn.set_processing_time_trxn(invalid_input_int)

    def test_set_processing_time(self):
        trxn = self.create_midnight_cash_trxn()
        trxn.set_processing_time_trxn(test_constants.process_time_5_sec)
        assert trxn.is_complete() == False
        assert trxn.get_time_remaining_trxn() == test_constants.process_time_5_sec
        with pytest.raises(ValueError):
            trxn.set_processing_time_trxn(-test_constants.process_time_5_sec)

    def test_process_single_trxn(self):
        trxn = self.create_midnight_cash_trxn()
        trxn.set_processing_time_trxn(test_constants.process_time_5_sec)
        for i in range(4):
            trxn.advance_time_transaction()
            assert trxn.get_time_remaining_trxn() > datetime.timedelta()
        trxn.advance_time_transaction()
        assert trxn.is_complete() == True
        assert trxn.get_time_remaining_trxn() == datetime.timedelta()

    def test_incomplete_processing(self):
        trxn = self.create_midnight_cash_trxn()
        trxn.set_processing_time_trxn(test_constants.process_time_5_sec)
        trxn.advance_time_transaction()
        assert trxn.is_complete() == False
        assert trxn.get_time_remaining_trxn() > datetime.timedelta()

class Test_Lane():

    def random_trx_id(self):
        return random.randint(1,10000)

    def rand_lane_id(self):
        return random.randint(1,10)

    def rand_lane_type(self, lane_type_list):
        n = len(lane_type_list)
        index = random.randint(0, n-1)
        return lane_type_list[index]

    def create_midnight_cash_trxn(self):
        rand_id = self.random_trx_id() 
        trxn = toll_queue.Transaction(test_constants.datetime_midnight,\
                test_constants.pmt_type_cash, test_constants.axel_cnt_2,\
                rand_id)
        timedelta_5_seconds = datetime.timedelta(seconds=5)
        trxn.set_processing_time_trxn(timedelta_5_seconds)
        return trxn

    def create_random_lane(self):
        lane_id = self.rand_lane_id()
        lane_type = self.rand_lane_type(test_constants.lane_type_list)
        return toll_queue.Lane(lane_id, lane_type)

    def test_lane_constructor(self):
        lane_id = self.rand_lane_id()
        lane_type = self.rand_lane_type(test_constants.lane_type_list)
        lane = toll_queue.Lane(lane_id, lane_type)
        assert lane.get_lane_ID() == lane_id
        assert lane.get_lane_type() == lane_type

    def test_empty_lane(self):
        lane = self.create_random_lane()
        assert len(lane.get_queue()) == 0
        assert lane.get_queue_length() == 0
        assert lane.get_wait_time() == datetime.timedelta()

    def test_add_single_transaction(self):
        lane = self.create_random_lane()
        trxn = self.create_midnight_cash_trxn()
        lane.add_transaction(trxn)
        assert len(lane.get_queue()) == 1
        assert lane.get_queue_length() == 1

    def test_add_multiple_transaction(self):
        n = 5
        lane = self.create_random_lane()
        for i in range(n):
            trxn = self.create_midnight_cash_trxn()
            lane.add_transaction(trxn)
        assert lane.get_queue_length() == n
        assert lane.get_wait_time() <= datetime.timedelta(seconds=\
                n*(13.5+3*2.5))

    def test_processing_time_cash_gen_lane(self):
        lane = self.create_random_lane()
        range_low = datetime.timedelta(seconds=13.5 - 4*2.5)
        range_high = datetime.timedelta(seconds=13.5 + 4*2.5)
        for i in range(100):
            process_time = lane.processing_time_credit_gen_lane()
            assert process_time >= range_low
            assert process_time <= range_high

    def test_processing_time_credit_gen_lane(self):
        lane = self.create_random_lane()
        range_low = datetime.timedelta(seconds=13.5 - 4.0*2.5)
        range_high = datetime.timedelta(seconds=13.5 + 4.0*2.5)
        for i in range(100):
            process_time = lane.processing_time_credit_gen_lane()
            assert process_time >= range_low
            assert process_time <= range_high

    def test_processing_time_credit_credit_lane(self):
        lane = self.create_random_lane()
        range_low = datetime.timedelta(seconds=13 - 4.0*2.5)
        range_high = datetime.timedelta(seconds=13 + 4.0*2.5)
        for i in range(100):
            process_time = lane.processing_time_credit_credit_lane()
            assert process_time >= range_low
            assert process_time <= range_high

    def test_processing_time_ETC_ETC_lane(self):
        lane = self.create_random_lane()
        range_low = datetime.timedelta(seconds=5 - 4*1)
        range_high = datetime.timedelta(seconds=5 + 4*1)
        for i in range(100):
            process_time = lane.processing_time_ETC_ETC_lane()
            assert process_time >= range_low
            assert process_time <= range_high

    def test_processing_time_mail_gen_lane(self):
        lane = self.create_random_lane()
        range_low = datetime.timedelta(seconds=7 - 4*1)
        range_high = datetime.timedelta(seconds=7 + 4*1)
        for i in range(100):
            process_time = lane.processing_time_mail_gen_lane()
            assert process_time >= range_low
            assert process_time <= range_high

    def test_processing_time_ETC_gen_lane(self):
        lane = self.create_random_lane()
        range_low = datetime.timedelta(seconds=6 - 4*1)
        range_high = datetime.timedelta(seconds=6 + 4*1)
        for i in range(100):
            process_time = lane.processing_time_ETC_gen_lane()
            assert process_time >= range_low
            assert process_time <= range_high

    def test_set_lane_type(self):
        lane = self.create_random_lane()
        lane.set_lane_type('GEN')
        assert lane.get_lane_type() == 'GEN'
        with pytest.raises(ValueError):
            lane.set_lane_type('TEST')

class Test_Facility():

    def random_trx_id(self):
        return random.randint(1,10000)

    def rand_lane_id(self):
        return random.randint(1,10)

    def create_midnight_cash_trxn(self):
        rand_id = self.random_trx_id() 
        midnight_today = datetime.datetime.now().date()
        trxn = toll_queue.Transaction(midnight_today,\
                test_constants.pmt_type_cash, test_constants.axel_cnt_2,\
                rand_id)
        return trxn

    def create_midnight_ETC_trxn(self):
        rand_id = self.random_trx_id() 
        midnight_today = datetime.datetime.now().date()
        trxn = toll_queue.Transaction(midnight_today,\
                test_constants.pmt_type_ETC, test_constants.axel_cnt_2,\
                rand_id)
        return trxn

    def create_test_facility_w_todays_date(self):
        datetime_today = datetime.datetime.now()
        midnight_today = datetime.datetime(datetime_today.year,\
                datetime_today.month, datetime_today.day)
        return toll_queue.Facility(midnight_today)

    def create_lane(self, lane_type):
        lane_id = self.rand_lane_id()
        lane_type = self.rand_lane_type(test_constants.lane_type_list)
        return toll_queue.Lane(lane_id, lane_type)

    def test_constructor(self):
        datetime_now = datetime.datetime.now()
        add_seconds = random.randint(1,100)
        rand_int = random.randint(1,100)
        incorrect_time = datetime_now + datetime.timedelta(seconds=add_seconds)
        test_facility = toll_queue.Facility(datetime_now)
        assert test_facility.get_start_time() == datetime_now
        assert test_facility.get_start_time() != incorrect_time
        with pytest.raises(TypeError):
            toll_queue.Facility(rand_int)

    def test_advance_time_facility_second(self):
        datetime_now = datetime.datetime.now()
        add_timedelta_second = datetime.timedelta(seconds=1)
        test_facility = toll_queue.Facility(datetime_now)
        test_facility.advance_time_facility()
        assert test_facility.get_current_time() == datetime_now + add_timedelta_second

    def test_advance_time_facility(self):
        datetime_now = datetime.datetime.now()
        add_timedelta_random = datetime.timedelta(seconds=random.randint(1,100))
        test_facility = toll_queue.Facility(datetime_now)
        test_facility.advance_time_facility(input_time=add_timedelta_random)
        assert test_facility.get_current_time() == datetime_now + add_timedelta_random

    def test_add_ETC_trxn_ETC_lane(self):
        n = 10 #transaction count
        test_facility = self.create_test_facility_w_todays_date()
        test_facility.add_lane(toll_queue.Lane(1, 'ETC'))
        for i in range(n):
            test_facility.add_transaction(self.create_midnight_ETC_trxn())
            assert test_facility.total_queue() == (i+1)

        #total time within expected range
        low_expected = datetime.timedelta(seconds = n * (5 - 4*1))
        high_expected = datetime.timedelta(seconds = n * (5 + 4*1))
        assert test_facility.get_total_wait_time() >= low_expected and\
                test_facility.get_total_wait_time() <= high_expected

        #process transactions
        t = n * (5 + 4*1)
        for i in range(t):
            test_facility.advance_time_facility()
        assert test_facility.get_total_wait_time() == datetime.timedelta()
        assert test_facility.total_queue() == 0

    def test_add_cash_to_ETC_lane(self):
        test_facility = self.create_test_facility_w_todays_date()
        test_facility.add_lane(toll_queue.Lane(1, 'ETC'))
        cash_trxn = self.create_midnight_cash_trxn()
        with pytest.raises(TypeError):
            test_facility.add_transaction(cash_trxn)
