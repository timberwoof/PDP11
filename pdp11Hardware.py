"""PDP11 RAM, Registers, PSW"""

import sys

# masks for accessing words and bytes
mask_word = 0o177777
mask_word_msb = 0o100000
mask_byte_msb = 0o000200
mask_low_byte = 0o000377
mask_high_byte = 0o177400

class ram:
    # overall size of memory: 64kB
    top_of_memory = 0o177777
    # 16 bits   0o177777 = 0x0000FFFF
    # 18 bits   0o777777 = 0x0003FFFF
    # 22 bits 0o17777777 = 0x003FFFFF

    # the actual array for simuating RAM.
    memory = bytearray(top_of_memory + 1)
    # +1 because I want to be able to index self.top_of_memory

    # PSW is stored here
    PSW_address = top_of_memory - 1  # 0o377776
    Stack_Limit_Register = top_of_memory - 3  # 0o377774
    # the io page is the top 4kB of memory
    io_space = top_of_memory - 0o1000

    def __init__(self):
        print('initializing pdp11Hardware ram')

        # set up basic memory boundaries

        # set up the vector space
        # the bottom area is io device handler vectors
        #self.top_of_vector_space = 0o274
        #for address in range(0o0, self.top_of_vector_space):
        #    self.write_byte(address, 0o277)
        # set up the io page space so it's always ready
        #for address in range(self.io_space, self.top_of_memory):
        #    self.write_byte(address, 0o111)

        # set up always-ready i/o device status words
        #self.write_word(self.TKS, 0o000000)
        #self.write_word(self.TPS, 0b0000000011000000) # always xmit ready and interrupt enabled

        print(f'top_of_memory:{oct(self.top_of_memory)}')
        print(f'PSW_address:{oct(self.PSW_address)}')
        # psw class handles updating PSW in ram.
        # Only a pdp11 program should read this from ram.
        print(f'io_space:{oct(self.io_space)}')

        # io map is two dictionaries of addresses and methods
        self.iomap_readers = {}
        self.iomap_writers = {}

    def register_io_writer(self, device_address, method):
        print(f'register_io_writer({oct(device_address)}, {method.__name__})')
        self.iomap_writers[device_address] = method

    def register_io_reader(self, device_address, method):
        print(f'register_io_reader({oct(device_address)}, {method.__name__})')
        self.iomap_readers[device_address] = method

    def write_byte(self, address, data):
        """write a byte to memory.
        address can be even or odd"""
        data = data & mask_low_byte
        if address in self.iomap_writers.keys():
            print(f'write_byte io({oct(address)}, {oct(data)})')
            self.iomap_writers[address](data)
        else:
            print(f'write_byte({oct(address)}, {oct(data)})')
            self.memory[address] = data

    def read_byte(self, address):
        """Read one byte of memory."""
        if address in self.iomap_readers.keys():
            result = self.iomap_readers[address]()
            #print(f'read_byte io({oct(address)} returns {oct(result)}')
        else:
            result = self.memory[address]
            #print(f'read_byte ({oct(address)} returns {oct(result)}')
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
            hi = (data & mask_high_byte) >> 8  # 1 111 111 100 000 000
            lo = data & mask_low_byte  # 0 000 000 011 111 111
            # print(f'hi:{oct(hi)} lo:{oct(lo)}')
            self.memory[address + 1] = hi
            self.memory[address] = lo
            # print(f'hi:{oct(memory[address])} lo:{oct(memory[address-1])}')

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

#    mask_low_byte = 0o000277
#    mask_word = 0o177777
#    mask_byte_msb = 0o000200
#    mask_word_msb = 0o100000
# 16 bits   0o177777 = 0x0000FFFF
# 18 bits   0o777777 = 0x0003FFFF
# 22 bits 0o17777777 = 0x003FFFFF

    def dump(self, start, stop):
        """Print out memory from a nice address before start to a nice address after stop.
        Nice means rounded off to a bunch of bytes convenient to display on a line.
        Print a row as octal Words followed by octal Bytes followed by ascii interpretation
        Octal word is 7 chars with space. Octal byte is 4 chars with space. acii byte is 1 char. 12 chars
        :param start:
        :param stop:
        :return:
        """
        display_bytes = 8 # display this may bytes across the line
        start = start & ~mask_low_byte
        print(f'dump({oct(start)}, {oct(stop)})')

        print_line = ""
        for row_address in range(start, stop, display_bytes):
            print_line =  ("{0:o}".format(row_address)).rjust(6, "O")+" "  #row_address
            for word_address in range(row_address, row_address+display_bytes, 2):
                print_line = print_line + ("{0:o}".format(self.read_word(word_address))).rjust(6, "O")+" " #self.read_word(word_address)
            print_line = print_line + " "
            for byte_address in range(row_address, row_address+display_bytes):
                print_line = print_line + ("{0:o}".format(self.read_byte(byte_address))).rjust(3, "O")+" " #self.read_byte(byte_address)
            print_line = print_line + " "
            for byte_address in range(row_address, row_address+display_bytes):
                byte = self.read_byte(byte_address)
                if byte in range(16,254):
                    char = chr(byte)
                else:
                    char = "."
                print_line = print_line + char
            print(print_line)




