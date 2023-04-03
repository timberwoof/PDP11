"""PDP11 RAM and i/o"""

class ram:
    def __init__(self):
        print('initializing pdp11ram')

        # set up basic memory boundaries
        # overall size of memory: 64kB
        self.top_of_memory = 0o177777  # 0o177777 = 0xFFFF which is 16 bits

        # the actual array for simuating RAM.
        self.memory = bytearray(self.top_of_memory)

        # PSW is stored here
        self.PSW_address = self.top_of_memory - 3 # 0o377774

        # set up the vector space
        # the bottom area is io device handler vectors
        #self.top_of_vector_space = 0o274
        #for address in range(0o0, self.top_of_vector_space):
        #    self.write_byte(address, 0o377)
        # set up the io page space so it's always ready
        #for address in range(self.io_space, self.top_of_memory):
        #    self.write_byte(address, 0o111)

        # set up always-ready i/o device status words
        #self.write_word(self.TKS, 0o000000)
        #self.write_word(self.TPS, 0b0000000011000000) # always xmit ready and interrupt enabled

        # the io page is the top 4kB of memory
        self.io_space = self.top_of_memory - 0o1000
        print (f'io_space:{oct(self.io_space)}')

        # io map is two dictionaries of addresses and methods
        self.iomap_readers = {}
        self.iomap_writers = {}

    def register_io_reader(self, device_address, method):
        print(f'register_io_reader({oct(device_address)}, {method.__name__})')
        self.iomap_readers[device_address] = method

    def register_io_writer(self, device_address, method):
        print(f'register_io_writer({oct(device_address)}, {method.__name__})')
        self.iomap_writers[device_address] = method

    def read_byte(self, address):
        """Read one byte of memory."""
        if address in self.iomap_readers.keys():
            return self.iomap_readers[address]
        else:
            return self.memory[address]

    def read_word(self, address):
        """Read a word of memory.
        Low bytes are stored at even-numbered memory locations
        and high bytes at are stored at odd-numbered memory locations.
        Returns a two-byte value"""
        if address in self.iomap_readers.keys():
            return self.iomap_readers[address]
        else:
            hi = self.memory[address + 1]
            low = self.memory[address]
            result = (hi << 8) + low
            #print(f'    readword({oct(address)}): {oct(hi)} {oct(low)} result:{oct(result)}')
            return result

    def write_word(self, address, data):
        """write a two-word data chunk to memory.
        address must be even.

        :param address:
        :param data:
        """
        #print(f'    writeword({oct(address)}, {oct(data)})')
        if address in self.iomap_writers.keys():
            self.iomap_writers[address](data)
        else:
            hi = (data & 0o177400) >> 8  # 1 111 111 100 000 000
            lo = data & 0o000377  # 0 000 000 011 111 111
            # print(f'hi:{oct(hi)} lo:{oct(lo)}')
            self.memory[address + 1] = hi
            self.memory[address] = lo
            # print(f'hi:{oct(memory[address])} lo:{oct(memory[address-1])}')

    def write_byte(self, address, data):
        """write a byte to memory.
        address can be even or odd"""
        if address in self.iomap_writers.keys():
            self.iomap_writers[address](data)
        else:
            data = data & 0o000377
            #print(f'writebyte({oct(address)}, {oct(data)})')
            self.memory[address] = data

    def set_PSW(self, new_PSW):
        self.write_word(self.PSW_address, new_PSW)

    def get_PSW(self):
        return self.read_word(self.PSW_address)

    def dump(self, start, stop):
        print(f'{oct(start)}:{oct(stop)}')
        for address in range(start, stop+2, 2):
            print (f'{oct(address)}:{oct(self.read_word(address))}')