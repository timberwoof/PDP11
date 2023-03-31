"""PDP-11 Emulator"""
from pdp11ram import ram
from pdp11psw import psw
from pdp11reg import reg
from pdp11boot import boot
from pdp11noopr import noopr
from pdp11br import br
reg = reg()
ram = ram()
psw = psw(ram)
boot = boot(ram)
noopr = noopr(psw, ram, reg)
br = br(psw, ram, reg)

# masks for accessing words and bytes
mask_byte = 0o000377
mask_word = 0o177777
mask_word_msb = 0o100000
mask_byte_msb = 0o000200

# instruction dispatch tables
single_operand_instructions = {}
"""single_operand_instructions

    :param instruction: opcode
    :param dest: address
    :param operand: operand
    :param B: 'B' for byte instruction, '' for word
    :param mask:
    :param maskmsb: 
"""
double_operand_SSDD_instructions = {}
double_operand_RSS_instructions = {}

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
# Single-Operand instructions -
# 00 50 DD - 00 77 DD
# 10 50 DD - 10 77 DD
# ****************************************************

def JMP(instruction, dest, operand, B, mask, maskmsb):
    """00 01 DD JMP jump 4-56"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} JMP {oct(dest)} {oct(operand)}')
    global run
    reg.set_pc(operand, 'JMP')
    return reg.get_pc()

def SWAB(instruction, dest, operand, B, mask, maskmsb):
    """00 03 DD Swap Bytes 4-17"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} SWAB {oct(dest)} {oct(operand)}')
    reg.inc_pc()
    result = (operand & 0xFF00) << 8 + (operand & 0x00FF) >> 8
    reg.inc_pc()
    return result

def CLR(instruction, dest, operand, B, mask, maskmsb):
    print(f'    {oct(reg.get_pc())} {oct(instruction)} CLR{B} {oct(dest)} {oct(operand)}')
    reg.inc_pc()
    result = 0o0
    psw.set_PSW(N=0, Z=1, V=0, C=0)
    reg.inc_pc()
    return result

def COM(instruction, dest, operand, B, mask, maskmsb):
    print(f'    {oct(reg.get_pc())} {oct(instruction)} COM{B} {oct(dest)} {oct(operand)}')
    reg.inc_pc("COM{B}")
    result = ~operand & mask
    n = 0
    if result & maskmsb == maskmsb:
        n = 1
    z = 0
    if result == 0:
        z = 1
    psw.set_PSW(N=n, Z=z, V=0, C=1)
    return result

def INC(instruction, dest, operand, B, mask, maskmsb):
    instructionname = f'INC{is_byte_instruction(instruction)}'
    print(f'    {oct(reg.get_pc())} {oct(instruction)} {instructionname} {oct(dest)} {oct(operand)}')
    reg.inc_pc()
    # *** this is incomplete as words need their own special little operators
    result = operand + 1 & mask_word
    n = 0
    if result < 0:
        n = 1
    z = 0
    if result == 0:
        z = 1
    v = 0
    if dest == 0o077777: # what the fuck am I doing here?
        v = 1
    psw.set_PSW(N=n, Z=z, V=v)
    return result

def DEC(instruction, dest, operand, B, mask, maskmsb):
    print(f'    {oct(reg.get_pc())} {oct(instruction)} DEC{B} {oct(dest)} {oct(operand)}')
    reg.inc_pc()
    # *** this is incomplete as words need their own special little operators
    result = operand - 1 & mask_byte
    n = 0
    if result < 0:
        n = 1
    z = 0
    if result == 0:
        z = 1
    v = 0
    if dest == 0o100000: # what the fuck am I doing here?
        v = 1
    psw.set_PSW(N=n, Z=z, V=v)
    return result

def NEG(instruction, dest, operand, B, mask, maskmsb):
    print(f'    {oct(reg.get_pc())} {oct(instruction)} NEG{B} {oct(dest)} {oct(operand)}')
    reg.inc_pc()
    result = -operand & mask
    return result