class registers:
    def __init__(self):
        print('initializing pdp11Hardware registers')
        self.registermask = 0o07
        self.SP = 0o06  # R6 is frequentluy referred to as the stack pointer
        self.PC = 0o07  # R7 is the program counter
        # During operand decoding, PC points to the instruction being decoded.
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
        self.registers[register & self.registermask] = value & mask_word

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
        newpc = value & mask_word
        self.registers[self.PC] = newpc
        print(f'    setpc R7<-{oct(newpc)} {whocalled}')

    def set_pc_2x_offset(self, offset, whocalled=''):
        """set program counter to 2x offset"""
        waspc = self.registers[self.PC]
        newpc = self.registers[self.PC] + 2 * (offset & mask_low_byte)
        self.registers[self.PC] = newpc
        print(f'    set_pc_2x_offset R7<-{oct(newpc)} (was:{oct(waspc)}) {whocalled}')

    def get_sp(self):
        """get stack pointer

        :return: stack pointer"""
        return self.registers[self.SP]

    def set_sp(self, value, whocalled=''):
        """set stack pointer

        :return: new stack pointer"""
        #wassp =  self.registers[self.PC]
        newsp = value & mask_word
        self.registers[self.SP] = newsp
        #print(f'{oct(wassp)} setpc {oct(newsp)}')
        return newsp

