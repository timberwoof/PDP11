"""PDP-11 Emulator"""
import time

from pdp11_hardware import Registers as reg
from pdp11_hardware import Ram
from pdp11_hardware import PSW
from pdp11_hardware import Stack
from pdp11_hardware import AddressModes as am
from pdp11_no_operand_ops import NoOperandOps as nopr
from pdp11_single_operand_ops import SingleOperandOps as sopr
from pdp11_double_operand_ops import DoubleOperandOps as dopr
from pdp11_branch_ops import BranchOps as br
from pdp11_other_ops import OtherOps as other
from pdp11_dl11 import DL11
from pdp11_boot import pdp11Boot as boot
from pdp11_m9301 import M9301
from pdp11_rk11 import RK11
from stopwatches import StopWatches as sw

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

class PDP11():
    """Timber's PDP11 emulator"""
    def __init__(self):
        """instantiate toe PDP11 emulator components"""
        print('pdp11CPU initializing')
        self.sw = sw()

        self.reg = reg()
        self.ram = Ram(self.reg)
        self.psw = PSW(self.ram)
        self.stack = Stack(self.reg, self.ram, self.psw)
        self.am = am(self.reg, self.ram, self.psw)

        self.br = br(self.reg, self.ram, self.psw)
        self.nopr = nopr(self.reg, self.ram, self.psw, self.stack)
        self.sopr = sopr(self.reg, self.ram, self.psw, self.am)
        self.dopr = dopr(self.reg, self.ram, self.psw, self.am)
        self.other = other(self.reg, self.ram, self.psw, self.am)
        self.boot = boot(self.reg, self.ram)
        self.m9301 = M9301(self.reg, self.ram, self.boot)
        self.rk11 = RK11(self.ram)

        # set up DL11
        # set up the serial interface addresses
        # this must eventually be definable in a file so it has to be here
        # reader status register 177560
        self.dl11 = DL11(self.ram, 0o177560)
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

    def instruction_cycle(self, sw):
        """Run one PDP11 fetch-decode-execute cycle"""
        # fetch opcode and increment program counter
        sw.start("cycle")
        pc = self.reg.get_pc() # get pc without incrementing
        instruction = self.ram.read_word_from_pc() # read at pc and increment pc
        print('----')
        print(f'pc:{oct(pc)} opcode:{oct(instruction)}')
        #print(f'pc:{oct(self.reg.get_pc())}')
        # decode and execute opcode
        run = self.dispatch_opcode(instruction)
        self.reg.log_registers()
        sw.stop("cycle")
        return run


class pdp11Run():
    """sets up and runs PDP11 emulator"""
    def __init__(self, pdp11):
        """instantiate the PDP11 CPU"""
        self.sw = sw()
        self.pdp11 = pdp11
        self.running = False

    def run(self):
        """Run PDP11 emulator without terminal process"""
        print('begin PDP11 emulator')
        self.pdp11.reg.log_registers()

        # start the processor loop
        instructions_executed = 0
        time_start = time.time()
        while True:
            self.pdp11.instruction_cycle(self.sw)
            instructions_executed = instructions_executed + 1

        print (f'run instructions_executed: {instructions_executed}')
        time_end = time.time()
        time_elapsed = time_end - time_start
        print (f'time_elapsed: {time_elapsed}:.2f seconds')
        ops_per_sec = instructions_executed / time_elapsed
        print (f'executed {ops_per_sec:.2f} instructions per second')
        if self.pdp11.reg.get_pc() > 0o200:
            self.pdp11.Ram.dump(self.pdp11.reg.get_pc() - 0o20, self.pdp11.reg.get_pc() + 0o20)
        self.pdp11.am.address_mode_report()

    def run_in_terminal(self):
        """run PDP11 with a PySimpleGUI terminal window."""
        print('run_in_terminal begin')

        self.pdp11.reg.log_registers()

        # Create and run the terminal window in PySimpleGUI
        print('run_in_terminal dl11.make_window')
        window = self.pdp11.dl11.make_window()
        window_run = True # *** this is somehow broken. PyLint does not like this.
        cpu_run = False
        while window_run:
            # run window bits
            if cpu_run:
                cpu_run = self.pdp11.instruction_cycle(self.sw)
            window_run, cpu_run = self.pdp11.dl11.terminal_window_cycle(cpu_run, self.pdp11)

        print('run_in_terminal ends')
        self.pdp11.am.address_mode_report()
        self.sw.report()
