"""PDP-11 Emulator"""
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
from pdp11Boot import boot as boot

class pdp11():
    def __init__(self):
        print('initializing pdp11')
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

        # set up DL11
        # set up the serial interface addresses
        DL11 = 0o177560  # reader status register 177560
        self.dl11 = dl11(self.ram, DL11)
        self.dl11.register_with_ram()
        # this must eventually be definable in a file so it has to be here

        print(f'pdp11 init  PSW_address:{oct(self.psw.PSW_address)}') # *** this WORKS!

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
        #print(f'dispatch_opcode {oct(instruction)}')
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

    # ****************************************************
    # main
    # ****************************************************
    def run(self):
        print('begin PDP11 emulator')
        self.log_registers()

        #boot.load_machine_code(boot.bootstrap_loader, bootaddress)
        #reg.set_pc(0o2000, "load_machine_code")
        #self.ram.dump(0o2000, 0o2064)

        #boot.load_machine_code(boot.echo, boot.echo_address)
        #self.ram.dump(0o1000, 0o1020)

        #boot.read_PDP11_assembly_file('source/M9301-YF.txt')
        #self.reg.set_pc(0o165022, "load_machine_code")

        # source/M9301-YA.txt - includes assembly; starts at 165000
        # source/M9301-YF.txt - includes assembly; starts at 165022
        # source/M9301-YB.txt - raw machine, not very useful in diagnosing anything
        # source/M9301-YH.txt - raw machine, not very useful in diagnosing anything
        #self.ram.dump(0o165000, 0o165000+32)

        # start the processor loop
        instructions_executed = 0
        run = True
        while run:
            self.dl11.terminalWidnowLoop()

            # fetch opcode
            PC = self.reg.get_pc()
            instruction = self.ram.read_word(PC)
            print(f'PC:{oct(PC)}  opcode:{oct(instruction)}')
            self.reg.inc_pc(2, "fetched instruction")

            # decode and execute opcode
            run = self.dispatch_opcode(instruction)
            self.log_registers()

            instructions_executed = instructions_executed + 1
            if instructions_executed > 200:
                break

        self.dl11.terminalCloseWindow()

        if self.reg.get_pc() > 0o200:
            self.ram.dump(self.reg.get_pc()-0o20, self.reg.get_pc()+0o20)

        print (f'instructions_executed: {instructions_executed}')
        self.am.address_mode_report()

        self.dl11.dumpBuffer()