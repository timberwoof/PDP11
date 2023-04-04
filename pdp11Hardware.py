"""PDP11 RAM, Registers, PSW"""

# masks for accessing words and bytes
mask_byte = 0o000377
mask_word = 0o177777
mask_byte_msb = 0o000200
mask_word_msb = 0o100000

class ram:
    def __init__(self):
        print('initializing pdp11Hardware.ram')

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

class registers:
    def __init__(self):
        print('initializing pdp11Hardware.reg')
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

class psw:
    """PDP11 PSW"""

    def __init__(self, ram):
        """initialize PDP11 PSW"""
        print('initializing pdp11Hardware.psw')
        # 104000-104377 EMT (trap & interrupt)
        # 104400-104777 TRAP (trap & interrupt)

        # 013400 0 001 011 100 000 000 BCS (branch)
        # 16SSDD 1 110 *** *** *** *** subtract src from dst (double)
        # 06SSDD 0 110 *** *** *** *** ADD add src to dst (double)

        # PSW bit meanings and masks
        # 15 14 current mode        0o140000
        # 13 12 previous mode       0o030000
        # 7 6 5 priority            0o000340
        # 4 T trap                  0o000020
        # 3 N result was negative   0o000010
        # 2 Z result was zero       0o000004
        # 1 V overflow              0o000002
        # 0 C result had carry      0o000001
        self.ram = ram
        self.c_mode_mask = 0o140000
        self.p_mode_mask = 0o030000
        self.mode_mask = 0o170000
        self.priority_mask = 0o000340
        self.trap_mask = 0o000020
        self.N_mask = 0o000010  # Negative
        self.Z_mask = 0o000004  # Zero
        self.V_mask = 0o000002  # Overflow
        self.C_mask = 0o000001  # Carry

        self.byte_mask = 0o000377
        self.word_mask = 0o177777

    def set_PSW(self, mode=-1, priority=-1, trap=-1, N=-1, Z=-1, V=-1, C=-1, PSW=-1):
        """set processor status word by optional parameter

        :param mode:
        :param priority:
        :param trap:
        :param N:
        :param Z:
        :param V:
        :param C:
        :param PSW:
        :return:
        """
        new_PSW = PSW
        PSW = self.ram.get_PSW()
        if mode > -1:
            oldmode = (PSW & self.mode_mask)
            PSW = (PSW & ~self.c_mode_mask) | (mode << 14) | (oldmode >> 2)
        if priority > -1:
            PSW = (PSW & ~self.priority_mask) | (priority << 5)
        if trap > -1:
            PSW = (PSW & ~self.trap_mask) | (trap << 4)
        if N > -1:
            PSW = (PSW & ~self.N_mask) | (N << 3)
        if Z > -1:
            PSW = (PSW & ~self.Z_mask) | (Z << 2)
        if V > -1:
            PSW = (PSW & ~self.V_mask) | (V << 1)
        if C > -1:
            PSW = (PSW & ~self.C_mask) | C
        if new_PSW > -1:
            PSW = new_PSW
        self.ram.set_PSW(PSW)

    def set_condition_codes(self, value, B, pattern):
        """set condition codes based on value

        :param value: value to test
        :param B: "B" or "" for Byte or Word
        :param pattern: string matching DEC specification

        pattern looks like the Status Word Condition Codes in the DEC manual.
        Positionally NZVC for Negative, Zero, Overflor, Carry.
        * = conditionally set; - = not affected; 0 = cleared; 1 = set.
        Example: "**0-"
        """
        # set up some masks based on whether this is for Word or Byte
        if B == "B":
            n_mask = mask_byte_msb
            z_mask = mask_byte
            v_mask = mask_byte < 1 & ~mask_byte
            c_mask = mask_byte < 1 & ~mask_byte
        else:
            n_mask = mask_word_msb
            z_mask = mask_word
            v_mask = mask_word < 1 & ~mask_word
            c_mask = mask_word < 1 & ~mask_word  # *** I dion't know how to test for this

        # set unaffected values
        N = -1
        Z = -1
        V = -1
        C = -1

        codenames = "NZVC"

        # check each of the 4 characters
        for i in range(0,3):
            code = pattern[i]
            codename = codenames[i] # get the letter for convenience
            # check for explicit setting
            if code == "0" or code == "1":
                setting = int(code)
                if codename == "N":
                    N = setting
                elif codename == "Z":
                    Z = setting
                elif codename == "V":
                    V = setting
                elif codename == "C":
                    C = setting
            # check for conditional value
            elif code == "*":
                if codename == "N":
                    if (value & n_mask) == n_mask:
                        N = 1
                    else:
                        N = 0
                elif codename == "Z":
                    if (value & z_mask) == 0:
                        Z = 1
                    else:
                        Z = 0
                elif codename == "V":
                    if (value & v_mask) == v_mask:
                        V = 1
                    else:
                        V = 0
                elif codename == "C":
                    if (value & c_mask) == c_mask:  # *** I'm not sure about this
                        C = 1
                    else:
                        C = 0

        self.set_PSW(N=N, Z=Z, V=V, C=C)

    def N(self):
        """negative status bit of PSW"""
        return (self.ram.get_PSW() & self.N_mask) >> 3

    def Z(self):
        """zero status bit of PSW"""
        return (self.ram.get_PSW() & self.Z_mask) >> 2

    def V(self):
        """overflow status bit of PSW"""
        return (self.ram.get_PSW() & self.V_mask) >> 1

    def C(self):
        """carry status bit of PSW"""
        return (self.ram.get_PSW() & self.C_mask)

    def addb(self, b1, b2):
        """add byte, limit to 8 bits, set PSW"""
        result = b1 + b2
        if result > result & self.byte_mask:
            self.ram.set_PSW(V=1)
        if result == 0:
            self.ram.set_PSW(Z=1)
        result = result & self.byte_mask
        return result

    def subb(self, b1, b2):
        """subtract bytes b1 - b2, limit to 8 bits, set PSW"""
        result = b1 - b2
        if result < 0:
            self.ram.set_PSW(N=1)
        result = result & self.byte_mask
        return result

    def addw(self, b1, b2):
        """add words, limit to 16 bits, set PSW"""
        result = b1 + b2
        if result > result & self.word_mask:
            self.ram.set_PSW(V=1)
        if result == 0:
            self.ram.set_PSW(Z=1)
        result = result & self.word_mask
        return result

    def subw(self, b1, b2):
        """subtract words b1 - b2, limit to 16 bits, set PSW"""
        result = b1 - b2
        if result < 0:
            self.ram.set_PSW(N=1)
        result = result & self.word_mask
        return result