def ADC(instruction, dest, operand, B, mask, maskmsb):
    """Add Carry"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} ADC{B} {oct(dest)} {oct(operand)}')
    reg.inc_pc()
    result = dest + psw.C()
    n = 0
    if result < 0:
        n = 1
    z = 0
    if result == 0:
        z = 1
    v = 0
    if dest == 0o077777 and psw.C() == 1: # what the fuck am I doing here?
        v = 1
    c = 0
    if dest == 0o077777 and psw.C() == 1: # what the fuck am I doing here?
        c = 1
    psw.set_PSW(N=n, Z=z, V=v, C=c)
    return result

def SBC(instruction, dest, operand, B, mask, maskmsb):
    """subtract Carry"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} SBC{B} {oct(dest)} {oct(operand)}')
    reg.inc_pc()
    result = dest - operand
    n = 0
    if result < 0:
        n = 1
    z = 0
    if result == 0:
        z = 1
    v = 0
    if dest == 0o1000000 and psw.C() == 1: # what the fuck am I doing here?
        v = 1
    c = 0
    if dest == 0o0 and psw.C() == 1: # what the fuck am I doing here?
        c = 1
    psw.set_PSW(N=n, Z=z, V=v, C=c)
    return result

def TST(instruction, dest, operand, B, mask, maskmsb):
    print(f'    {oct(reg.get_pc())} {oct(instruction)} TST{B} {oct(dest)} {oct(operand)}')
    reg.inc_pc()
    result = operand
    n = 0
    if result & mask_word == mask_word:
        n = 1
    z = 0
    if result == 0:
        z = 1
    psw.set_PSW(N=n, Z=z, V=0, C=1)
    return result

def ROR(instruction, dest, operand, B, mask, maskmsb):
    """ROR rotate right"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} ROR{B} {oct(dest)} {oct(operand)}')
    reg.inc_pc()
    result = operand >> 1
    n = 0
    if result & maskmsb == maskmsb:
        n = 1
    z = 0
    if result == 0:
        z = 1
    psw.set_PSW(N=n, Z=z, V=0, C=1)
    return result

def ROL(instruction, dest, operand, B, mask, maskmsb):
    """ROL rotate left"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} ROR{B} {oct(dest)} {oct(operand)}')
    reg.inc_pc()
    result = operand << 1
    n = 0
    if result & maskmsb == maskmsb:
        n = 1
    z = 0
    if result == 0:
        z = 1
    psw.set_PSW(N=n, Z=z, V=0, C=1)
    return result

def ASR(instruction, dest, operand, B, mask, maskmsb):
    """ASR arithmetic shift right"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} ASR{B} {oct(dest)} {oct(operand)}')
    reg.inc_pc()
    result = operand >> 1
    n = 0
    if result & maskmsb == maskmsb:
        n = 1
    z = 0
    if result == 0:
        z = 1
    psw.set_PSW(N=n, Z=z, V=0, C=1)
    return result

def ASL(instruction, dest, operand, B, mask, maskmsb):
    """ASL arithmetic shift left"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} ASL{B} {oct(dest)} {oct(operand)}')
    reg.inc_pc()
    result = operand << 1
    n = 0
    if result & maskmsb == maskmsb:
        n = 1
    z = 0
    if result == 0:
        z = 1
    psw.set_PSW(N=n, Z=z, V=0, C=1)
    return result

def SXT(instruction, dest, operand, B, mask, maskmsb):
    print(f'    {oct(reg.get_pc())} {oct(instruction)} SXT{B} {oct(dest)} {oct(operand)}')
    reg.inc_pc()
    # *** this is incomplete as words need their own special little operators
    if psw.N() == 0:
        result = 0
    else:
        result = -1
    z = 0
    if result == 0:
        z = 1
    psw.set_PSW(Z=z)
    return result

