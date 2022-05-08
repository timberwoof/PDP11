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

        print (f'TKS:{oct(self.TKS)}')
        print (f'TKB:{oct(self.TKB)}')
        print (f'TPS:{oct(self.TPS)}')
        print (f'TPB:{oct(self.TPB)}')



    def readbyte(self, address):
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

    def readword(self, address):
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

    def writeword(self, address, data):
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

    def writebyte(self, address, data):
        """write a byte to self.memory.
        address can be even or odd"""
        #print(f'    writebyte({oct(address)}, {oct(data)})')
        self.memory[address] = data

        #if address > self.iospace:
            #print(f'    iopage @{oct(address)}')
        # serial output
        if address == self.TPB:
            #print(f'    TPB<-{data}')
            self.TPbuffer.append(data)
            if data == 0:
                print (self.TPbuffer.decode('utf-8'))
                #self.TPbuffer = bytearray("test", encoding="utf-8")

    def OctalToDecimal(self,num):
        decimal_value = 0
        base = 1
        while (num):
            last_digit = num % 10
            num = int(num / 10)
            decimal_value += last_digit * base
            base = base * 8
        return decimal_value

    def readPDP11(self, file):
        print (f'readPDP11 file "{file}"')
        base = 0
        text = open(file, 'r')
        for line in text:
            parts = line.split()
            if len(parts) == 0:
                continue
            part0 = parts[0]
            if part0 == ';':
                continue
            if part0.isnumeric():
                address = self.OctalToDecimal(int(part0))
                if base == 0:
                    base = address
            else:
                continue

            part1 = parts[1]
            value1 = self.OctalToDecimal(int(part1))
            print(part0, part1, address, value1)
            ram.writeword(self, address, value1)
        return base

