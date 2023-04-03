"""PDP-11 Emulator"""
from pdp11ram import ram
from pdp11psw import psw
from pdp11reg import reg
from pdp11Boot import boot
from pdp11NoOperand import noopr
from pdp11SingleOperand import sopr
from pdp11DoubleOperand import dopr
from pdp11Branch import br
from pdp11Other import other
from pdp11DL11 import dl11

reg = reg()
ram = ram()
psw = psw(ram)
boot = boot(ram, reg)
noopr = noopr(psw, ram, reg)
sopr = sopr(psw, ram, reg)
dopr = dopr(psw, ram, reg)
br = br(psw, ram, reg)
other = other(psw, ram, reg)

def dispatch_opcode(instruction):
    """ top-level dispatch"""
    #print(f'dispatch_opcode {oct(reg.get_pc())} {oct(instruction)}')
    run = True

    if br.is_branch(instruction):
        br.do_branch(instruction)

    elif noopr.is_no_operand(instruction):
        run = noopr.do_no_operand(instruction)

    elif sopr.is_single_operand(instruction):
        run = sopr.do_single_operand(instruction)

    elif dopr.is_double_operand_RSS(instruction):
        run = dopr.do_double_operand_RSS(instruction)

    elif dopr.is_double_operand_SSDD(instruction):
        run = dopr.do_double_operand_SSDD(instruction)

    else:
        run = other.other_opcode(instruction)

    #reg.log_registers()
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
#ram.dump(0o2000, 0o2064)

boot.load_machine_code(boot.echo, boot.echo_address)
ram.dump(0o1000, 0o1020)

#start_address, end_address = boot.read_PDP11_assembly_file('source/M9301-YA.txt')
#ram.dump(start_address, start_address+32)
#reg.set_pc(start_address, "load_machine_code")

# start the processor loop
run = True
while run:
    # fetch opcode
    instruction = ram.read_word(reg.get_pc())

    # increment PC
    reg.inc_pc('main')

    # decode and execute opcode
    run = dispatch_opcode(instruction)
