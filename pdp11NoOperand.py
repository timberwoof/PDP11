"""pdp11NoOperand.py - no-operand instructions 00 00 00 through 00 00 06"""

from pdp11psw import psw
from pdp11ram import ram
from pdp11reg import reg

class noopr:
    def __init__(self, psw, ram, reg):
        print('initializing pdp11noopr')
        self.psw = psw
        self.ram = ram
        self.reg = reg
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

    def popstack(self):
        """pop the stack and return that value

        get the stack value, increment the stack pointer, return value"""
        stack = self.reg.get_sp()
        result = self.ram.read_word(stack)
        self.reg.set_sp(stack + 2)
        return result

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
        *** need to implement the stack
        """
        self.reg.set_pc(self.popstack(), "RTI")
        self.psw.set_PSW(PSW=self.popstack())
        return True

    def BPT(self, instruction):
        """00 00 03 BPT breakpoint trap 4-67"""
        print(f'BPT unimplemented')
        return False

    def IOT(self, instruction):
        """00 00 04 IOT input/output trap 4-68"""
        print(f'IOT unimplemented')
        return False

    def RESET(self, instruction):
        """00 00 05 RESET reset external bus 4-76"""
        return True

    def RTT(self, instruction):
        """00 00 06 RTT return from interrupt 4-70"""
        print(f'RTT unimplemented')
        return False

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
