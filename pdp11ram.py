"""PDP11 RAM and i/o"""
class ram:
    def __init__(self):
        print('initializing pdp11ram')

        # set up basic memory boundaries
        # overall size of memory: 64kB
        self.top_of_memory = 0o377777  # 0o377777 = 0xFFFF which is 16 bits

        # the actual array for simuating RAM.
        self.memory = bytearray(self.top_of_memory)

        # the bottom area is io device handler vectors
        self.top_of_vector_space = 0o274

        # the io page is the top 4kB of memory
        self.io_space = self.top_of_memory - 0o27777

        # PSW is stored here
        self.PSW_address = self.top_of_memory - 3 # 0o377774

        # set up the serial interface addresses
        self.TKS = self.io_space + 0o27560 # reader status register 177560
        self.TKB = self.io_space + 0o27562 # reader buffer register
        self.TPS = self.io_space + 0o27564 # punch status register
        self.TPB = self.io_space + 0o27566 # punch buffer register
        self.TPbuffer = bytearray("", encoding="utf-8")

        print (f'    i/o devices:')
        print (f'    TKS:{oct(self.TKS)}')
        print (f'    TKB:{oct(self.TKB)}')
        print (f'    TPS:{oct(self.TPS)}')
        print (f'    TPB:{oct(self.TPB)}')

        # set up the vector space
        for address in range(0o0, self.top_of_vector_space):
            self.write_byte(address, 0o377)
        # set up the io page space
        for address in range(self.io_space, self.top_of_memory):
            self.write_byte(address, 0o111)

        # set up always-ready i/o device status words
        self.write_word(self.TKS, 0o000000)
        self.write_word(self.TPS, 0b0000000011000000) # always xmit ready and interrupt enabled

    def read_byte(self, address):
        """Read one byte of memory."""
        return self.memory[address]

    def read_word(self, address):
        """Read a word of memory.
        Low bytes are stored at even-numbered memory locations
        and high bytes at are stored at odd-numbered memory locations.
        Returns a two-byte value"""
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
        :return:
        """
        print(f'    writeword({oct(address)}, {oct(data)})')
        hi = (data & 0o177400) >> 8  # 1 111 111 100 000 000
        lo = data & 0o000377  # 0 000 000 011 111 111
        # print(f'hi:{oct(hi)} lo:{oct(lo)}')
        self.memory[address + 1] = hi
        self.memory[address] = lo
        # print(f'hi:{oct(memory[address])} lo:{oct(memory[address-1])}')

        # serial output
        #if address > self.iospace:
            #print(f'    iopage @{oct(address)}')

    def write_byte(self, address, data):
        """write a byte to memory.
        address can be even or odd"""
        data = data & 0o000377
        print(f'    writebyte({oct(address)}, {oct(data)})')
        self.memory[address] = data

        #if address > self.iospace:
            #print(f'    iopage {oct(address)}')
        # serial output
        if address == self.TPB:
            #print(f'    TPB<-{data}')
            self.TPbuffer.append(data)
            if data == 0:
                print (self.TPbuffer.decode('utf-8'))
                #self.TPbuffer = bytearray("test", encoding="utf-8")

    def set_PSW(self, new_PSW):
        self.write_word(self.PSW_address, new_PSW)

    def get_PSW(self):
        return self.read_word(self.PSW_address)


