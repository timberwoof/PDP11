"""PDP11 DL11 communications console"""
from pdp11Hardware import ram

class dl11:
    def __init__(self, ram, base_address):
        print(f'initializing pdp11DL11.dl11({oct(base_address)})')
        self.ram = ram
        self.RCSR_address = base_address
        self.RBUF_address = base_address + 2
        self.XCSR_address = base_address + 4
        self.XBUF_address = base_address + 6

        print(f'dl11 RCSR:{oct(self.RCSR_address)}')
        print(f'dl11 RBUF:{oct(self.RBUF_address)}')
        print(f'dl11 XCSR:{oct(self.XCSR_address)}')
        print(f'dl11 XBUF:{oct(self.XBUF_address)}')

        self.RCSR = 0
        self.RBUF = 0
        self.XCSR = 0
        self.XBUF = 0

    # these methods let RAM write to the registers
    def write_RCSR(self, byte):
        """write to receiver status register"""
        print(f'dl11.write_RCSR({oct(byte)})')
        self.RCSR = byte

    def write_RBUF(self, byte):
        """write to receiver buffer register"""
        print(f'dl11.write_RBUF({oct(byte)})')
        self.RBUF = byte

    def write_XCSR(self, byte):
        """write to transmitter status register"""
        print(f'dl11.write_XCSR({oct(byte)})')
        self.XCSR = byte

    def write_XBUF(self, byte):
        """write to transitter buffer register"""
        print(f'dl11.write_XBUF({oct(byte)})')
        self.XBUF = byte
        print(f'{chr(byte)}')

    # these methods let RAM read from the registers
    def read_RCSR(self):
        """read from receiver status register"""
        print(f'dl11.read_RCSR() returns {oct(self.RCSR)}')
        return self.RCSR

    def read_RBUF(self):
        """read from receiver buffer register"""
        print(f'dl11.read_RBUF() returns {oct(self.RBUF)}')
        return self.RBUF

    def read_XCSR(self):
        """read from transitter status register"""
        print(f'dl11.read_XCSR() returns {oct(self.XCSR)}')
        return self.XCSR

    def read_XBUF(self):
        """read from transitter buffer register"""
        print(f'dl11.read_XBUF() returns {oct(self.XBUF)}')
        return self.XBUF

    def register_with_ram(self):
        print(f'dl11.register_with_ram')
        self.ram.register_io_writer(self.RCSR_address, self.write_RCSR)
        self.ram.register_io_reader(self.RCSR_address, self.read_RCSR)
        self.ram.register_io_writer(self.RBUF_address, self.write_RBUF)
        self.ram.register_io_reader(self.RBUF_address, self.read_RBUF)
        self.ram.register_io_writer(self.XCSR_address, self.write_XCSR)
        self.ram.register_io_reader(self.XCSR_address, self.read_XCSR)
        self.ram.register_io_writer(self.XBUF_address, self.write_XBUF)
        self.ram.register_io_reader(self.XBUF_address, self.read_XBUF)
