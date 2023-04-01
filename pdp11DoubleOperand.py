"""pdp11DoubleOperand.py double operand instructions"""

from pdp11psw import psw
from pdp11ram import ram
from pdp11reg import reg
from pdp11AddressMode import am

class dopr:
    def __init__(self, psw, ram, reg):
        print('initializing pdp11DoubleOperand')
        self.psw = psw
        self.ram = ram
        self.reg = reg
        self.am = am(psw, ram, reg)

        self.double_operand_RSS_instructions = {}
        self.double_operand_RSS_instructions[0o070000] = self.MUL
        self.double_operand_RSS_instructions[0o071000] = self.DIV
        self.double_operand_RSS_instructions[0o072000] = self.ASH
        self.double_operand_RSS_instructions[0o073000] = self.ASHC
        self.double_operand_RSS_instructions[0o074000] = self.XOR
        self.double_operand_RSS_instructions[0o077000] = self.SOB

        self.double_operand_SSDD_instructions = {}
        self.double_operand_SSDD_instructions[0o010000] = self.MOV
        self.double_operand_SSDD_instructions[0o020000] = self.CMP
        self.double_operand_SSDD_instructions[0o030000] = self.BIT
        self.double_operand_SSDD_instructions[0o040000] = self.BIC
        self.double_operand_SSDD_instructions[0o050000] = self.BIS
        self.double_operand_SSDD_instructions[0o060000] = self.ADD
        self.double_operand_SSDD_instructions[0o160000] = self.SUB

    # ****************************************************
    # Double-Operand RSS instructions - 07 0R SS through 07 7R SS
    # ****************************************************

    def MUL(self, instruction, register, source):
        """07 0R SS MUL 4-31

        (R, R+1) < (R, R+1) * (src)"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} MUL unimplemented')
        source_value = self.am.addressing_mode_get(self, source)
        result = register * source_value
        self.psw.set_condition_codes(result, "", "****")
        return result

    def DIV(self, instruction, register, source):
        """07 1R SS DIV 4-32

        (R, R+1) < (R, R+1) / (src)"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} DIV unimplemented')
        source_value = self.am.addressing_mode_get(self, source)
        # *** needs to get word from register and its neighbor
        # *** needs to get word from source
        result = register / source_value
        self.psw.set_condition_codes(result, "", "****")
        return result

    def ASH(self, instruction, register, source):
        """07 2R SS ASH arithmetic shift 4-33

        R < R >> NN """
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} ASH unimplemented')
        result = register >> source
        self.psw.set_condition_codes(result, "", "****")
        return result

    def ASHC(self, instruction, register, source):
        """07 3R SS ASHC arithmetic shift combined 4-34

        (R, R+1) < (R, R+1) >> N"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} ASHC unimplemented')
        source_value = self.am.addressing_mode_get(self, source)
        result = register >> source
        self.psw.set_condition_codes(result, "", "****")
        return result

    def XOR(self, instruction, register, source):
        """07 4R DD XOR 4-35

        (dst) < R ^ (dst)"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} XOR unimplemented')
        source_value = self.am.addressing_mode_get(self, source)
        result = register ^ source_value
        self.psw.set_condition_codes(result, "", "****")
        return result

    def SOB(self, instruction, register, source):
        """07 7R NN SOB sutract one and branch 4-63

        R < R -1, then maybe branch"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} SOB unimplemented')
        source_value = self.am.addressing_mode_get(self, source)
        result = register * source_value
        self.psw.set_condition_codes(result, "", "****")
        return result

    def is_double_operand_RSS(self, instruction):
        """Using instruction bit pattern, determine whether it's an RSS RDD RNN instruction"""
        # 077R00 0 111 111 *** 000 000 SOB (jump & subroutine)
        # bit 15 = 0
        # bits 14-12 = 7
        # bits 9 10 11 in [0,1,2,3,4,7]
        bit15 = instruction & 0o100000 == 0o000000
        bits14_12 = instruction & 0o070000 == 0o070000
        bits11_9 = instruction & 0o077000 in [0o070000, 0o071000, 0o072000, 0o073000, 0o074000, 0o077000]
        return bit15 and bits14_12 and bits11_9

    def do_double_operand_RSS(self, instruction):
        """dispatch an RSS opcode"""
        # parameter: opcode of form 0 111 *** *** *** ***
        # register source or destination
        # 15-9 opcode
        # 8-6 reg
        # 5-0 src or dst
        opcode = (instruction & 0o077000)
        register = (instruction & 0o000700) >> 6
        source = instruction & 0o000077

        run = True
        try:
            result = self.double_operand_RSS_instructions[opcode](self, instruction, register, source)
            self.reg.inc_pc('do_double_operand_RSS')
            self.am.addressing_mode_set(B, dest, result)
        except KeyError:
            print(f'    {oct(self.reg.get_pc())} double_operand_RSS {oct(instruction)} {oct(opcode)} R{register} {oct(dest)} KeyError')
            run =  False
        return run

    # ****************************************************
    # Double-Operand SSDD instructions
    # 01 SS DD through 06 SS DD
    # 11 SS DD through 16 SS DD
    # ****************************************************

    def MOV(self, instruction, B, source, dest):
        """01 SS DD move 4-23

        (dst) < (src)"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} MOV{B} {oct(source)} {oct(dest)}')
        result = self.am.addressing_mode_get(B, source)
        self.psw.set_condition_codes(result, B, "**0-")
        return result

    def CMP(self, instruction, B, source, dest):
        """compare 4-24

        (src)-(dst)"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} CMP{B} {oct(source)} {oct(dest)}')
        source_value = self.am.addressing_mode_get(B, source)
        dest_value = self.am.addressing_mode_get(B, dest)
        result = source_value - dest_value
        self.psw.set_condition_codes(result, B, "****")
        return result

    def BIT(self, instruction, B, source, dest):
        """bit test 4-28

        (src) ^ (dst)"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} BIT{B} {oct(source)} {oct(dest)}')
        result = source & dest
        self.psw.set_condition_codes(result, B, "**0-")
        return result

    def BIC(self, instruction, B, source, dest):
        """bit clear 4-29

        (dst) < ~(src)&(dst)"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} BIC{B} {oct(source)} {oct(dest)}')
        result = ~source & dest
        self.psw.set_condition_codes(result, B, "**0-")
        return result

    def BIS(self, instruction, B, source, dest):
        """bit set 4-30
        (dst) < (src) v (dst)"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} BIS{B} {oct(source)} {oct(dest)}')
        result = source | dest
        self.psw.set_condition_codes(result, B, "**0-")
        return result

    def ADD(self, instruction, B, source, dest):
        """06 SS DD ADD add 4-25

        (dst) < (src) + (dst)"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} ADD{B} {oct(source)} {oct(dest)}')
        result = source + dest
        self.psw.set_condition_codes(result, B, "****")
        return result

    def SUB(self, instruction, B, source, dest):
        """06 SS DD SUB add 4-25

        (dst) < (dst) + ~(src) + 1"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} SUB{B} {oct(source)} {oct(dest)}')
        result = source + ~dest + 1
        self.psw.set_condition_codes(result, B, "****")
        return result

    def is_double_operand_SSDD(self, instruction):
        """Using instruction bit pattern, determine whether it's a souble operand instruction"""
        # bits 14 - 12 in [1, 2, 3, 4, 5, 6]
        # print (f'is_double_operand_SSDD {oct(instruction)}&0o070000={instruction & 0o070000}')
        bits14_12 = instruction & 0o070000 in [0o010000, 0o020000, 0o030000, 0o040000, 0o050000, 0o060000]
        return bits14_12

    def do_double_operand_SSDD(self, instruction):
        """dispatch a double-operand opcode.
        parameter: opcode of form * +++ *** *** *** ***
        where +++ = not 000 and not 111 and not 110 """
        # print(f'double_operand_SSDD {oct(instruction)}')
        # double operands
        # 15-12 opcode
        # 11-6 src
        # 5-0 dst

        #        * +++ *** *** *** *** double operands
        # •1SSDD * 001 *** *** *** *** MOV move source to destination (double)
        # •2SSDD * 010 *** *** *** *** CMP compare src to dst (double)
        # •3SSDD * 011 *** *** *** *** BIT bit test (double)
        # •4SSDD * 100 *** *** *** *** BIC bit clear (double)
        # •5SSDD * 101 *** *** *** *** BIS bit set (double)

        if (instruction & 0o100000) >> 15 == 1:
            B = 'B'
        else:
            B = ''
        opcode = (instruction & 0o070000)
        source = (instruction & 0o007700) >> 6
        dest = (instruction & 0o000077)

        run = True
        try:
            result = self.double_operand_SSDD_instructions[opcode](instruction, B, source, dest)
            self.am.addressing_mode_set(B, dest, result)
            #if B == '':
            #    self.reg.inc_pc('do_double_operand_SSDD') # **** this is probably not quite right
        except KeyError:
            print(f'    {oct(self.reg.get_pc())} {oct(instruction)} {oct(opcode)} is not a double operand instruction')
            run = false

        return run
