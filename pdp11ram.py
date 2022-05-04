"""PDP11 RAM"""

TKS = 0o177560
TKB = 0o177562
TPS = 0o177564
TPB = 0o177566



class ram:
    def __init__(self):
        #print('initializing pdp11ram')
        self.topofmemory = 0o377777  # 0xFFFF which is 16 bits
        self.iospace = self.topofmemory - 0o27777
        self.memory = bytearray(self.topofmemory)

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
        result = 0o177777
        if address < self.iospace:
            result = (hi << 8) + low
        if address == TKS:
            result = 0o000000
        if address == TKB:
            result = 0o000000
        if address == TPS:
            result = 0o000000
        #print(f'readword({oct(address)}): {oct(hi)} {oct(low)} result:{oct(result)}')
        return result

    def writeword(self, address, data):
        """write a two-word data chunk to self.memory.
        address needs to be even"""
        print(f'writeword({oct(address)}, {oct(data)})')
        hi = (data & 0o177400) >> 8  # 1 111 111 100 000 000
        lo = data & 0o000377  # 0 000 000 011 111 111
        # print(f'hi:{oct(hi)} lo:{oct(lo)}')
        self.memory[address + 1] = hi
        self.memory[address] = lo
        # print(f'hi:{oct(self.memory[address])} lo:{oct(self.memory[address-1])}')

        # serial output
        if address == 177566:
            print(f'print:{data}')

    def writebyte(self, address, data):
        """write a byte to self.memory.
        address can be even or odd"""
        print(f'writebyte({oct(address)}, {oct(data)})')
        self.memory[address] = data

        # serial output
        if address == 177566:
            print(f'print:{data}')