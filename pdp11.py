"""PDP-11 Emulator"""
import threading
import time

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
from threading import Thread
from threading import Event
import time
import traceback

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
        self.ram = ram()
        self.psw = psw(self.ram)
        self.br = br(self.reg, self.ram, self.psw)
        self.stack = stack(self.reg, self.ram, self.psw)
        self.nopr = nopr(self.reg, self.ram, self.psw, self.stack)
        self.am = am(self.reg, self.ram, self.psw)
        self.sopr = sopr(self.reg, self.ram, self.psw, self.am)
        self.dopr = dopr(self.reg, self.ram, self.psw, self.am)
        self.other = other(self.reg, self.ram, self.psw, self.am)
        self.boot = boot(self.reg, self.ram)
        print(f'pdp11CPU init PSW_address:{oct(self.psw.PSW_address)}') # *** this WORKS!

    def log_registers(self):
        """print all the registers in the log"""
        # *** this ought to go into hardware
        index = 0
        report = '    '
        for register in self.reg.registers:
            report = report + f'R{index}: {oct(register)}  '
            index = index + 1
        report = report + f'NZVC: {self.psw.N()}{self.psw.Z()}{self.psw.V()}{self.psw.C()}'
        print(report)

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
        PC = self.reg.get_pc()
        instruction = self.ram.read_word(PC)
        print(f'PC:{oct(PC)}  opcode:{oct(instruction)}')
        self.reg.inc_pc(2, "fetched instruction")
        # decode and execute opcode
        run = self.dispatch_opcode(instruction)
        self.log_registers()


class pdp11Run():
    def __init__(self, pdp11CPU):
        """instantiate the PDP11 CPU"""
        self.pdp11 = pdp11CPU
        self.run = False

    def run(self):
        """Run PDP11 emulator without terminal process"""
        print('begin PDP11 emulator')
        # set up DL11
        # set up the serial interface addresses
        DL11 = 0o177560  # reader status register 177560
        self.dl11 = dl11(self.ram, DL11, terminal=False)
        self.dl11.register_with_ram()
        # this must eventually be definable in a file so it has to be here
        self.log_registers()

        # start the processor loop
        instructions_executed = 0
        timeStart = time.time()
        while True:
            self.pdp11.instructionCycle()
            instructions_executed = instructions_executed + 1
            if instructions_executed > 200:
                break

        if self.reg.get_pc() > 0o200:
            self.ram.dump(self.reg.get_pc()-0o20, self.reg.get_pc()+0o20)

        print (f'run instructions_executed: {instructions_executed}')
        timeEnd = time.time()
        timeElapsed = (timeEnd - timeStart)
        print (f'timeElapsed: {timeElapsed}:.2f seconds')
        ops_per_sec = instructions_executed / timeElapsed
        print (f'executed {ops_per_sec:.2f} instructions per second')
        if self.reg.get_pc() > 0o200:
            self.ram.dump(self.reg.get_pc()-0o20, self.reg.get_pc()+0o20)
        self.am.address_mode_report()
        self.dl11.dumpBuffer()

    def runThreaded(self, dl11, event):
        """Run PDP11 emulator in thread with main terminal process.
        Runs instructionCycle in a loop"""
        print('runThreaded begin PDP11 emulator\n')
        # this must eventually be definable in a file so it has to be here
        print('runThreaded log_registers()')
        self.pdp11.log_registers()

        # start the processor loop
        instructions_executed = 0
        timeStart = time.time()
        while True:
            event.wait() # This is the only difference
            try:
                self.pdp11.instructionCycle()
            except:
                traceback.print_exc()
            instructions_executed = instructions_executed + 1
            if instructions_executed > 200:
                break

        print (f'runThreaded instructions_executed: {instructions_executed}')
        timeEnd = time.time()
        timeElapsed = (timeEnd - timeStart)
        print (f'timeElapsed: {timeElapsed}:.2f seconds')
        ops_per_sec = instructions_executed / timeElapsed
        print (f'executed {ops_per_sec:.2f} instructions per second')
        if self.reg.get_pc() > 0o200:
            self.ram.dump(self.reg.get_pc()-0o20, self.reg.get_pc()+0o20)
        self.am.address_mode_report()
        self.dl11.dumpBuffer()

    def runInTerminal(self):
        """run PDP11 as a separae thread and launch a PySimpleGUI terminal window."""
        print('runInTerminal begin')

        DL11 = 0o177560  # reader status register 177560
        self.dl11 = dl11(self.pdp11.ram, DL11, terminal=True)
        self.dl11.register_with_ram()
        # this must eventually be definable in a file so it has to be here
        self.pdp11.log_registers()

        # Run the PDP11 emulator as a separate thread
        event = threading.Event()
        #cpu_thread = Thread(target=self.runThreaded, args=(self.dl11, event,), daemon=True)
        # Threads marked as daemon automatically die when every other non-daemon thread is dead.
        #print('runInTerminal cpu_thread.start')
        #cpu_thread.start()

        # Create and run the terminal window in PySimpleGUI
        print('runInTerminal dl11.makeWindow')
        window = self.dl11.makeWindow()
        windowRun = True
        cpuRun = False
        while windowRun:
            # run window bits
            if cpuRun:
                self.pdp11.instructionCycle()
            windowRun, cpuRun = self.dl11.terminalWindowCycle(cpuRun)
            #if cpuRun:
            #    event.set()
            #else:
            #    event.clear()

        print('runInTerminal dl11.dumpBuffer:')
        self.dl11.dumpBuffer()
        print('runInTerminal ends')