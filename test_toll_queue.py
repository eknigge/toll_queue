import toll_queue
import random
import datetime
import pytest

class test_constants:
    datetime_midnight = datetime.datetime(2020,1,1)
    pmt_type_cash = 'CASH'
    pmt_type_credit = 'CC'
    pmt_type_ETC = 'ETC'
    pmt_type_mail = 'PMB'
    axel_cnt_2 = 2
    process_time_5_sec = datetime.timedelta(seconds=5)
    lane_type_list = ['GEN', 'CC', 'ETC', 'CASH', 'PMB']

class Test_Transaction:

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
            trxn.set_processing_time_lane(invalid_input_str)
        with pytest.raises(TypeError):
            trxn.set_processing_time_lane(invalid_input_int)

    def test_set_processing_time(self):
        trxn = self.create_midnight_cash_trxn()
        trxn.set_processing_time_lane(test_constants.process_time_5_sec)
        assert trxn.is_complete() == False
        assert trxn.get_time_remaining() == test_constants.process_time_5_sec
        with pytest.raises(ValueError):
            trxn.set_processing_time_lane(-test_constants.process_time_5_sec)

    def test_process_single_trxn(self):
        trxn = self.create_midnight_cash_trxn()
        trxn.set_processing_time_lane(test_constants.process_time_5_sec)
        for i in range(4):
            trxn.advance_time_transaction()
            assert trxn.get_time_remaining() > datetime.timedelta()
        trxn.advance_time_transaction()
        assert trxn.is_complete() == True
        assert trxn.get_time_remaining() == datetime.timedelta()

    def test_incomplete_processing(self):
        trxn = self.create_midnight_cash_trxn()
        trxn.set_processing_time_lane(test_constants.process_time_5_sec)
        trxn.advance_time_transaction()
        assert trxn.is_complete() == False
        assert trxn.get_time_remaining() > datetime.timedelta()

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
        trxn.set_processing_time_lane(timedelta_5_seconds)
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

    def test_set_lane_type(self):
        lane = self.create_random_lane()
        lane.set_lane_type('GEN')
        assert lane.get_lane_type() == 'GEN'
        with pytest.raises(ValueError):
            lane.set_lane_type('TEST')
