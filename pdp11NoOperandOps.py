"""pdp11NoOperandOps.py - no-operand instructions 00 00 00 through 00 00 06"""

from pdp11Hardware import ram
from pdp11Hardware import reg
from pdp11Hardware import psw
from pdp11Stack import stack

class noopr:
    def __init__(self, psw, ram, reg, stack):
        print('initializing pdp11noopr')
        self.psw = psw
        self.ram = ram
        self.reg = reg
        self.stack = stack

        self.no_operand_instructions = {}
        self.no_operand_instructions[0o000000] = self.HALT
        self.no_operand_instructions[0o000001] = self.WAIT
        self.no_operand_instructions[0o000002] = self.RTI
        self.no_operand_instructions[0o000003] = self.BPT
        self.no_operand_instructions[0o000004] = self.IOT
        self.no_operand_instructions[0o000005] = self.RESET
        self.no_operand_instructions[0o000006] = self.RTT
        self.no_operand_instructions[0o000240] = self.NOP

        self.no_operand_instruction_namess = {}
        self.no_operand_instruction_namess[0o000000]= "HALT"
        self.no_operand_instruction_namess[0o000001]= "WAIT"
        self.no_operand_instruction_namess[0o000002]= "RTI"
        self.no_operand_instruction_namess[0o000003]= "BPT"
        self.no_operand_instruction_namess[0o000004]= "IOT"
        self.no_operand_instruction_namess[0o000005]= "RESET"
        self.no_operand_instruction_namess[0o000006]= "RTT"
        self.no_operand_instruction_namess[0o000240]= "NOP"

    def HALT(self, instruction):
        """00 00 00 Halt"""
        return False

    def WAIT(self, instruction):
        """00 00 01 Wait 4-75"""
        print(f'WAIT unimplemented')
        return False

    def RTI(self, instruction):
        """00 00 02 RTI return from interrupt 4-69
        PC < (SP)^; PS< (SP)^
        """
        self.reg.set_pc(self.stack.pop(), "RTI")
        self.psw.set_PSW(PSW=self.stack.pop())
        return True

    def BPT(self, instruction):
        """00 00 03 BPT breakpoint trap 4-67"""
        print(f'BPT unimplemented')
        return False

    def IOT(self, instruction):
        """00 00 04 IOT input/output trap 4-68

        | push PS
        | push PC
        PC <- 20
        PS <- 22"""
        # Performs a trap sequence with a trap vector address of 20.
        # Used to call the 1/0 Executive routine lOX in the paper tape software system,
        # and for error reporting in the Disk Oper- ating System.

        self.stack.push(self.ram.get_PSW()) # this shows that get-PSW should be in reg
        self.stack.push(self.reg.get_pc())
        #self.reg.set_pc(20) # why this magic value?
        #self.reg.set_ps(22) # what are we setting? why this magic value?
        return True

    def RESET(self, instruction):
        """00 00 05 RESET reset external bus 4-76"""
        return True

    def RTT(self, instruction):
        """00 00 06 RTT return from interrupt 4-70"""
        self.reg.set_pc(self.stack.pop(), "RTT")
        self.reg.set_sp(self.stack.pop())
        self.psw.set_condition_codes(self.reg.get_sp(), '', "***")
        return True

    def NOP(self, instruction):
        """00 02 40 NOP no operation"""
        return True

    def is_no_operand(self, instruction):
        """Using instruction bit pattern, determine whether it's a no-operand instruction"""
        return instruction in self.no_operand_instructions.keys()

    def do_no_operand(self, instruction):
        """dispatch a no-operand opcode"""
        # parameter: opcode of form * 000 0** *** *** ***
        print(f'{oct(self.reg.get_pc()-2)} {oct(instruction)} {self.no_operand_instruction_namess[instruction]}')
        result = True
        result = self.no_operand_instructions[instruction](instruction)
        return result
