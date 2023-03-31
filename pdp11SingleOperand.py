"""pdp11SingleOperand.py single oprand instructions"""

from pdp11psw import psw
from pdp11ram import ram
from pdp11reg import reg
from pdp11AddressMode import am

# masks for accessing words and bytes
mask_byte = 0o000377
mask_word = 0o177777
mask_word_msb = 0o100000
mask_byte_msb = 0o000200

"""self.single_operand_instructions
    :param instruction: opcode
    :param dest: address
    :param operand: operand
    :param B: 'B' for byte instruction, '' for word
    :param mask:
    :param maskmsb: 
"""

class sopr:
    def __init__(self, psw, ram, reg):
        print('initializing pdp11sopr')
        self.psw = psw
        self.ram = ram
        self.reg = reg
        self.am = am(psw, ram, reg)

        self.single_operand_instructions = {}
        self.single_operand_instructions[0o000100] = self.JMP
        self.single_operand_instructions[0o000300] = self.SWAB
        self.single_operand_instructions[0o005000] = self.CLR
        self.single_operand_instructions[0o005100] = self.COM
        self.single_operand_instructions[0o005200] = self.INC
        self.single_operand_instructions[0o005300] = self.DEC
        self.single_operand_instructions[0o005400] = self.NEG
        self.single_operand_instructions[0o005500] = self.ADC
        self.single_operand_instructions[0o005600] = self.SBC
        self.single_operand_instructions[0o005700] = self.TST
        self.single_operand_instructions[0o006000] = self.ROR
        self.single_operand_instructions[0o006100] = self.ROL
        self.single_operand_instructions[0o006200] = self.ASR
        self.single_operand_instructions[0o006300] = self.ASL
        #self.single_operand_instructions[0o006400] = self.MARK
        #self.single_operand_instructions[0o006500] = self.MFPI
        #self.single_operand_instructions[0o006600] = self.MTPI
        self.single_operand_instructions[0o006700] = self.SXT
        self.single_operand_instructions[0o105000] = self.CLR # CLRB
        self.single_operand_instructions[0o105100] = self.COM # COMB
        self.single_operand_instructions[0o105200] = self.INC # INCB
        self.single_operand_instructions[0o105300] = self.DEC # DECB
        self.single_operand_instructions[0o105400] = self.NEG # NEGB
        self.single_operand_instructions[0o105500] = self.ADC  # ADCB
        self.single_operand_instructions[0o105600] = self.SBC  # SBCB
        self.single_operand_instructions[0o105700] = self.TST  # TSTB
        self.single_operand_instructions[0o106000] = self.ROR  # RORB
        self.single_operand_instructions[0o106100] = self.ROL  # ROLB
        self.single_operand_instructions[0o106200] = self.ASR  # ASRB
        self.single_operand_instructions[0o106300] = self.ASL  # ASLB
        self.single_operand_instructions[0o106500] = self.MFPD
        self.single_operand_instructions[0o106600] = self.MTPD

    # ****************************************************
    # Single-Operand instructions -
    # 00 50 DD - 00 77 DD
    # 10 50 DD - 10 77 DD
    # ****************************************************

    def JMP(self, instruction, dest, operand, B, mask, maskmsb):
        """00 01 DD JMP jump 4-56"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} JMP {oct(dest)} {oct(operand)}')
        self.reg.set_pc(operand, 'JMP')
        return self.reg.get_pc()

    def SWAB(self, instruction, dest, operand, B, mask, maskmsb):
        """00 03 DD Swap Bytes 4-17"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} SWAB {oct(dest)} {oct(operand)}')
        self.reg.inc_pc()
        result = (operand & 0xFF00) << 8 + (operand & 0x00FF) >> 8
        self.reg.inc_pc()
        return result

    def CLR(self, instruction, dest, operand, B, mask, maskmsb):
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} CLR{B} {oct(dest)} {oct(operand)}')
        self.reg.inc_pc()
        result = 0o0
        self.psw.set_PSW(N=0, Z=1, V=0, C=0)
        self.reg.inc_pc()
        return result

    def COM(self, instruction, dest, operand, B, mask, maskmsb):
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} COM{B} {oct(dest)} {oct(operand)}')
        self.reg.inc_pc("COM{B}")
        result = ~operand & mask
        n = 0
        if result & maskmsb == maskmsb:
            n = 1
        z = 0
        if result == 0:
            z = 1
        self.psw.set_PSW(N=n, Z=z, V=0, C=1)
        return result

    def INC(self, instruction, dest, operand, B, mask, maskmsb):
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} INC{B} {oct(dest)} {oct(operand)}')
        self.reg.inc_pc()
        # *** this is incomplete as words need their own special little operators
        result = operand + 1 & mask_word
        n = 0
        if result < 0:
            n = 1
        z = 0
        if result == 0:
            z = 1
        v = 0
        if dest == 0o077777: # what the fuck am I doing here?
            v = 1
        self.psw.set_PSW(N=n, Z=z, V=v)
        return result

    def DEC(self, instruction, dest, operand, B, mask, maskmsb):
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} DEC{B} {oct(dest)} {oct(operand)}')
        self.reg.inc_pc()
        # *** this is incomplete as words need their own special little operators
        result = operand - 1 & mask_byte
        n = 0
        if result < 0:
            n = 1
        z = 0
        if result == 0:
            z = 1
        v = 0
        if dest == 0o100000: # what the fuck am I doing here?
            v = 1
        self.psw.set_PSW(N=n, Z=z, V=v)
        return result

    def NEG(self, instruction, dest, operand, B, mask, maskmsb):
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} NEG{B} {oct(dest)} {oct(operand)}')
        self.reg.inc_pc()
        result = -operand & mask
        return result

    def ADC(self, instruction, dest, operand, B, mask, maskmsb):
        """Add Carry"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} ADC{B} {oct(dest)} {oct(operand)}')
        self.reg.inc_pc()
        result = dest + self.psw.C()
        n = 0
        if result < 0:
            n = 1
        z = 0
        if result == 0:
            z = 1
        v = 0
        if dest == 0o077777 and self.psw.C() == 1: # what the fuck am I doing here?
            v = 1
        c = 0
        if dest == 0o077777 and self.psw.C() == 1: # what the fuck am I doing here?
            c = 1
        self.psw.set_PSW(N=n, Z=z, V=v, C=c)
        return result

    def SBC(self, instruction, dest, operand, B, mask, maskmsb):
        """subtract Carry"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} SBC{B} {oct(dest)} {oct(operand)}')
        self.reg.inc_pc()
        result = dest - operand
        n = 0
        if result < 0:
            n = 1
        z = 0
        if result == 0:
            z = 1
        v = 0
        if dest == 0o1000000 and self.psw.C() == 1: # what the fuck am I doing here?
            v = 1
        c = 0
        if dest == 0o0 and self.psw.C() == 1: # what the fuck am I doing here?
            c = 1
        self.psw.set_PSW(N=n, Z=z, V=v, C=c)
        return result

    def TST(self, instruction, dest, operand, B, mask, maskmsb):
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} TST{B} {oct(dest)} {oct(operand)}')
        self.reg.inc_pc()
        result = operand
        n = 0
        if result & mask_word == mask_word:
            n = 1
        z = 0
        if result == 0:
            z = 1
        self.psw.set_PSW(N=n, Z=z, V=0, C=1)
        return result

    def ROR(self, instruction, dest, operand, B, mask, maskmsb):
        """ROR rotate right"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} ROR{B} {oct(dest)} {oct(operand)}')
        self.reg.inc_pc()
        result = operand >> 1
        n = 0
        if result & maskmsb == maskmsb:
            n = 1
        z = 0
        if result == 0:
            z = 1
        self.psw.set_PSW(N=n, Z=z, V=0, C=1)
        return result

    def ROL(self, instruction, dest, operand, B, mask, maskmsb):
        """ROL rotate left"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} ROR{B} {oct(dest)} {oct(operand)}')
        self.reg.inc_pc()
        result = operand << 1
        n = 0
        if result & maskmsb == maskmsb:
            n = 1
        z = 0
        if result == 0:
            z = 1
        self.psw.set_PSW(N=n, Z=z, V=0, C=1)
        return result

    def ASR(self, instruction, dest, operand, B, mask, maskmsb):
        """ASR arithmetic shift right"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} ASR{B} {oct(dest)} {oct(operand)}')
        self.reg.inc_pc()
        result = operand >> 1
        n = 0
        if result & maskmsb == maskmsb:
            n = 1
        z = 0
        if result == 0:
            z = 1
        self.psw.set_PSW(N=n, Z=z, V=0, C=1)
        return result

    def ASL(self, instruction, dest, operand, B, mask, maskmsb):
        """ASL arithmetic shift left"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} ASL{B} {oct(dest)} {oct(operand)}')
        self.reg.inc_pc()
        result = operand << 1
        n = 0
        if result & maskmsb == maskmsb:
            n = 1
        z = 0
        if result == 0:
            z = 1
        self.psw.set_PSW(N=n, Z=z, V=0, C=1)
        return result

    def SXT(self, instruction, dest, operand, B, mask, maskmsb):
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} SXT{B} {oct(dest)} {oct(operand)}')
        self.reg.inc_pc()
        # *** this is incomplete as words need their own special little operators
        if self.psw.N() == 0:
            result = 0
        else:
            result = -1
        z = 0
        if result == 0:
            z = 1
        self.psw.set_PSW(Z=z)
        return result

    def MFPD(self, instruction, dest, operand, B, mask, maskmsb):
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} MFPD{B} {oct(dest)} {oct(operand)} NOT IMPLEMENTED')
        self.reg.inc_pc()
        result = 0

    def MTPD(self, instruction, dest, operand, B, mask, maskmsb):
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} MTPD{B} {oct(dest)} {oct(operand)} NOT IMPLEMENTED')
        self.reg.inc_pc()
        result = 0

    def is_single_operand(self, instruction):
        """Using instruction bit pattern, determine whether it's a single-operand instruction"""
        # 15  12 10  876 543 210
        #  * 000 101 *** *** ***
        #  * 000 110 *** *** ***
        # bit 15 can be 1 or 0
        # bits 14,13,12 must be 0
        # bits 11,10,9 must be 5 or 6
        # bits 8,7,6 can be anything
        # bits 5-0 can be anything
        # 0o000301 is one of these
        # 0 000 000 101 *** ***
        #print(f'    is_single_operand({type(instruction)} {oct(instruction)})')
        bits_14_13_12 = instruction & 0o070000 == 0o000000
        bits_11_10_9 = instruction & 0o007000 in [0o006000, 0o005000]
        isJMP = instruction & 0o000700 == 0o000100
        isSWAB = instruction & 0o000700 == 0o000300
        #print(f'    is_single_operand {bits_14_13_12} {bits_11_10_9} {isSWAB}')
        return (bits_14_13_12 and bits_11_10_9) or isSWAB or isJMP

    def do_single_operand(self, instruction):
        """dispatch a single-operand opcode"""
        # parameter: opcode of form * 000 1** *** *** ***
        # single operands
        # 15-6 opcode
        # 15 is 1 to indicate a byte instruction
        # 15 is 0 to indicate a word instruction
        # 5-0 dst
        if (instruction & 0o100000) == 0o100000:
            B = 'B'
            mask = mask_byte
            maskmsb = mask_byte_msb
        else:
            B = ''
            mask = mask_word
            maskmsb = mask_word_msb
        opcode = (instruction & 0o107700)
        source = instruction & 0o000077
        source_value = self.am.addressing_mode_get(B, source)

        self.reg.log_registers()

        run = True
        try:
            print(f'    {oct(self.reg.get_pc())} {oct(instruction)} single_operand opcode:{oct(opcode)} source_value:{oct(source_value)}')
            result = self.single_operand_instructions[opcode](instruction, source_value, source_value, B, mask, maskmsb)
            self.am.addressing_mode_set(B, source_value, result)
        except KeyError:
            print(f'    {oct(self.reg.get_pc())} {oct(instruction)} single_operandmethod {oct(opcode)} was not implemented')
            result = 0
            run = False

        return run