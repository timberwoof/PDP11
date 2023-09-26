"""PDP-11 Emulator"""
import time

import pdp11Hardware
from pdp11Hardware import registers as reg
from pdp11Hardware import ram
from pdp11Hardware import psw
from pdp11Hardware import stack
from pdp11Hardware import addressModes as am
from pdp11NoOperandOps import noOperandOps as nopr
from pdp11SingleOperandOps import singleOperandOps as sopr
from pdp11DoubleOperandOps import doubleOperandOps as dopr
from pdp11BranchOps import branchOps as br
from pdp11OtherOps import otherOps as other
from pdp11DL11 import dl11 as dl11
from pdp11Boot import pdp11Boot as boot
from pdp11m9301 import m9301 as m9301
from pdp11rk11 import rk11 as rk11

# boot.load_machine_code(boot.bootstrap_loader, bootaddress)
# reg.set_pc(0o2000, "load_machine_code")
# self.ram.dump(0o2000, 0o2064)

# boot.load_machine_code(boot.echo, boot.echo_address)
# self.ram.dump(0o1000, 0o1020)

# boot.read_PDP11_assembly_file('source/M9301-YF.txt')
# self.reg.set_pc(0o165022, "load_machine_code")

# source/M9301-YA.txt - includes assembly; starts at 165000
# source/M9301-YF.txt - includes assembly; starts at 165022
# source/M9301-YB.txt - raw machine, not very useful in diagnosing anything
# source/M9301-YH.txt - raw machine, not very useful in diagnosing anything
# self.ram.dump(0o165000, 0o165000+32)

class pdp11CPU():
    def __init__(self):
        """instantiate toe PDP11 emulator components"""
        print('pdp11CPU initializing')
        self.reg = reg()
        self.ram = ram(self.reg)
        self.psw = psw(self.ram)
        self.stack = stack(self.reg, self.ram, self.psw)
        self.am = am(self.reg, self.ram, self.psw)

        self.br = br(self.reg, self.ram, self.psw)
        self.nopr = nopr(self.reg, self.ram, self.psw, self.stack)
        self.sopr = sopr(self.reg, self.ram, self.psw, self.am)
        self.dopr = dopr(self.reg, self.ram, self.psw, self.am)
        self.other = other(self.reg, self.ram, self.psw, self.am)
        self.boot = boot(self.reg, self.ram)
        self.m9301 = m9301(self.reg, self.ram, self.boot)
        self.rk11 = rk11(self.ram)

        # set up DL11
        # set up the serial interface addresses
        # this must eventually be definable in a file so it has to be here
        DL11 = 0o177560  # reader status register 177560
        self.dl11 = dl11(self.ram, DL11, terminal=False)
        print('pdp11CPU initializing done')

    def dispatch_opcode(self, instruction):
        """ top-level dispatch"""
        #print(f'pdp11CPU dispatch_opcode {oct(instruction)}')
        # *** Redo this based on the table in PDP-11-10 processor manual.pdf II-1-34
        run = True

        if self.br.is_branch(instruction):
            self.br.do_branch(instruction)

        elif self.nopr.is_no_operand(instruction):
            run = self.nopr.do_no_operand(instruction)

        elif self.sopr.is_single_operand(instruction):
            run = self.sopr.do_single_operand(instruction)

        elif self.dopr.is_double_operand_RSS(instruction):
            run = self.dopr.do_double_operand_RSS(instruction)

        elif self.dopr.is_double_operand_SSDD(instruction):
            run = self.dopr.do_double_operand_SSDD(instruction)

        else:
            run = self.other.other_opcode(instruction)

        return run

    def instructionCycle(self):
        """Run one PDP11 fetch-decode-execute cycle"""
        # fetch opcode and increment PC
        PC = self.reg.get_pc() # get PC without incrementing
        instruction = self.ram.read_word_from_PC() # read at PC and increment PC
        print('----')
        print(f'PC:{oct(PC)} opcode:{oct(instruction)}')
        #print(f'PC:{oct(self.reg.get_pc())}')
        # decode and execute opcode
        run = self.dispatch_opcode(instruction)
        self.reg.log_registers()
        return run


class pdp11Run():
    def __init__(self, pdp11CPU):
        """instantiate the PDP11 CPU"""
        self.pdp11 = pdp11CPU
        self.run = False

    def run(self):
        """Run PDP11 emulator without terminal process"""
        print('begin PDP11 emulator')
        self.reg.log_registers()

        # start the processor loop
        instructions_executed = 0
        timeStart = time.time()
        while True:
            self.pdp11.instructionCycle()
            instructions_executed = instructions_executed + 1

        print (f'run instructions_executed: {instructions_executed}')
        timeEnd = time.time()
        timeElapsed = (timeEnd - timeStart)
        print (f'timeElapsed: {timeElapsed}:.2f seconds')
        ops_per_sec = instructions_executed / timeElapsed
        print (f'executed {ops_per_sec:.2f} instructions per second')
        if self.reg.get_pc() > 0o200:
            self.ram.dump(self.reg.get_pc()-0o20, self.reg.get_pc()+0o20)
        self.pdp11.am.address_mode_report()

    def runInTerminal(self):
        """run PDP11 with a PySimpleGUI terminal window."""
        print('runInTerminal begin')

        DL11 = 0o177560  # reader status register 177560
        self.dl11 = dl11(self.pdp11.ram, DL11, terminal=True)
        self.pdp11.reg.log_registers()

        # Create and run the terminal window in PySimpleGUI
        print('runInTerminal dl11.makeWindow')
        window = self.dl11.makeWindow()
        windowRun = True
        cpuRun = False
        while windowRun:
            # run window bits
            if cpuRun:
                cpuRun = self.pdp11.instructionCycle()
            windowRun, cpuRun = self.dl11.terminalWindowCycle(cpuRun, self.pdp11)

        print('runInTerminal ends')
        self.pdp11.am.address_mode_report()