def addressing_mode_get(B, mode_register):
    """copy the value from the location indicated by byte_register"""
    addressmode = (mode_register & 0o70) >> 3
    register = mode_register & 0o07

    print(f'    addressing_mode_get {B} mode:{oct(addressmode)} reg:{oct(register)}')

    if B == 'B':
        read = ram.read_byte
        increment = 1
        b = 'B'
    else:
        read = ram.read_word
        increment = 2
        b = ''
    if register == 6 or register == 7:
        increment = 2

    if addressmode == 0:
        print('    register: Rn: register contains operand')
        operand = reg.get(register)
        #print(f'R{oct(register)} = operand:{oct(operand)}')
    elif addressmode == 1:
        print('    register deferred: @Rn or (Rn): register contains address of operand')
        operandaddress = reg.get(register)
        operand = operandaddress
        print(f'{oct(operandaddress)} = operand:{oct(operand)}')
    elif addressmode == 2:
        print('    autoincrement: (Rn)+: register contains address of operand then incremented')
        operandaddress = reg.get(register)
        operand = read(operandaddress)
        if register != 7:
            reg.set(register, reg.get(register) + increment)
            # increment 1 for B and 2 for W
        #print(f'R{register}={oct(operandaddress)} = operand:{oct(operand)}')
    elif addressmode == 3:  # autoincrement deferred
        print('    autoincrement deferred: @(Rn) +: register contains address of address of operand, then incremented')
        operandaddress = reg.get(register)
        operand = read(operandaddress)
        if register != 7:
            reg.set(register, reg.get(register) + 2)
            # increment always by 2
        #print(f'{oct(operandaddress)} = operand:{oct(operand)}')
    elif addressmode == 4:  # autodecrement direct
        print('    autodecrement: -(rn): register is decremented, then contains address of operand')
        reg.set(register, reg.get(register) - increment)
        # decrement 1 for B and 2 for W
        operandaddress = reg.get(register)
        operand = read(operandaddress)
        #print(f'R{register}={oct(operandaddress)} = operand:{oct(operand)}')
    elif addressmode == 5:  # autodecrement deferred
        print('    autodecrement deferred: @-(Rn): register is decremented, then contains address of address of operand')
        reg.set(register, reg.get(register) - 2)
        # decrement always by 2
        operandaddress = reg.get(register)
        operand = read(operandaddress)
        #print(f'R{register}={oct(operandaddress)} = operand:{oct(operand)}')
    elif addressmode == 6:
        print('    index: X(Rn): value X is added to Register to produce address of operand')
        operandaddress = reg.get(register) + read(reg.get_pc() + 2)
        operand = read(operandaddress)
        print(f'    R{register}={oct(operandaddress)} = operand:{oct(operand)}')
    elif addressmode == 7: # index deferred
        print('    index deferred: @X(Rn): value X is added to Register then used as address of address of operand')
        operandaddress = reg.get(register)
        operandaddress = read(operandaddress) + read(reg.get_pc() + 2)
        operand = read(operandaddress)
        #print(f'R{register}={oct(operandaddress)} = operand:{oct(operand)}')
    return operand

