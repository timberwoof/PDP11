"""PDP-11 Emulator"""
from pdp11ram import ram
from pdp11psw import psw
from pdp11reg import reg
from pdp11boot import boot
from pdp11noopr import noopr
from pdp11sopr import sopr
from pdp11dopr import dopr
from pdp11br import br
reg = reg()
ram = ram()
psw = psw(ram)
boot = boot(ram)
noopr = noopr(psw, ram, reg)
sopr = sopr(psw, ram, reg)
dopr = dopr(psw, ram, reg)
br = br(psw, ram, reg)

# masks for accessing words and bytes
mask_byte = 0o000377
mask_word = 0o177777
mask_word_msb = 0o100000
mask_byte_msb = 0o000200

run = True

# ****************************************************
# stack methods for use by instructions
# ****************************************************
def pushstack(value):
    """push the value onto the stack

    decrement stack pointer, write value to that address
    """
    stack = reg.get_sp() - 2
    reg.set_sp(stack)
    ram.write_word(stack, ram.value)

def popstack():
    """pop the stack and return that value

    get the stack value, increment the stack pointer, return value"""
    stack = reg.get_sp()
    result = ram.read_word(stack)
    reg.set_sp(stack + 2)
    return result

def is_byte_instruction(instruction):
    """if it's a byte instruction, return 'B'"""
    if instruction & 0o100000 == 0o100000:
        return 'B'
    else:
        return ''







# ****************************************************
# Other instructions
# ****************************************************

def RTS(instruction):
    """00 20 0R RTS return from subroutine 00020R 4-60"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} RTS unimplemented')
    reg.inc_pc('RTS')

def JSR(instruction):
    """00 4R DD JSR jump to subroutine

    |  004RDD 4-58
    |  pushstack(reg)
    |  reg <- PC+2
    |  PC <- (dst)
    """
    print(f'    {oct(reg.get_pc())} {oct(instruction)} JSR')
    pushstack(ram.read_word(register))
    reg.set(register, reg.inc_pc('JSR'))
    reg.set_pc(dest, "JSR")


def other_opcode(instruction):
    """dispatch a leftover opcode"""
    # parameter: opcode of form that doesn't fit the rest
    print(f'    {oct(reg.get_pc())} {oct(instruction)} other_opcode')
    if instruction & 0o177000 == 0o002000:
        RTS(instruction)
    elif instruction & 0o177000 == 0o004000:
        JSR(instruction)
    elif instruction & 0o177700 == 0o006400:
        MARK(instruction)
    elif instruction & 0o177700 == 0o006500:
        MFPI(instruction)
    elif instruction & 0o177700 == 0o006600:
        MTPI(instruction)
    else:
        #print(f'{oct(instruction)} is an unknown instruction')
        reg.set_pc(0o0, "other_opcode")

# ****************************************************
# General Instruction Dispatch
# ****************************************************
def dispatch_opcode(instruction):
    """ top-level dispatch"""
    print(f'dispatch_opcode {oct(reg.get_pc())} {oct(instruction)}')
    run = True

    if br.is_branch(instruction):
        br.do_branch(instruction)

    elif noopr.is_no_operand(instruction):
        run = noopr.do_no_operand(instruction)

    elif sopr.is_single_operand(instruction):
        sopr.do_single_operand(instruction)

    elif dopr.is_double_operand_RSS(instruction):
        dopr.do_double_operand_RSS(instruction)

    elif dopr.is_double_operand_SSDD(instruction):
        dopr.do_double_operand_SSDD(instruction)

    else:
        other_opcode(instruction)

    return run

# ****************************************************
# main
# ****************************************************
print('begin PDP11 emulator')

#boot.load_machine_code(boot.bootstrap_loader, bootaddress)
#boot.load_machine_code(boot.hello_world, hello_address)

start_address = boot.read_PDP11_assembly_file('source/M9301-YA.txt')
reg.set_pc(start_address, "load_machine_code")

# start the processor loop
run = True
while run:
    # fetch opcode
    instruction = ram.read_word(reg.get_pc())
    # decode and execute opcode
    run = dispatch_opcode(instruction)
