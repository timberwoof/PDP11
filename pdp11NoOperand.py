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

    def HALT(self, instruction):
        """00 00 00 Halt"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} HALT')
        return False

    def WAIT(self, instruction):
        """00 00 01 Wait 4-75"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} WAIT unimplemented')
        self.reg.inc_pc('WAIT')
        return True

    def RTI(self, instruction):
        """00 00 02 RTI return from interrupt 4-69
        PC < (SP)^; PS< (SP)^
        *** need to implement the stack
        """
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} RTI')
        self.reg.set_pc(popstack(), "RTI")
        psw.set_PSW(PSW=popstack())
        return True

    def BPT(self, instruction):
        """00 00 03 BPT breakpoint trap 4-67"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} BPT unimplemented')
        self.reg.inc_pc('BPT')
        return True

    def IOT(self, instruction):
        """00 00 04 IOT input/output trap 4-68"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} IOT unimplemented')
        self.reg.inc_pc('IOT')
        return True

    def RESET(self, instruction):
        """00 00 05 RESET reset external bus 4-76"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} RESET unimplemented')
        self.reg.inc_pc('RESET')
        return True

    def RTT(self, instruction):
        """00 00 06 RTT return from interrupt 4-70"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} RTT unimplemented')
        self.reg.inc_pc('RTT')
        return True

    def NOP(self, instruction):
        """00 02 40 NOP no operation"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} NOP')
        self.reg.inc_pc('NOP')
        return True

    def is_no_operand(self, instruction):
        """Using instruction bit pattern, determine whether it's a no-operand instruction"""
        return instruction in self.no_operand_instructions.keys()

    def do_no_operand(self, instruction):
        """dispatch a no-operand opcode"""
        # parameter: opcode of form * 000 0** *** *** ***
        # print(f'    {oct(self.reg.getpc())} {oct(instruction)} no_operand {oct(instruction)}')
        result = True
        try:
            # method = self.no_operand_instructions[instruction]
            result = self.no_operand_instructions[instruction](instruction)
        except KeyError:
            #print(f'{oct(instruction)} is not a no_operand')
            result = False
        return result
