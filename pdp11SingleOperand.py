"""pdp11SingleOperand.py single oprand instructions"""

from pdp11psw import psw
from pdp11ram import ram
from pdp11reg import reg
from pdp11AddressMode import am

"""self.single_operand_instructions
    :param instruction: opcode
    :param dest: address
    :param operand: operand
    :param B: 'B' for byte instruction, '' for word
"""

class sopr:
    def __init__(self, psw, ram, reg):
        print('initializing pdp11sopr')
        self.psw = psw
        self.ram = ram
        self.reg = reg
        self.am = am(psw, ram, reg)

        # ****************************************************
        # Single-Operand instructions -
        # 00 50 DD - 00 77 DD
        # 10 50 DD - 10 77 DD
        # ****************************************************
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

        self.single_operand_instruction_names = {}
        self.single_operand_instruction_names[0o000100] = "JMP"
        self.single_operand_instruction_names[0o000300] = "SWAB"
        self.single_operand_instruction_names[0o005000] = "CLR"
        self.single_operand_instruction_names[0o005100] = "COM"
        self.single_operand_instruction_names[0o005200] = "INC"
        self.single_operand_instruction_names[0o005300] = "DEC"
        self.single_operand_instruction_names[0o005400] = "NEG"
        self.single_operand_instruction_names[0o005500] = "ADC"
        self.single_operand_instruction_names[0o005600] = "SBC"
        self.single_operand_instruction_names[0o005700] = "TST"
        self.single_operand_instruction_names[0o006000] = "ROR"
        self.single_operand_instruction_names[0o006100] = "ROL"
        self.single_operand_instruction_names[0o006200] = "ASR"
        self.single_operand_instruction_names[0o006300] = "ASL"
        # self.single_operand_instruction_names[0o006400] = "MARK"
        # self.single_operand_instruction_names[0o006500] = "MFPI"
        # self.single_operand_instruction_names[0o006600] = "MTPI"
        self.single_operand_instruction_names[0o006700] = "SXT"
        self.single_operand_instruction_names[0o105000] = "CLRB"
        self.single_operand_instruction_names[0o105100] = "COMB"
        self.single_operand_instruction_names[0o105200] = "INCB"
        self.single_operand_instruction_names[0o105300] = "DECB"
        self.single_operand_instruction_names[0o105400] = "NEGB"
        self.single_operand_instruction_names[0o105500] = "ADCB"
        self.single_operand_instruction_names[0o105600] = "SBCB"
        self.single_operand_instruction_names[0o105700] = "TSTB"
        self.single_operand_instruction_names[0o106000] = "RORB"
        self.single_operand_instruction_names[0o106100] = "ROLB"
        self.single_operand_instruction_names[0o106200] = "ASRB"
        self.single_operand_instruction_names[0o106300] = "ASLB"
        self.single_operand_instruction_names[0o106500] = "MFPD"
        self.single_operand_instruction_names[0o106600] = "MTPD"

    def JMP(self, instruction, dest, operand, B):
        """00 01 DD JMP jump 4-56"""
        self.reg.set_pc(operand, 'JMP')
        return operand, "----"

    def SWAB(self, instruction, dest, operand, B):
        """00 03 DD Swap Bytes 4-17"""
        result = (operand & 0xFF00) << 8 + (operand & 0x00FF) >> 8
        return result, "**00"

    def CLR(self, instruction, dest, operand, B):
        """00 50 DD Clear Destination"""
        result = 0o0
        return result, "0000"

    def COM(self, instruction, dest, operand, B):
        """00 51 DD Complement Destination"""
        result = ~operand
        return result, "**01"

    def INC(self, instruction, dest, operand, B):
        """00 52 DD Increment Destination"""
        result = operand + 1
        return result, "***-"

    def DEC(self, instruction, dest, operand, B):
        """00 53 DD Decrement Destination"""
        result = operand - 1
        return result, "***-"

    def NEG(self, instruction, dest, operand, B):
        """00 54 DD negate Destination"""
        result = -operand
        return result, "****"

    def ADC(self, instruction, dest, operand, B):
        """00 55 DD Add Carry"""
        result = dest + self.psw.C()
        return result, "****"

    def SBC(self, instruction, dest, operand, B):
        """00 56 DD Subtract Carry"""
        result = dest - operand
        return result, "****"

    def TST(self, instruction, dest, operand, B):
        """00 57 DD Test Destination"""
        return dest, "**00"

    def ROR(self, instruction, dest, operand, B):
        """00 60 DD ROR rotate right"""
        result = operand >> 1
        return result, "****"

    def ROL(self, instruction, dest, operand, B):
        """00 61 DD ROL rotate left"""
        result = operand << 1
        return result, "****"

    def ASR(self, instruction, dest, operand, B):
        """00 62 DD ASR arithmetic shift right"""
        result = operand >> 1
        return result, "****"

    def ASL(self, instruction, dest, operand, B):
        """00 63 DD ASL arithmetic shift left"""
        result = operand << 1
        return result, "****"

    def SXT(self, instruction, dest, operand, B):
        """00 67 DD Sign Extend"""
        return result, "****"

    def MFPD(self, instruction, dest, operand, B):
        """10 65 SS Move from previous data space"""
        print(f'NOT IMPLEMENTED')
        return operand, "****"

    def MTPD(self, instruction, dest, operand, B):
        """10 66 SS Move to previous data space"""
        print(f'NOT IMPLEMENTED')
        return operand, "****"

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
        #print(f'    is_single_operand({oct(instruction)})')
        bits_14_13_12 = instruction & 0o070000 == 0o000000
        bits_11_10_9 = instruction & 0o007000 in [0o006000, 0o005000]
        isJMP = instruction & 0o177700 == 0o000100
        isSWAB = instruction & 0o177700 == 0o000300
        #print(f'    is_single_operand {bits_14_13_12} {bits_11_10_9} {isSWAB}  {isJMP}')
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
        else:
            B = ''
        opcode = instruction & 0o107700
        source = instruction & 0o000077
        source_value = self.am.addressing_mode_get(B, source)

        run = True
        print(f'{oct(self.reg.get_pc()-2)} {oct(instruction)} '
              f'{self.single_operand_instruction_names[opcode]} {oct(source_value)}')
        result, codes = self.single_operand_instructions[opcode](instruction, source_value, source_value, B)
        self.am.addressing_mode_set(B, source, result)
        self.psw.set_condition_codes(result, B, codes)
        return run