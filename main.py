"""PDP-11 Emulator"""
from pdp11Hardware import ram
from pdp11Hardware import registers as reg
from pdp11Hardware import psw
from pdp11Hardware import stack
from pdp11Hardware import addressModes as am
from pdp11NoOperandOps import noOperandOps as nopr
from pdp11SingleOperandOps import singleOperandOps as sopr
from pdp11DoubleOperandOps import doubleOperandOps as dopr
from pdp11BranchOps import branchOps as br
from pdp11OtherOps import otherOps as other
from pdp11DL11 import dl11
from pdp11Boot import boot

reg = reg()
ram = ram()
psw = psw(ram)
stack = stack(psw, ram, reg)
am = am(psw, ram, reg)
nopr = nopr(psw, ram, reg, stack)
sopr = sopr(psw, ram, reg, am)
dopr = dopr(psw, ram, reg, am)
br = br(psw, ram, reg)
other = other(psw, ram, reg, am)
boot = boot(ram, reg)

def log_registers():
    """print all the registers in the log"""
    index = 0
    report = '    '
    for register in reg.registers:
        report = report + f'R{index}: {oct(register)}  '
        index = index + 1
    report = report + f'NZVC: {psw.N()}{psw.Z()}{psw.V()}{psw.C()}'
    print(report)

def dispatch_opcode(instruction):
    """ top-level dispatch"""
    #print(f'dispatch_opcode {oct(instruction)}')
    # *** Redo this based on the table in PDP-11-10 processor manual.pdf II-1-34
    run = True

    if br.is_branch(instruction):
        br.do_branch(instruction)

    elif nopr.is_no_operand(instruction):
        run = nopr.do_no_operand(instruction)

    elif sopr.is_single_operand(instruction):
        run = sopr.do_single_operand(instruction)

    elif dopr.is_double_operand_RSS(instruction):
        run = dopr.do_double_operand_RSS(instruction)

    elif dopr.is_double_operand_SSDD(instruction):
        run = dopr.do_double_operand_SSDD(instruction)

    else:
        run = other.other_opcode(instruction)

    return run

# ****************************************************
# main
# ****************************************************
print('begin PDP11 emulator')

# set up DL11
# set up the serial interface addresses
DL11 = 0o177560  # reader status register 177560
dl11 = dl11(ram, DL11)
dl11.register_with_ram()
# this must eventually be definable in a file so it has to be here

#boot.load_machine_code(boot.bootstrap_loader, bootaddress)
#boot.load_machine_code(boot.hello_world, boot.hello_address)
#reg.set_pc(0o2000, "load_machine_code")
#ram.dump(0o2000, 0o2064)

#boot.load_machine_code(boot.echo, boot.echo_address)
#ram.dump(0o1000, 0o1020)

boot.read_PDP11_assembly_file('source/M9301-YA.txt')
reg.set_pc(0o165000, "load_machine_code")
ram.dump(0o165000, 0o165777)
ram.dump(0o173000, 0o173776)

#boot.read_PDP11_assembly_file('source/M9301-YF.txt')
#reg.set_pc(0o165022, "load_machine_code")

# source/M9301-YA.txt - includes assembly; starts at 165000
# source/M9301-YF.txt - includes assembly; starts at 165022
# source/M9301-YB.txt - raw machine, not very useful in diagnosing anything
# source/M9301-YH.txt - raw machine, not very useful in diagnosing anything
#ram.dump(0o165000, 0o165000+32)

# start the processor loop
run = True
while run:
    # fetch opcode
    PC = reg.get_pc()
    instruction = ram.read_word(PC)
    print(f'{oct(PC)} {oct(instruction)}')
    log_registers()

    # decode and execute opcode
    run = dispatch_opcode(instruction)
    log_registers()

if reg.get_pc() > 0o200:
    ram.dump(reg.get_pc()-0o20, reg.get_pc()+0o20)