def addressing_mode_set(B, mode_register, result):
    """copy the result into the place indicated by mode_register

    Parameters:
        B: 'B' or ''
        mode_register: SS or DD
        result: what to store there
    """
    addressmode = (mode_register & 0o70) >> 3
    register = mode_register & 0o07

    print(f'    addressing_mode_set("{B}", {oct(mode_register)}, {oct(result)})')
    print(f'    addressing_mode_set {B} mode:{oct(addressmode)} reg:{register} result:{oct(result)}')

    if B == 'B':
        write = ram.write_byte
        increment = 1
    else:
        write = ram.write_word
        increment = 2
    if register == 6 or register == 7:
        increment = 2

    if addressmode == 0:  # register direct
        #print('    register direct')
        reg.set(register, result)
    if addressmode == 1:  # register deferred
        #print('    register deferred')
        operandaddress = reg.get(register)
        write(operandaddress, result)
    elif addressmode == 2:  # autoincrement direct
        #print('    autoincrement direct')
        operandaddress = reg.get(register)
        write(operandaddress, result)
    elif addressmode == 3:  # autoincrement deferred
        #print('    autoincrement deferred')
        operandaddress = reg.get(register)
        write(operandaddress, result)
        reg.set(register, reg.get(register) + 2)
    elif addressmode == 4:  # autodecrement direct
        #print('    autodecrement direct')
        operandaddress = reg.get(register)
        write(operandaddress, result)
    elif addressmode == 5:  # autodecrement deferred
        #print('    autodecrement deferred')
        operandaddress = reg.get(register)
        write(operandaddress, result)
        reg.inc_pc('ams6')
    elif addressmode == 6:  # index
        operandaddress = reg.get(register)
        #print(f'index R{register}={oct(operandaddress)} <- {oct(result)}')
        write(operandaddress, result)
        reg.inc_pc('ams6')
    elif addressmode == 7:  # index deferred
        #print('    index deferred')
        operandaddress = reg.get(register)
        write(operandaddress, result)
        reg.inc_pc('ams7')

def setup_single_operand_instructions():
    """set up table of single-operand instructions"""
    single_operand_instructions[0o000100] = JMP
    single_operand_instructions[0o000300] = SWAB
    single_operand_instructions[0o005000] = CLR
    single_operand_instructions[0o005100] = COM
    single_operand_instructions[0o005200] = INC
    single_operand_instructions[0o005300] = DEC
    single_operand_instructions[0o005400] = NEG
    single_operand_instructions[0o005500] = ADC
    single_operand_instructions[0o005600] = SBC
    single_operand_instructions[0o005700] = TST
    single_operand_instructions[0o006000] = ROR
    single_operand_instructions[0o006100] = ROL
    single_operand_instructions[0o006200] = ASR
    single_operand_instructions[0o006300] = ASL
    single_operand_instructions[0o006400] = MARK
    single_operand_instructions[0o006500] = MFPI
    single_operand_instructions[0o006600] = MTPI
    single_operand_instructions[0o006700] = SXT
    single_operand_instructions[0o105000] = CLR # CLRB
    single_operand_instructions[0o105100] = COM # COMB
    single_operand_instructions[0o105200] = INC # INCB
    single_operand_instructions[0o105300] = DEC # DECB
    single_operand_instructions[0o105400] = NEG # NEGB
    single_operand_instructions[0o105500] = ADC  # ADCB
    single_operand_instructions[0o105600] = SBC  # SBCB
    single_operand_instructions[0o105700] = TST  # TSTB
    single_operand_instructions[0o106000] = ROR  # RORB
    single_operand_instructions[0o106100] = ROL  # ROLB
    single_operand_instructions[0o106200] = ASR  # ASRB
    single_operand_instructions[0o106300] = ASL  # ASLB
    single_operand_instructions[0o106500] = 0  # MFPD
    single_operand_instructions[0o106600] = 0  # MTPD

def is_single_operand(instruction):
    """Using instruction bit pattern, determine whether it's a single-operand instruction"""
    # 15  12 10  876 543 210
    #  * 000 101 *** *** ***
    #  * 000 110 *** *** ***
    # bit 15 can be 1 or 0
    # bits 14,13,12 must be 0
    # bits 11,10,9 must be 5 or 6
    # bits 8,7,6 can be anything
    # bits 5-0 can be anything
    # 0o000301 is one of these
    # 0 000 000 101 *** ***
    #print(f'    is_single_operand({type(instruction)} {oct(instruction)})')
    bits_14_13_12 = instruction & 0o070000 == 0o000000
    bits_11_10_9 = instruction & 0o007000 in [0o006000, 0o005000]
    isJMP = instruction & 0o000700 == 0o000100
    isSWAB = instruction & 0o000700 == 0o000300
    #print(f'    is_single_operand {bits_14_13_12} {bits_11_10_9} {isSWAB}')
    return (bits_14_13_12 and bits_11_10_9) or isSWAB or isJMP