class stack:
    def __init__(self, psw, ram, reg):
        print('initializing pdp11Hardware.stack')
        self.psw = psw
        self.ram = ram
        self.reg = reg

    # ****************************************************
    # stack methods for use by instructions
    # ****************************************************
    def push(self, value):
        """push the value onto the stack

        decrement stack pointer, write value to that address
        """
        stack = self.reg.get_sp() - 2
        self.reg.set_sp(stack)
        self.ram.write_word(stack, value)

    def pop(self):
        """pop value off the stack

        get value from stack pointer, increment stack pointer"""
        stack = self.reg.get_sp()
        result = self.ram.read_word(stack)
        self.reg.set_sp(stack + 2)
        return result

class addressModes:
    def __init__(self, psw, ram, reg):
        print('initializing pdp11Hardware.am')
        self.psw = psw
        self.ram = ram
        self.reg = reg

    def addressing_mode_get(self, B, mode_register):
        """copy the value from the location indicated by byte_register"""
        addressmode = (mode_register & 0o70) >> 3
        register = mode_register & 0o07

        print(f'    S addressing_mode_get {B} mode:{oct(addressmode)} reg:{oct(register)}')

        if B == 'B':
            ram_read = self.ram.read_byte
            increment = 1
            b = 'B'
        else:
            ram_read = self.ram.read_word
            increment = 2
            b = ''
        if register == 6 or register == 7:
            increment = 2

        if addressmode == 0:
            print(f'    S mode 0 Register: R{register}: register contains operand')
            operand = self.reg.get(register)
            print(f'    S mode 0 R{register} = operand:{oct(operand)}')
        elif addressmode == 1:
            print(f'    S mode 1 Register Deferred: (R{register}): register contains address of operand')
            address = self.reg.get(register)
            operand = ram_read(address)
            print(f'    S mode 1 @{oct(address)} = operand:{oct(operand)}')
        elif addressmode == 2:
            print(f'    S mode 2 Autoincrement: (R{register})+: register contains address of operand then incremented')
            address = self.reg.get(register)
            operand = ram_read(address)
            self.reg.set(register, self.reg.get(register) + increment)
            print(f'    S mode 2 R{register}={oct(address)} = operand:{oct(operand)}')
        elif addressmode == 3:  # autoincrement deferred
            print(f'    S mode 3 Autoincrement Deferred: @(R{register})+: register contains address of address of operand, then incremented')
            address = self.reg.get(register)
            self.reg.set(register, self.reg.get(register)+2)
            operand = ram_read(address)
            print(f'    S mode 3 @{oct(address)} = operand:{oct(operand)}')
        elif addressmode == 4:  # autodecrement direct
            print(f'    S mode 4 Autodecrement: -(R{register}): register is decremented, then contains address of operand')
            self.reg.set(register, self.reg.get(register) - increment)
            address = self.reg.get(register)
            operand = ram_read(address)
            print(f'    S mode 4 R{register}=@{oct(address)} = operand:{oct(operand)}')
        elif addressmode == 5:  # autodecrement deferred
            print(f'    S mode 5 Autodecrement Deferred: @-(R{register}): register is decremented, then contains address of address of operand')
            self.reg.set(register, self.reg.get(register)-2)
            pointer = self.reg.get(register)
            address = ram_read(pointer)
            operand = ram_read(address)
            print(f'    S mode 5 R{register}=@{oct(address)} = operand:{oct(operand)}')
        elif addressmode == 6:
            print(f'    S mode 6 Index: X(R{register}): value X is added to Register to produce address of operand')
            X = self.ram.read_word(self.reg.get_pc())
            address = self.reg.get(register) + X
            print(f'    S mode 6 X:{oct(X)} address:{oct(address)}')
            operand = ram_read(address)
            print(f'    S mode 6 R{register}=@{oct(address)} = operand:{oct(operand)}')
        elif addressmode == 7:  # index deferred
            print(f'    S mode 7 Index Deferred: @X(R{register}): value X is added to Register then used as address of address of operand')
            X = self.ram.read_word(self.reg.get_pc()+2)
            pointer = self.reg.get(register) + X
            address = ram_read(pointer)
            operand = ram_read(address)
            print(f'    S mode 7 R{register}=@{oct(address)} = operand:{oct(operand)}')

        if (addressmode == 6 or addressmode == 7) and register != 7:
            self.reg.set_pc(self.reg.get_pc()+2, "addressing_mode_get")

        return operand


    def addressing_mode_set(self, B, mode_register, result):
        """copy the result into the place indicated by mode_register

        Parameters:
            B: 'B' or ''
            mode_register: SS or DD
            result: what to store there
        """
        print(f'    D addressing_mode_set("{B}", {oct(mode_register)}, {oct(result)})')

        addressmode = (mode_register & 0o70) >> 3
        register = mode_register & 0o07
        print(f'    D addressing_mode_set {B} mode:{oct(addressmode)} reg:{register} result:{oct(result)}')

        if B == 'B':
            ram_read = self.ram.read_byte
            ram_write = self.ram.write_byte
            increment = 1
        else:
            ram_read = self.ram.read_word
            ram_write = self.ram.write_word
            increment = 2
        if register == 6 or register == 7:
            increment = 2

        if addressmode == 0:  # register direct
            print(f'    D mode 0 register: R{register}: register contains operand')
            self.reg.set(register, result)
            print(f'    D mode 0 R{register} = operand:{oct(result)}')
        if addressmode == 1:  # register deferred
            print(f'    D mode 1 register deferred: (R{register}): register contains address of operand')
            address = self.reg.get(register)
            ram_write(address, result)
            print(f'    D mode 1 @{oct(address)} = operand:{oct(result)}')
        elif addressmode == 2:  # autoincrement direct - R has address, then increment
            print(f'    D mode 2 autoincrement: (R{register})+: register contains address of operand then incremented')
            address = self.reg.get(register)
            self.reg.set(register, self.reg.get(register) + increment)
            ram_write(address, result)
            print(f'    D mode 2 R{register}={oct(address)} = operand:{oct(result)}')
        elif addressmode == 3:  # autoincrement deferred - R has handle, then increment
            print(f'    D mode 3 autoincrement deferred: @(R{register})+: register contains address of address of operand, then incremented')
            pointer = self.reg.get(register)
            self.reg.set(register, self.reg.get(register)+2)
            address = self.ram.read_word(pointer)
            ram_write(address, result)
            print(f'    D mode 3 @{oct(address)} = operand:{oct(result)}')
        elif addressmode == 4:  # autodecrement direct - decrement, then R has address
            print(f'    D mode 4 autodecrement: -(R{register}): register is decremented, then contains address of operand')
            self.reg.set(register, self.reg.get(register) - increment)
            address = self.reg.get(register)
            ram_write(address, result)
            print(f'    D mode 4 R{register}=@{oct(address)} = operand:{oct(result)}')
        elif addressmode == 5:  # autodecrement deferred - decrement, then R has handle
            print(f'    D mode 5 autodecrement deferred: @-(R{register}): register is decremented, then contains address of address of operand')
            self.reg.set(register, self.reg.get(register)-2)
            pointer = self.reg.get(register)
            address = self.ram.read_word(pointer)
            ram_write(address, result)
            print(f'    D mode 5 R{register}=@{oct(address)} = operand:{oct(result)}')
        elif addressmode == 6:  # index
            print(f'    D mode 6 index: X(R{register}): value X is added to Register to produce address of operand')
            nextword = self.ram.read_word(self.reg.get_pc())
            address = self.reg.get(register) + nextword
            print(f'    D mode 6 index R{register}={oct(address)} <- {oct(result)}')
            ram_write(address, result)
            print(f'    D mode 6 R{register}=@{oct(address)} = operand:{oct(result)}')
        elif addressmode == 7:  # index deferred
            print(f'    D mode 7 index deferred: @X(R{register}): value X is added to Register then used as address of address of operand')
            nextword = self.ram.read_word(self.reg.get_pc())
            address = self.reg.get(register) + nextword
            address = ram_read(address)
            ram_write(address, result)
            print(f'    D mode 7 R{register}=@{oct(address)} = operand:{oct(result)}')

        if (addressmode == 6 or addressmode == 7) and register != 7:
            self.reg.set_pc(self.reg.get_pc()+2, "addressing_mode_set")
