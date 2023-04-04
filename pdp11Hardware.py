"""PDP11 RAM, Registers"""

class ram:
    def __init__(self):
        print('initializing pdp11 ram')

        # set up basic memory boundaries
        # overall size of memory: 64kB
        self.top_of_memory = 0o177777
            # 16 bits   0o177777 = 0x0000FFFF
            # 18 bits   0o777777 = 0x0003FFFF
            # 22 bits 0o17777777 = 0x003FFFFF

        # the actual array for simuating RAM.
        self.memory = bytearray(self.top_of_memory+1)
        # +1 because I want to be able to index self.top_of_memory

        # PSW is stored here
        self.PSW_address = self.top_of_memory - 1 # 0o377776
        self.Stack_Limit_Register = self.top_of_memory - 3 #0o377774

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
            return self.iomap_readers[address]()
        else:
            return self.memory[address]

    def read_word(self, address):
        """Read a word of memory.
        Low bytes are stored at even-numbered memory locations
        and high bytes at are stored at odd-numbered memory locations.
        Returns a two-byte value"""
        if address in self.iomap_readers.keys():
            return self.iomap_readers[address]()
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
            print(f'writebyte({oct(address)}, {oct(data)})')
            self.memory[address] = data

    def set_PSW(self, new_PSW):
        self.write_word(self.PSW_address, new_PSW)

    def get_PSW(self):
        return self.read_word(self.PSW_address)

    def dump(self, start, stop):
        print(f'{oct(start)}:{oct(stop)}')
        for address in range(start, stop+2, 2):
            print (f'{oct(address)}:{oct(self.read_word(address))}')

class reg:
    def __init__(self):
        print('initializing pdp11 registers')
        self.bytemask = 0o377
        self.wordmask = 0o177777
        self.registermask = 0o07
        self.SP = 0o06  # R6 is rfequentluy referred to as the stack pointer
        self.PC = 0o07  # R7 is the program counter
        self.registers = [0, 0, 0, 0, 0, 0, 0, 0]  # R0 R1 R2 R3 R4 R5 R6 R7

    def get(self, register):
        """read a single register

        :param register:
        :return: register contents"""
        result = self.registers[register & self.registermask]
        #print(f'    get R{register}={oct(result)}')
        return result

    def set(self, register, value):
        """set a single register
        :param register:
        :param value:
        """
        #print(f'    set R{register}<-{oct(value)}')
        self.registers[register & self.registermask] = value & self.wordmask

    def get_pc(self):
        """get program counter

        :return: program counter"""
        return self.registers[self.PC]

    def inc_pc(self, whocalled=''):
        """increment progran counter by 2

        :return: new program counter"""
        self.registers[self.PC] = self.registers[self.PC] + 2
        #print(f'    inc_pc R7<-{oct(self.registers[self.PC])} {whocalled}')
        return self.registers[self.PC]

    def set_pc(self, value, whocalled=''):
        """set program counter to arbitrary value"""
        waspc =  self.registers[self.PC]
        newpc = value & self.wordmask
        self.registers[self.PC] = newpc
        #print(f'    setpc R7<-{oct(newpc)} {whocalled}')

    def set_pc_2x_offset(self, offset, whocalled=''):
        """set program counter to 2x offset"""
        waspc = self.registers[self.PC]
        newpc = self.registers[self.PC] + 2 * (offset & self.bytemask)
        self.registers[self.PC] = newpc
        #print(f'    set_pc_2x_offset R7<-{oct(newpc)} (was:{oct(waspc)}) {whocalled}')

    def get_sp(self):
        """get stack pointer

        :return: stack pointer"""
        return self.registers[self.SP]

    def set_sp(self, value, whocalled=''):
        """set stack pointer

        :return: new stack pointer"""
        wassp =  self.registers[self.PC]
        newsp = value & self.wordmask
        self.registers[self.PC] = newsp
        #print(f'{oct(wassp)} setpc {oct(newsp)}')
        return newsp

    def log_registers(self):
        """print all the registers in the log"""
        index = 0
        report = '    '
        for register in self.registers:
            report = report + f'R{index}: {oct(register)}  '
            index = index + 1
        print (report)