def do_single_operand(instruction):
    """dispatch a single-operand opcode"""
    # parameter: opcode of form * 000 1** *** *** ***
    # single operands
    # 15-6 opcode
    # 15 is 1 to indicate a byte instruction
    # 15 is 0 to indicate a word instruction
    # 5-0 dst
    if (instruction & 0o100000) == 0o100000:
        B = 'B'
        mask = mask_byte
        maskmsb = mask_byte_msb
    else:
        B = ''
        mask = mask_word
        maskmsb = mask_word_msb
    opcode = (instruction & 0o107700)
    source = instruction & 0o000077
    source_value = addressing_mode_get(B, source)

    reg.log_registers()

    try:
        print(f'    {oct(reg.get_pc())} {oct(instruction)} single_operand opcode:{oct(opcode)} source_value:{oct(source_value)}')
        result = single_operand_instructions[opcode](instruction, source_value, source_value, B, mask, maskmsb)
    except KeyError:
        print(f'    {oct(reg.get_pc())} {oct(instruction)} single_operandmethod {oct(opcode)} was not implemented')
        result = source

    addressing_mode_set(B, source_value, result)

# ****************************************************
# Double-Operand SSDD instructions
# 01 SS DD through 06 SS DD
# 11 SS DD through 16 SS DD
# ****************************************************

def set_condition_codes(source, dest, result):
    if result < 0:
        N = 1
    else:
        N = 0

    if result == 0:
        Z = 1
    else:
        Z = 0

    signsource = source > 0
    signdest = dest > 0
    signresult = result > 0
    if (signsource != signdest) and (signdest == signresult):
        V = 1
    else:
        V = 0

    byte = False # *** this needs to be set up right
    if byte:
        if result != 0o400:
            C = 1
        else:
            C = 0
    else:
        if result != 0o200000:
            C = 1
        else:
            C = 0

    psw.set_PSW(N=N, Z=Z, V=V, C=C)
    reg.inc_pc('scc')

def MOV(instruction, b, source, dest):
    """01 SS DD move 4-23

    (dst) < (src)"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} MOV{b} {oct(source)} {oct(dest)}')
    reg.inc_pc("MOV")
    source_value = addressing_mode_get(b, source)
    addressing_mode_set(b, dest, source_value)
    return source

def CMP(instruction, b, source, dest):
    """compare 4-24

    (src)-(dst)"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} CMP{b} {oct(source)} {oct(dest)}')
    source_value = addressing_mode_get(b, source)
    dest_value = addressing_mode_get(b, dest)
    result = source_value - dest_value
    set_condition_codes(source, dest, result)
    reg.inc_pc('CMP')
    return result

def BIT(instruction, b, source, dest):
    """bit test 4-28

    (src) ^ (dst)"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} BIT{b} {oct(source)} {oct(dest)}')
    result = source & dest
    set_condition_codes(source, dest, result)
    reg.inc_pc('BIT')
    return result

def BIC(instruction, b, source, dest):
    """bit clear 4-29

    (dst) < ~(src)&(dst)"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} BIC{b} {oct(source)} {oct(dest)}')
    result = ~source & dest
    set_condition_codes(source, dest, result)
    reg.inc_pc('BIC')
    return result

def BIS(instruction, b, source, dest):
    """bit set 4-30
    (dst) < (src) v (dst)"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} BIS{b} {oct(source)} {oct(dest)}')
    result = source | dest
    set_condition_codes(source, dest, result)
    reg.inc_pc('BIS')
    return result

def ADD(instruction, b, source, dest):
    """06 SS DD ADD add 4-25

    (dst) < (src) + (dst)"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} ADD{b} {oct(source)} {oct(dest)}')
    result = source + dest
    set_condition_codes(source, dest, result)
    reg.inc_pc('ADD')
    return result