class psw:
    """PDP11 PSW"""

    def __init__(self, ram):
        """initialize PDP11 PSW"""
        print('initializing pdp11Hardware psw')
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
        # This class keeps the deinitive version of the PSW.
        # When it changes, this class sets it into RAM.
        self.PSW = 0o0

        self.c_mode_mask = 0o140000
        self.p_mode_mask = 0o030000
        self.mode_mask = 0o170000
        self.priority_mask = 0o000340
        self.trap_mask = 0o000020

        # condition codes
        self.N_mask = 0o000010  # Negative
        self.Z_mask = 0o000004  # Zero
        self.V_mask = 0o000002  # Overflow
        self.C_mask = 0o000001  # Carry

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
        if PSW > -1:
            self.PSW = PSW
        if mode > -1:
            oldmode = (self.PSW & self.mode_mask)
            self.PSW = (self.PSW & ~self.c_mode_mask) | (mode << 14) | (oldmode >> 2)
        if priority > -1:
            self.PSW = (self.PSW & ~self.priority_mask) | (priority << 5)
        if trap > -1:
            self.PSW = (self.PSW & ~self.trap_mask) | (trap << 4)
        if N > -1:
            self.PSW = (self.PSW & ~self.N_mask) | (N << 3)
        if Z > -1:
            self.PSW = (self.PSW & ~self.Z_mask) | (Z << 2)
        if V > -1:
            self.PSW = (self.PSW & ~self.V_mask) | (V << 1)
        if C > -1:
            self.PSW = (self.PSW & ~self.C_mask) | C
        self.ram.write_word(self.ram.PSW_address, self.PSW)

    def set_condition_codes(self, B, value, pattern):
        """set condition codes based on value and pattern

        :param B: "B" or "" for Byte or Word
        :param value: value to test
        :param pattern: string matching DEC specification like --*1

        pattern looks like the Status Word Condition Codes in the DEC manual.
        Positionally NZVC for Negative, Zero, Overflor, Carry.
        * = conditionally set; - = not affected; 0 = cleared; 1 = set.
        Example: "**0-"
        """
        print(f'    set_condition_codes({B}, {oct(value)}, {pattern})')

        # set up some masks based on whether this is for Word or Byte
        if B == 'B':
            n_mask = mask_byte_msb
            z_mask = mask_low_byte
            v_mask = mask_low_byte < 1 & ~mask_low_byte
            c_mask = mask_low_byte < 1 & ~mask_low_byte
        else:
            n_mask = mask_word_msb
            z_mask = mask_word
            v_mask = mask_word < 1 & ~mask_word
            c_mask = mask_word < 1 & ~mask_word  # *** I dion't know how to test for this

        codition_code_masks = [n_mask, z_mask, v_mask, c_mask]
        condition_codes = [0,0,0,0]
        # check each of the 4 characters
        for i in range(0,4):
            code = pattern[i]
            the_mask = codition_code_masks[i]
            # check for explicit setting
            if code == "0" or code == "1":
                condition_codes[i] = int(code)
            # check for conditional value
            elif code == "*":
                if (value & the_mask) == the_mask:
                    condition_codes[i] = 1
                else:
                    condition_codes[i] = 0
            # check for unaffected value
            elif code == "-":
                value = self.PSW & the_mask
                if value > 0:
                    condition_codes[i] = 1
                else:
                    condition_codes[i] = 0
        # Put the codes into the PSW
        self.set_PSW(N=condition_codes[0], Z=condition_codes[1], V=condition_codes[2], C=condition_codes[3])

    def N(self):
        """negative status bit of PSW"""
        return (self.PSW & self.N_mask) >> 3

    def Z(self):
        """zero status bit of PSW"""
        return (self.PSW & self.Z_mask) >> 2

    def V(self):
        """overflow status bit of PSW"""
        return (self.PSW & self.V_mask) >> 1

    def C(self):
        """carry status bit of PSW"""
        return (self.PSW & self.C_mask)

    def addb(self, b1, b2):
        """add byte, limit to 8 bits, set PSW"""
        result = b1 + b2
        if result > (result & mask_low_byte):
            self.set_PSW(V=1)
        if result == 0:
            self.set_PSW(Z=1)
        result = result & mask_low_byte
        return result

    def subb(self, b1, b2):
        """subtract bytes b1 - b2, limit to 8 bits, set PSW"""
        result = b1 - b2
        if result < 0:
            self.set_PSW(N=1)
        result = result & mask_low_byte
        return result

    def addw(self, b1, b2):
        """add words, limit to 16 bits, set PSW"""
        result = b1 + b2
        if result > (result & mask_word):
            self.set_PSW(V=1)
        if result == 0:
            self.set_PSW(Z=1)
        result = result & mask_word
        return result

    def subw(self, b1, b2):
        """subtract words b1 - b2, limit to 16 bits, set PSW"""
        result = b1 - b2
        if result < 0:
            self.set_PSW(N=1)
        result = result & mask_word
        return result

