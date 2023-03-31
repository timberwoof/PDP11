"""PDP11 RAM"""



class ram:
    def __init__(self):
        print('initializing pdp11ram')
        self.topofmemory = 0o377777  # 0o377777 = 0xFFFF which is 16 bits
        self.iospace = self.topofmemory - 0o27777
        self.memory = bytearray(self.topofmemory)

        # set up the serial interface addresses
        self.TKS = self.iospace + 0o27560 # reader status register 177560
        self.TKB = self.iospace + 0o27562 # reader buffer register
        self.TPS = self.iospace + 0o27564 # punch status register
        self.TPB = self.iospace + 0o27566 # bunch buffer register
        self.TPbuffer = bytearray("", encoding="utf-8")

        print (f'    TKS:{oct(self.TKS)}')
        print (f'    TKB:{oct(self.TKB)}')
        print (f'    TPS:{oct(self.TPS)}')
        print (f'    TPB:{oct(self.TPB)}')



    def read_byte(self, address):
        """Read a byte of self.memory.
        Return 0o377 for anything in the vector space.
        Return 0o111 for anything in the iospace.
        Return 0 for anything else."""
        if address in range(0o0, 0o274):
            return 0o377
        elif address in range(300, self.iospace):
            return self.memory[address]
        elif address in range(self.iospace, self.topofmemory):
            return 0o111
        else:
            return 0o222

    def read_word(self, address):
        """Read a word of self.memory.
        Low bytes are stored at even-numbered self.memory locations
        and high bytes at odd-numbered self.memory locations.
        Returns two bytes."""
        hi = self.memory[address + 1]
        low = self.memory[address]
        result = 0o377777
        if address < self.iospace:
            result = (hi << 8) + low
        if address == self.TKS:
            result = 0o000000
        if address == self.TPS:
            result = 0b0000000011000000 # always xmit ready and interrupt enabled
        #print(f'    readword({oct(address)}): {oct(hi)} {oct(low)} result:{oct(result)}')
        return result

    def write_word(self, address, data):
        """write a two-word data chunk to self.memory.
        address needs to be even"""
        #print(f'    writeword({oct(address)}, {oct(data)})')
        hi = (data & 0o177400) >> 8  # 1 111 111 100 000 000
        lo = data & 0o000377  # 0 000 000 011 111 111
        # print(f'hi:{oct(hi)} lo:{oct(lo)}')
        self.memory[address + 1] = hi
        self.memory[address] = lo
        # print(f'hi:{oct(self.memory[address])} lo:{oct(self.memory[address-1])}')

        # serial output
        #if address > self.iospace:
            #print(f'    iopage @{oct(address)}')

    def write_byte(self, address, data):
        """write a byte to self.memory.
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



