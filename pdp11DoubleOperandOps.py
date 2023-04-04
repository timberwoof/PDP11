"""pdp11DoubleOperandOps.py double operand instructions"""

from pdp11Hardware import ram
from pdp11Hardware import reg
from pdp11Hardware import psw
from pdp11Hardware import am

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

        self.double_operand_RSS_instruction_names = {}
        self.double_operand_RSS_instruction_names[0o070000] = "MUL"
        self.double_operand_RSS_instruction_names[0o071000] = "DIV"
        self.double_operand_RSS_instruction_names[0o072000] = "ASH"
        self.double_operand_RSS_instruction_names[0o073000] = "ASHC"
        self.double_operand_RSS_instruction_names[0o074000] = "XOR"
        self.double_operand_RSS_instruction_names[0o077000] = "SOB"

        self.double_operand_SSDD_instructions = {}
        # SSDD instructions with B variants the usual way
        self.double_operand_SSDD_instructions[0o010000] = self.MOV
        self.double_operand_SSDD_instructions[0o020000] = self.CMP
        self.double_operand_SSDD_instructions[0o030000] = self.BIT
        self.double_operand_SSDD_instructions[0o040000] = self.BIC
        self.double_operand_SSDD_instructions[0o050000] = self.BIS

        # SSDD instructions that break the rule
        self.double_operand_SSDD_instructions[0o060000] = self.ADDSUB

        self.double_operand_SSDD_instruction_names = {}
        self.double_operand_SSDD_instruction_names[0o010000] = "MOV"
        self.double_operand_SSDD_instruction_names[0o020000] = "CMP"
        self.double_operand_SSDD_instruction_names[0o030000] = "BIT"
        self.double_operand_SSDD_instruction_names[0o040000] = "BIC"
        self.double_operand_SSDD_instruction_names[0o050000] = "BIS"
        self.double_operand_SSDD_instruction_names[0o060000] = "ADD"
        self.double_operand_SSDD_instruction_names[0o110000] = "MOVB"
        self.double_operand_SSDD_instruction_names[0o120000] = "CMPB"
        self.double_operand_SSDD_instruction_names[0o130000] = "BITB"
        self.double_operand_SSDD_instruction_names[0o140000] = "BICB"
        self.double_operand_SSDD_instruction_names[0o150000] = "BISB"
        self.double_operand_SSDD_instruction_names[0o160000] = "SUB"

    # ****************************************************
    # Double-Operand RSS instructions - 07 0R SS through 07 7R SS
    # ****************************************************

    def MUL(self, register, source):
        """07 0R SS MUL 4-31

        (R, R+1) < (R, R+1) * (src)"""
        print(f'MUL unimplememnted')
        result = register * source
        return result, "****"

    def DIV(self, register, source):
        """07 1R SS DIV 4-32

        (R, R+1) < (R, R+1) / (src)"""
        print(f'DIV unimplemented')
        # *** needs to get word from register and its neighbor
        # *** needs to get word from source
        result = register / source
        return result, "****"

    def ASH(self, register, source):
        """07 2R SS ASH arithmetic shift 4-33

        R < R >> NN """
        result = register >> source
        return result, "****"

    def ASHC(self, register, source):
        """07 3R SS ASHC arithmetic shift combined 4-34

        (R, R+1) < (R, R+1) >> N"""
        print(f'ASHC unimplemented')
        result = register >> source
        return result, "****"

    def XOR(self, register, source):
        """07 4R DD XOR 4-35

        (dst) < R ^ (dst)"""
        result = register ^ source
        return result, "****"

    def SOB(self, register, source):
        """07 7R NN SOB sutract one and branch 4-63

        R < R -1, then maybe branch"""
        print(f'SOB unimplemented')
        result = register * source
        return result, "****"

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
        source_value = self.am.addressing_mode_get('', source)

        run = True
        print(f'{oct(self.reg.get_pc() - 2)} {oct(instruction)} '
              f'{self.double_operand_RSS_instruction_names[opcode]} '
              f'r{register}={oct(self.reg[register])} {oct(source)}={oct(source_value)}')
        result, code = self.double_operand_RSS_instructions[opcode](self, register, source_value)
        self.reg.inc_pc('do_double_operand_RSS')
        self.reg.registers[register] = result
        self.psw.set_condition_codes(result, "", code)

        return run

    # ****************************************************
    # Double-Operand SSDD instructions
    # 01 SS DD through 06 SS DD
    # 11 SS DD through 16 SS DD
    # ****************************************************

    def MOV(self, B, source, dest):
        """01 SS DD move 4-23

        (dst) < (src)"""
        result = source
        print(f'    source:{oct(source)} dest:{oct(dest)} result:{oct(result)}')
        return result, "**0-"

    def CMP(self, B, source, dest):
        """compare 4-24
        (src)-(dst)"""
        # subtract dst from source
        # set the condition code based on that result
        # but don't change the destination
        result = source - dest
        #print(f'    CMP source:{source} dest:{dest} result:{result}')
        self.psw.set_condition_codes(result, B, "****")
        #print(f'    CMP NZVC: {self.psw.N()}{self.psw.Z()}{self.psw.V()}{self.psw.C()}')
        return dest, "----"

    def BIT(self, B, source, dest):
        """bit test 4-28

        (src) ^ (dst)"""
        result = source & dest
        return result, "**0-"

    def BIC(self, B, source, dest):
        """bit clear 4-29

        (dst) < ~(src)&(dst)"""
        result = ~source & dest
        return result, "**0-"

    def BIS(self, B, source, dest):
        """bit set 4-30
        (dst) < (src) v (dst)"""
        result = source | dest
        return result, "**0-"

    def ADDSUB(self, B, source, dest):
        """06 SS DD: ADD 4-25 (dst) < (src) + (dst)
        | 16 SS DD: SUB 4-26 (dst) < (dst) + ~(src) + 1
        """
        if B == "":
            result = source + dest
        else:
            result = abs(source + ~dest + 1)
        return result, "****"

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
        name_opcode = (instruction & 0o170000)
        print(f'{oct(self.reg.get_pc()-2)} {oct(instruction)} '
              f'{self.double_operand_SSDD_instruction_names[name_opcode]} ')

        source = (instruction & 0o007700) >> 6
        dest = (instruction & 0o000077)
        source_value = self.am.addressing_mode_get(B, source)
        dest_value = self.am.addressing_mode_get(B, dest)
        #print(f'    {oct(source)}={oct(source_value)} {oct(dest)}={oct(dest_value)}')

        run = True
        result, code = self.double_operand_SSDD_instructions[opcode](B, source_value, dest_value)
        self.am.addressing_mode_set(B, dest, result)
        self.psw.set_condition_codes(result, B, code)
        print(f'    result:{oct(result)}   NZVC: {self.psw.N()}{self.psw.Z()}{self.psw.V()}{self.psw.C()}  PC:{oct(self.reg.get_pc())}')

        return run
