"""PDP11 RK11 Interface"""
import logging
class RK11:
    """DEC RK11 disk drive interface"""
    # *** stubbed out. Inoperative.
    def __init__(self, ram):
        logging.info('initializing RK11')
        self.ram = ram
        base_address = 0o177400
        self.RKDS_address = base_address
        self.RKER_address = base_address + 0o02
        self.RKCS_address = base_address + 0o04
        self.RKWC_address = base_address + 0o06
        self.RKBA_address = base_address + 0o10
        self.RKDA_address = base_address + 0o12
        self.RKMR_address = base_address + 0o14
        self.RKDB_address = base_address + 0o16

        logging.info('RK11 register_with_ram')
        self.ram.register_io_writer(self.RKCS_address, self.write_RKCS)  # rw
        self.ram.register_io_writer(self.RKWC_address, self.write_RKWC)  # rw
        self.ram.register_io_writer(self.RKBA_address, self.write_RKBA)  # rw
        self.ram.register_io_writer(self.RKDA_address, self.write_RKDA)  # rw
        self.ram.register_io_writer(self.RKMR_address, self.write_RKMR)  # rw
        self.ram.register_io_writer(self.RKDB_address, self.write_RKDB)  # rw

        self.ram.register_io_reader(self.RKDS_address, self.read_RKDS)  # ro
        self.ram.register_io_reader(self.RKER_address, self.read_RKER)  # ro
        self.ram.register_io_reader(self.RKCS_address, self.read_RKCS)
        self.ram.register_io_reader(self.RKWC_address, self.read_RKWC)
        self.ram.register_io_reader(self.RKBA_address, self.read_RKBA)
        self.ram.register_io_reader(self.RKDA_address, self.read_RKDA)
        self.ram.register_io_reader(self.RKMR_address, self.read_RKMR)
        self.ram.register_io_reader(self.RKDB_address, self.read_RKDB)

        self.RKCS = 0
        self.RKWC = 0
        self.RKBA = 0
        self.RKDA = 0
        self.RKMR = 0
        self.RKDB = 0
        logging.info('initializing RK11 done')

    def write_RKCS(self, data):
        logging.info('RK11 write_RKCS')
        self.RKCS = data
    def write_RKWC(self, data):
        logging.info('RK11 write_RKWC')
        self.RKWC = data
    def write_RKBA(self, data):
        logging.info('RK11 write_RKBA')
        self.RKBA = data
    def write_RKDA(self, data):
        logging.info('RK11 write_RKDA')
        self.RKDA = data
    def write_RKMR(self, data):
        logging.info('RK11 write_RKMR')
        self.RKMR = data
    def write_RKDB(self, data):
        logging.info('RK11 write_RKDB')
        self.RKDB = data

    def read_RKDS(self):
        logging.info('RK11 read_RKDS')
        return 0
    def read_RKER(self):
        logging.info('RK11 read_RKER')
        return 0
    def read_RKCS(self):
        logging.info('RK11 read_RKCS')
        return self.RKCS
    def read_RKWC(self):
        logging.info('RK11 read_RKWC')
        return self.RKWC
    def read_RKBA(self):
        logging.info('RK11 read_RKBA')
        return self.RKBA
    def read_RKDA(self):
        logging.info('RK11 read_RKDA')
        return self.RKDA
    def read_RKMR(self):
        logging.info('RK11 read_RKMR')
        return self.RKMR
    def read_RKDB(self):
        logging.info('RK11 read_RKDB')
        return self.RKDB

    def control_reset(self):
        logging.info('RK11 control reset')

    def drive_reset(self):
        logging.info('RK11 drive reset')

    def write_lock(self):
        logging.info('RK11 write lock')

    def seek(self):
        logging.info('RK11 seek')

    def write_check(self):
        logging.info('RK11 write check')

    def write(self):
        logging.info('RK11 write')

    def read_check(self):
        logging.info('RK11 read check')

    def read(self):
        logging.info('RK11 read')



