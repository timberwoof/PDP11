"""pdp11_noopr_ops.py - no-operand instructions 00 00 00 through 00 00 06"""
import logging

class noopr_ops:
    """Implements PDP11 no-operand instructions"""
    def __init__(self, reg, ram, psw, stack, sw):
        logging.info('initializing NoOperandOps')
        self.reg = reg
        self.ram = ram
        self.psw = psw
        self.stack = stack
        self.sw = sw

        self.no_operand_instructions = {}
        self.no_operand_instructions[0o000000] = self.HALT
        self.no_operand_instructions[0o000001] = self.WAIT
        self.no_operand_instructions[0o000002] = self.RTI
        self.no_operand_instructions[0o000003] = self.BPT
        self.no_operand_instructions[0o000004] = self.IOT
        self.no_operand_instructions[0o000005] = self.RESET
        self.no_operand_instructions[0o000006] = self.RTT

        self.no_operand_instruction_names = {}
        self.no_operand_instruction_names[0o000000]= "HALT"
        self.no_operand_instruction_names[0o000001]= "WAIT"
        self.no_operand_instruction_names[0o000002]= "RTI"
        self.no_operand_instruction_names[0o000003]= "BPT"
        self.no_operand_instruction_names[0o000004]= "IOT"
        self.no_operand_instruction_names[0o000005]= "RESET"
        self.no_operand_instruction_names[0o000006]= "RTT"

    def HALT(self):
        """00 00 00 Halt"""
        return False, ''

    def WAIT(self):
        """00 00 01 Wait 4-75"""
        # *** unimplemented
        self.reg.inc_pc('WAIT')
        return False, 'WAIT unimplemented'

    def RTI(self):
        """00 00 02 RTI return from interrupt 4-69
        PC < (SP)^; PS< (SP)^
        """
        self.reg.set_pc(self.stack.pop(), "RTI")
        self.psw.set_psw(psw=self.stack.pop())
        return True, 'RTI unimplemented'

    def BPT(self):
        """00 00 03 BPT breakpoint trap 4-67"""
        # *** unimplemented
        self.reg.inc_pc('BPT')
        return False, 'BPT unimplemented'

    def IOT(self):
        """00 00 04 IOT input/output trap 4-68

        | push PS
        | push PC
        PC <- 20
        PS <- 22"""
        # Performs a trap sequence with a trap vector address of 20.
        # Used to call the 1/0 Executive routine lOX in the paper tape software system,
        # and for error reporting in the Disk Oper- ating System.

        self.stack.push(self.psw.PSW)
        self.stack.push(self.reg.get_pc())
        self.reg.set_pc(0o20, "IOT")
        self.reg.set_sp(0o22, "IOT")
        return True, ''

    def RESET(self):
        """00 00 05 RESET reset external bus 4-76"""
        return True, '; RESET unimplemented (mostly harmless)'

    def RTT(self):
        """00 00 06 RTT return from interrupt 4-70"""
        self.reg.set_pc(self.stack.pop(), "RTT")
        self.reg.set_sp(self.stack.pop(), "RTT")
        self.psw.set_condition_codes('W', self.reg.get_sp(), "***")
        return True, ''

    def is_noopr_op(self, instruction):
        """Using instruction bit pattern, determine whether it's a no-operand instruction"""
        return instruction in self.no_operand_instructions

    def do_noopr_op(self, instruction):
        """dispatch a no-operand opcode"""
        # parameter: opcode of form * 000 0** *** *** ***
        self.sw.start("noopr")
        try:
            assembly = f'{self.no_operand_instruction_names[instruction]}'
            result, report = self.no_operand_instructions[instruction]()
        except KeyError:
            assembly = ''
            report = 'Error: no-operand opcode not found'
            result = False
        self.sw.stop("noopr")
        return result, '', '', assembly, report