def SUB(instruction, b, source, dest):
    """06 SS DD SUB add 4-25

    (dst) < (dst) + ~(src) + 1"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} SUB{b} {oct(source)} {oct(dest)}')
    result = source + ~dest + 1
    set_condition_codes(source, dest, result)
    reg.inc_pc('SUB')
    return result

def setup_double_operand_SSDD_instructions():
    double_operand_SSDD_instructions[0o010000] = MOV;
    double_operand_SSDD_instructions[0o020000] = CMP;
    double_operand_SSDD_instructions[0o030000] = BIT;
    double_operand_SSDD_instructions[0o040000] = BIC;
    double_operand_SSDD_instructions[0o050000] = BIS;
    double_operand_SSDD_instructions[0o060000] = ADD;
    double_operand_SSDD_instructions[0o160000] = SUB;

def is_double_operand_SSDD(instruction):
    """Using instruction bit pattern, determine whether it's a souble operand instruction"""
    # bits 14 - 12 in [1, 2, 3, 4, 5, 6]
    #print (f'is_double_operand_SSDD {oct(instruction)}&0o070000={instruction & 0o070000}')
    bits14_12 = instruction & 0o070000 in [0o010000, 0o020000, 0o030000, 0o040000, 0o050000, 0o060000]
    return bits14_12

def do_double_operand_SSDD(instruction):
    """dispatch a double-operand opcode.
    parameter: opcode of form * +++ *** *** *** ***
    where +++ = not 000 and not 111 and not 110 """
    #print(f'double_operand_SSDD {oct(instruction)}')
    # double operands
    # 15-12 opcode
    # 11-6 src
    # 5-0 dst

    #        * +++ *** *** *** *** double operands
    # •1SSDD * 001 *** *** *** *** MOV move source to destination (double)
    # •2SSDD * 010 *** *** *** *** CMP compare src to dst (double)
    # •3SSDD * 011 *** *** *** *** BIT bit test (double)
    # •4SSDD * 100 *** *** *** *** BIC bit clear (double)
    # •5SSDD * 101 *** *** *** *** BIS bit set (double)

    if (instruction & 0o100000) >> 15 == 1:
        b = 'B'
    else:
        b = ''
    opcode = (instruction & 0o070000)
    source = (instruction & 0o007700) >> 6
    dest = (instruction & 0o000077)

    try:
        result = double_operand_SSDD_instructions[opcode](instruction, b, source, dest)
    except KeyError:
        print(f'    {oct(reg.get_pc())} {oct(instruction)} {oct(opcode)} is not a double operand instruction')
    reg.inc_pc('do_double_operand')

# ****************************************************
# Double-Operand RSS instructions - 07 0R SS through 07 7R SS
# ****************************************************

def MUL(instruction, register, source):
    """07 0R SS MUL 4-31

    (R, R+1) < (R, R+1) * (src)"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} MUL unimplemented')
    source_value = addressing_mode_get(source)
    result = register * source_value
    set_condition_codes(source, dest, result)
    reg.inc_pc('MUL')
    return result

def DIV(instruction, register, source):
    """07 1R SS DIV 4-32

    (R, R+1) < (R, R+1) / (src)"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} DIV unimplemented')
    source_value = addressing_mode_get(source)
    # *** needs to get word from register and its neighbor
    # *** needs to get word from source
    result = register / source_value
    set_condition_codes(source, dest, result)
    reg.inc_pc('DIV')
    return result

def ASH(instruction, register, source):
    """07 2R SS ASH arithmetic shift 4-33

    R < R >> NN """
    print(f'    {oct(reg.get_pc())} {oct(instruction)} ASH unimplemented')
    result = register >> source
    set_condition_codes(source, dest, result)
    reg.inc_pc('SDH')
    return result