class stack:
    def __init__(self, psw, ram, reg):
        print('initializing pdp11Hardware stack')
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
    '''Implements the 6 standrad address modes of the PDP11 instruction set.
    Every instruction that needs to set these up calls addressing_mode_get to get the praneter,
    addressing_mode_jmp to implement program counter jmps, and
    addressing_mode_set to hndle addres smodes for destination register'''
    def __init__(self, psw, ram, reg):
        print('initializing pdp11Hardware addressModes')
        self.psw = psw
        self.ram = ram
        self.reg = reg

    def fix_sign(selfself, word):
        """fix a negative word so it will work with python math"""
        if word & mask_word_msb:
            more_bits = sys.maxsize & ~mask_word
            field = sys.maxsize - (word & mask_word | more_bits) + 1
            result = -field
        else:
            result = word
        return result

    def add_word(self, a, b):
        """add two-byte words with sign handling"""
        #print(f'add_word({oct(a)}, {oct(b)})  mask_word_msb:{oct(mask_word_msb)}')
        result = self.fix_sign(a) + self.fix_sign(b)
        return result

    def addressing_mode_get(self, B, mode_register):
        """copy the value from the location indicated by byte_register

        :param B: "W" for word, "B" for byte
        :param mode_register: bits of opcode that contain address mode and register number
        :return: the parameter
        """
        # B sets the byte/word mode. It is empty for word nd 'B' for byte mode.
        # Thus it is useful as the mode indicator and to label instructions in log correctly.
        # mode_register contains the six bits that specify the mode and the register.
        # This could be for either of the two parameters of an SSDD instruction.
        # PC points to NEXT word in memory after the instruction
        addressmode = (mode_register & 0o70) >> 3
        register = mode_register & 0o07

        print(f'    S addressing_mode_get({B}, {oct(mode_register)}) address mode:{oct(addressmode)} register:{oct(register)}')

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
            operand = ram_read(address)
            self.reg.set(register, self.reg.get(register) + increment)
            print(f'    S mode 3 @{oct(address)} = operand:{oct(operand)}')
        elif addressmode == 4:  # autodecrement direct
            print(f'    S mode 4 Autodecrement: -(R{register}): register is decremented, then contains address of operand')
            self.reg.set(register, self.reg.get(register) - increment)
            address = self.reg.get(register)
            operand = ram_read(address)
            print(f'    S mode 4 R{register}=@{oct(address)} = operand:{oct(operand)}')
        elif addressmode == 5:  # autodecrement deferred
            print(f'    S mode 5 Autodecrement Deferred: @-(R{register}): register is decremented, then contains address of address of operand')
            self.reg.set(register, self.reg.get(register) - 2)
            pointer = self.reg.get(register)
            address = ram_read(pointer)
            operand = ram_read(address)
            print(f'    S mode 5 R{register}=@{oct(address)} = operand:{oct(operand)}')
        elif addressmode == 6: # index
            X = self.ram.read_word(self.reg.get_pc())
            self.reg.set_pc(self.reg.get_pc() + 2, "address mode 6")
            print(f'    S mode 6 Index: X(R{register}): immediate value {oct(X)} is added to R{register} to produce address of operand')
            address = self.add_word(self.reg.get(register), X)
            print(f'    S mode 6 X:{oct(X)} address:{oct(address)}')
            operand = ram_read(address)
            print(f'    S mode 6 R{register}=@{oct(address)} = operand:{oct(operand)}')
        elif addressmode == 7:  # index deferred
            X = self.ram.read_word(self.reg.get_pc())
            self.reg.set_pc(self.reg.get_pc() + 2, "address mode 7")
            print(f'    S mode 7 Index Deferred: @X(R{register}): immediate value {oct(X)} is added to R{register} then used as address of address of operand')
            pointer = self.add_word(self.reg.get(register), X)
            address = ram_read(pointer)
            print(f'    S mode 7 X:{oct(X)} pointer:{oct(pointer)} address:{oct(address)}')
            operand = ram_read(address)
            print(f'    S mode 7 R{register}=@{oct(address)} = operand:{oct(operand)}')

        print(f'    addressing_mode_get returns operand:{operand}')
        return operand

    # https://retrocomputing.stackexchange.com/questions/9248/pdp-11-jmp-and-jsr-how-was-the-target-specified
    # Mode 0 - illegal
    # Mode 1, Register Indirect, jumps to wherever the register points - JMP (R1)
    # Mode 2 (Autoincrement) becomes immediate (Not useful for JMP/JSR) -  ADC #label
    # Mode 3 (Autoincrement Indirect) becomes Absolute - JMP @#label
    # Mode 3, Autoincrement Indirect, jumps to address contained in a word addressed by the register and increments the register by two - JMP @(R1)+ (*3)
    # Mode 6 (Indexed) is the already mentioned Relative -  JMP label
    # Mode 6, Indexed, jumps to the result of adding a 16 bit word to the register specified - JMP 20(PC)
    # Mode 7, Index Indirect, jumps to address contained in a word addressed by adding a 16 bit word to the register specified - JMP @20(PC)
    # section 5 of the MACRO-11 manual

    # PDP-11 IAS/RSX-11 MACRO-11 Reference Manual:
    # See page B-2 for mores and for JMP
    # In the autoincrement mode, both the JMP and JSR instructions autoincrement the register before its
    # use on the PDP-11/40, but not on the PDP-11/45 o r 11/10.
    #
    # In double operand instructions having the addressing form Rn, (Rn) + or Rn, -(Rn),
    # # where the source and destination registers are the same, the source operand is evaluated as the autoincremented
    # or autodecremented value, but the destination register, at the time it is used, still contains the originally-intended effective address.
    # In the following example, as executed on the PDP-11/40, Register 0 originally contains 100(8):
    # MOV 100,R0
    # MOV R0,(R0)+  ; 102 is moved to R0
    # MOV R0,-(R0)  ; 75 is moved to R0
    # avoid these forms because they don't always work the same
    # MOV #100,R0  ; assembles into two words.
    #       ;Processor fetches MOV and increments PC.
    #       ;Processor fetches 100 and increments PC.

    # Questions on MACRO-11
    # It is source,target
    # MOV #100,R0 ; move 100 into Register 0
    # can you have two autoincrement or autodecrement addresses?

    # Branch instructions

    def addressing_mode_jmp(self, mode_register):
        """copy the value from the location indicated by byte_register"""
        # See page A-11 pf pdp11/40.pdf

        addressmode = (mode_register & 0o70) >> 3
        register = mode_register & 0o07

        print(f'    S addressing_mode_get mode:{oct(addressmode)} reg:{oct(register)}')

        run = True
        if addressmode == 0:
            print(f'    S mode 07: JMP direct illegal register address')
            run = False
        elif addressmode == 1:
            print(f'    S mode 17: JMP register deferred. R{register} contains the address of the operand. Weird.')
            address = self.reg.get(register)
            operand = self.ram.read_word(address)
        elif addressmode == 2:
            print(f'    S mode 27: JMP immediate: The expression E is the operand itself.')
            operand = self.ram.read_word(self.reg.get(7)+2)
        elif addressmode == 3:
            print(f'    S mode 37: JMP absolute: The expression E is the address of the operand.')
            address = self.ram.read_word(self.reg.get(7)+2)
            operand = self.ram.read_word(address)
        elif addressmode == 4:
            # The contents of the register specified as (ER) are decremented
            # before being used as the address of the operand. Weird.
            print(f'    S mode 47: Autodecrement. Weird.')
            self.reg.set(register, self.reg.get(register)-2)
            address = self.reg.get(register)
            operand = self.ram.read_word(address)
        elif addressmode == 5:
            # The contents of the register specified a s (ER) are decremented
            # before being used as the pointer to the address of the operand.
            print(f'    S mode 57: Autodecrement deferred. Weird.')
            self.reg.set(register, self.reg.get(register)-2)
            pointer = self.reg.get(register)
            address = self.ram.read_word(pointer)
            operand = self.ram.read_word(address)
        elif addressmode == 6:
            # The expression E, plus the contents of the PC,
            # yield the effective address of the operand.
            X = self.ram.read_word(self.reg.get_pc()+2)
            print(f'    S mode 67: JMP relative. immediate value {oct(X)} plus PC gets address.')
            address = self.add_word(self.reg.get(register), X)
            operand = self.ram.read_word(address)
        elif addressmode == 7:
            # The expression E, plus the contents of the PC
            # yield a pointer to the effective address of the operand.
            X = self.ram.read_word(self.reg.get_pc()+2)
            print(f'    S mode 77: JMP relative deferred. immediate value {oct(X)} plus PC gets pointer to address.')
            pointer = self.add_word(self.reg.get(register), X)
            address = self.ram.read_word(pointer)
            operand = self.ram.read_word(address)

        print(f'    addressmode:{addressmode}  register:{register}')
        if (addressmode == 6 or addressmode == 7) and register != 7:
            self.reg.set_pc(self.reg.get_pc()+2, "addressing_mode_set")
            print(f'    D increment PC to {oct(self.reg.get_pc())}')

        print(f'    addressing_mode_jmp returns run:{run}, operand:{operand}  ')
        self.reg.set(register, operand)
        return run, operand

    def addressing_mode_set(self, B, mode_register, result):
        """copy the result into the place indicated by mode_register

        Parameters:
            B: 'B' or ''
            mode_register: SS or DD
        """
        print(f'    D addressing_mode_set("{B}", '
              f'mode_register:{oct(mode_register)}, result:{oct(result)})')

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
            PC = self.reg.get_pc()
            X = self.ram.read_word(self.reg.get_pc()+2)
            print(f'    D mode 6 index: X(R{register}): immediate value @{oct(PC+2)}={oct(X)} is added to R{register} to produce address of operand')
            address = self.add_word(self.reg.get(register), X)
            operand = self.ram.read_word(address)
            ram_write(operand, result)
        elif addressmode == 7:  # index deferred
            X = self.ram.read_word(self.reg.get_pc()+2)
            print(f'    D mode 7 index deferred: @X(R{register}): immediate value {oct(X)} is added to R{register} then used as address of address of operand')
            pointer = self.add_word(self.reg.get(register), X)
            address = self.ram.read_word(pointer)
            ram_write(address, result)
            print(f'    D mode 7 R{register}=@{oct(address)} = operand:{oct(result)}')

        if (addressmode == 6 or addressmode == 7) and register != 7:
            self.reg.set_pc(self.reg.get_pc()+2, "addressing_mode_set") # should we do this?
            print(f'    D increment PC to {oct(self.reg.get_pc())}')

    def addressing_mode_set_jmp(self, result):
        self.reg.set(7, result);
        print(f'    D 7 set PC to {oct(result)}')