def ASHC(instruction, register, source):
    """07 3R SS ASHC arithmetic shift combined 4-34

    (R, R+1) < (R, R+1) >> N"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} ASHC unimplemented')
    source_value = addressing_mode_get(source)
    result = register >> source
    set_condition_codes(source, dest, result)
    reg.inc_pc('ASHC')
    return result

def XOR(instruction, register, source):
    """07 4R DD XOR 4-35

    (dst) < R ^ (dst)"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} XOR unimplemented')
    source_value = addressing_mode_get(source)
    result = register ^ source_value
    set_condition_codes(source, dest, result)
    reg.inc_pc('XOR')
    return result

def SOB(instruction, register, source):
    """07 7R NN SOB sutract one and branch 4-63

    R < R -1, then maybe branch"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} SOB unimplemented')
    source_value = addressing_mode_get(source)
    result = register * source_value
    set_condition_codes(source, dest, result)
    # *** set PC appropriately
    reg.inc_pc('SOB')
    return result

def setup_double_operand_RSS_instructions():
    """Set up jump table for RSS RDD RNN instructions"""
    double_operand_RSS_instructions[0o070000] = MUL
    double_operand_RSS_instructions[0o071000] = DIV
    double_operand_RSS_instructions[0o072000] = ASH
    double_operand_RSS_instructions[0o073000] = ASHC
    double_operand_RSS_instructions[0o074000] = XOR
    double_operand_RSS_instructions[0o077000] = SOB

def is_double_operand_RSS(instruction):
    """Using instruction bit pattern, determine whether it's an RSS RDD RNN instruction"""
    # 077R00 0 111 111 *** 000 000 SOB (jump & subroutine)
    # bit 15 = 0
    # bits 14-12 = 7
    # bits 9 10 11 in [0,1,2,3,4,7]
    bit15 = instruction & 0o100000 == 0o000000
    bits14_12 = instruction & 0o070000 == 0o070000
    bits11_9 = instruction & 0o077000 in [0o070000, 0o071000, 0o072000, 0o073000, 0o074000, 0o077000]
    return bit15 and bits14_12 and bits11_9

def do_double_operand_RSS(instruction):
    """dispatch an RSS opcode"""
    # parameter: opcode of form 0 111 *** *** *** ***
    # register source or destination
    # 15-9 opcode
    # 8-6 reg
    # 5-0 src or dst
    opcode = (instruction & 0o077000)
    register = (instruction & 0o000700) >> 6
    source = instruction & 0o000077

    try:
        double_operand_RSS_instructions[opcode](instruction, register, source)
    except KeyError:
        print(f'    {oct(reg.get_pc())} double_operand_RSS {oct(instruction)} {oct(opcode)} R{register} {oct(dest)} KeyError')
    reg.inc_pc('do_double_operand_RSS')

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

def MARK(instruction):
    """00 64 NN mark 46-1"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} MARK unimplemented')
    reg.inc_pc('MARK')

def MFPI(instruction):
    """00 65 SS move from previous instruction space 4-77"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} MFPI unimplemented')
    reg.inc_pc('MFPI')

def MTPI(instruction, dest, operand):
    """00 66 DD move to previous instruction space 4-78"""
    print(f'    {oct(reg.get_pc())} {oct(instruction)} MTPI unimplemented')
    reg.inc_pc('MTPI')

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
    result = True

    if br.is_branch(instruction):
        br.do_branch(instruction)

    elif noopr.is_no_operand(instruction):
        result = noopr.do_no_operand(instruction)

    elif is_single_operand(instruction):
        do_single_operand(instruction)

    elif is_double_operand_RSS(instruction):
        do_double_operand_RSS(instruction)

    elif is_double_operand_SSDD(instruction):
        do_double_operand_SSDD(instruction)

    else:
        other_opcode(instruction)

    return result

# ****************************************************
# main
# ****************************************************
print('begin PDP11 emulator')

setup_single_operand_instructions()
setup_double_operand_SSDD_instructions()
setup_double_operand_RSS_instructions()

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
