"""PDP-11 Emulator"""
from pdp11psw import psw
from pdp11ram import ram
from pdp11reg import reg

reg = reg()
ram = ram()
psw = psw(ram)

maskbyte = 0o000377
maskword = 0o177777
maskwordmsb = 0o100000
maskbytemsb = 0o000200

# instruction dispatch tables
no_operand_instructions = {}
branch_instructions = {}
single_operand_instructions = {}
double_operand_SSDD_instructions = {}
double_operand_RSS_instructions = {}

run = True

# from pdp-11/40 book
bootstrap_loader = [0o016701, # MOV 0o67:0o0 0o1:0o0
                    0o000240, # 0o000026
                    0o012702, # MOV 0o27:0o0 0o2:0o0
                    0o000240, # 0o000352
                    0o005211, # INC 0o0 0o0 incomplete
                    0o105711, # CLR 0o0 0o1
                    0o100376, # BPL 0o376
                    0o116162, # MOVB 0o61:0o377 0o62:0o377
                    0o000240, # 0o000002 RTI
                    0o000240, # BR 0o0
                    0o005267, # INC 0o770 0o5267
                    0o177756,
                    0o000765, # BR 0o365
                    0o177560, # 0o177560
                    0o000000] #
# NOP 0o000240
# 0o000400 BR 00 - what's at 00 now?
bootaddress = 0o000744


# http://www.retrocmp.com/how-tos/interfacing-to-a-pdp-1105/146-interfacing-with-a-pdp-1105-test-programs-and-qhello-worldq
hello_world = [0o012702,
               0o177564,
               0o012701,
               0o002032,
               0o112100,
               0o001405,
               0o110062,
               0o000002,
               0o105712,
               0o100376,
               0o000771,
               0o000000,
               0o000763,
               0o110,     0o145,     0o154,
               0o154,     0o157,     0o054,
               0o040,     0o167,     0o157,
               0o162,     0o154,     0o144,
               0o012,     0o000]
hello_address = 0o2000

def load_machine_code(code, base):
    address = base
    for instruction in code:
        # print()
        #print(f'bootaddress:{oct(address)}  instruction: {oct(instruction)}')
        ram.writeword(address, instruction)
        #print(f'{oct(address)}:{oct(ram.readword(address))}')
        address = address + 2
    reg.setpc(base)



# ****************************************************
# stack methods for use by instructions
# ****************************************************
def pushstack(value):
    """push the value onto the stack

    decrement stack pointer, write value to that address
    """
    stack = reg.getsp() - 2
    reg.setsp(stack)
    ram.writeword(stack, ram.value)

def popstack():
    """pop the stack and return that value

    get the stack value, increment the stack pointer, return value"""
    stack = reg.getsp()
    result = ram.readword(stack)
    reg.setsp(stack +2)
    return result


# ****************************************************
# No-Operand instructions - 00 00 00 through 00 00 06
# ****************************************************

def HALT(instruction):
    """00 00 00 Halt"""
    print(f'{oct(reg.getpc())} {oct(instruction)} HALT')
    global run
    run = False


def WAIT(instruction):
    """00 00 01 Wait 4-75"""
    print(f'{oct(reg.getpc())} {oct(instruction)} WAIT unimplemented')
    reg.incpc()


def RTI(instruction):
    """00 00 02 RTI return from interrupt 4-69
    PC < (SP)^; PS< (SP)^
    *** need to implement the stack
    """
    print(f'{oct(reg.getpc())} {oct(instruction)} RTI')
    reg.setpc(popstack())
    psw.setpsw(PSW=popstack())


def BPT(instruction):
    """00 00 03 BPT breakpoint trap 4-67"""
    print(f'{oct(reg.getpc())} {oct(instruction)} BPT unimplemented')
    reg.incpc()


def IOT(instruction):
    """00 00 04 IOT input/output trap 4-68"""
    print(f'{oct(reg.getpc())} {oct(instruction)} IOT unimplemented')
    reg.incpc()


def RESET(instruction):
    """00 00 05 RESET reset external bus 4-76"""
    print(f'{oct(reg.getpc())} {oct(instruction)} RESET unimplemented')
    reg.incpc()


def RTT(instruction):
    """00 00 06 RTT return from interrupt 4-70"""
    print(f'{oct(reg.getpc())} {oct(instruction)} RTT unimplemented')
    reg.incpc()


def NOP(instruction):
    """00 02 40 NOP no operation"""
    print(f'{oct(reg.getpc())} {oct(instruction)} NOP')
    reg.incpc()


def setup_no_operand_instructions():
    """populate array of no-operand methods"""
    no_operand_instructions[0o000000] = HALT
    no_operand_instructions[0o000001] = WAIT
    no_operand_instructions[0o000002] = RTI
    no_operand_instructions[0o000003] = BPT
    no_operand_instructions[0o000004] = IOT
    no_operand_instructions[0o000005] = RESET
    no_operand_instructions[0o000006] = RTT
    no_operand_instructions[0o000240] = NOP


def is_no_operand(instruction):
    """Using instruction bit pattern, determine whether it's a no-operand instruction"""
    return instruction & 0o074000 == 0o000000


def do_no_operand(instruction):
    """dispatch a no-operand opcode"""
    # parameter: opcode of form * 000 0** *** *** ***
    # print(f'{oct(reg.getpc())} {oct(instruction)} no_operand {oct(instruction)}')
    try:
        method = no_operand_instructions[instruction]
        no_operand_instructions[instruction](instruction)
    except KeyError:
        print(f'{oct(instruction)} is not a no_operand')





# ****************************************************
# Branch instructions
# 00 04 XXX - 00 34 XXX
# 10 00 XXX - 10 34 XXX
# ****************************************************
# Symbols in DEC book and Python operators
# A = boolean AND = &
# V = boolean OR = |
# -v = exclusive OR = ^
# ~ = boolean NOT = ~
# ****************************************************

def BR(offset):
    """00 04 XXX Branch"""
    global run
    oldpc = reg.getpc()
    newpc = reg.getpc() + 2 * offset
    if oldpc == newpc:
        print(f'{oct(reg.getpc())} {oct(instruction)} BR {oct(offset)} halts')
        run = False
    else:
        print(f'{oct(reg.getpc())} {oct(instruction)} BR {oct(offset)}')
        reg.setpc(newpc)
    # with the Branch instruction at location 500 see p. 4-37


def BNE(offset):
    """00 10 XXX branch if not equal Z=0"""
    print(f'{oct(reg.getpc())} {oct(instruction)} BNE {oct(offset)}')
    if psw.z() == 0:
        reg.setpcoffset(offset)
    else:
        reg.incpc()


def BEQ(offset):
    """00 14 XXX branch if equal Z=1"""
    print(f'{oct(reg.getpc())} {oct(instruction)} BEQ {oct(offset)}')
    if psw.z() == 1:
        reg.setpcoffset(offset)
    else:
        reg.incpc()

def BGE(offset):
    """00 20 XXX branch if greater than or equal 4-47"""
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BGE {oct(offset)}')
    if psw.n() | psw.v() == 0:
        reg.setpcoffset(offset)
    else:
        reg.incpc()


def BLT(offset):
    """"00 24 XXX branch if less thn zero"""
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BLT {oct(offset)}')
    if psw.n() ^ psw.v() == 1:
        reg.setpcoffset(offset)
    else:
        reg.incpc()


def BGT(offset):
    """00 30 XXX branch if equal Z=1"""
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BGT {oct(offset)}')
    if psw.z() | (psw.n() ^ psw.v()) == 0:
        reg.setpcoffset(offset)
    else:
        reg.incpc()


def BLE(offset):
    """00 34 XXX branch if equal Z=1"""
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BLE {oct(offset)}')
    if psw.z() | (psw.n() ^ psw.v()) == 1:
        reg.setpcoffset(offset)
    else:
        reg.incpc()

def BPL(offset):
    """10 00 XXX branch if positive N=0"""
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BPL {oct(offset)}')
    if psw.n() == 0:
        reg.setpcoffset(offset)
    else:
        reg.incpc()


def BMI(offset):
    """10 04 XXX branch if negative N=1"""
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BMI {oct(offset)}')
    if psw.n() == 1:
        reg.setpcoffset(offset)
    else:
        reg.incpc()

def BHI(offset):
    """10 10 XXX branch if higher"""
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BHI {oct(offset)}')
    if psw.c() == 0 and psw.z() == 0:
        reg.setpcoffset(offset)
    else:
        reg.incpc()


def BLOS(offset):
    """10 14 XXX branch if lower or same"""
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BLOS {oct(offset)}')
    if psw.c() | psw.z() == 1:
        reg.setpcoffset(offset)
    else:
        reg.incpc()


def BVC(offset):
    """10 20 XXX Branch if overflow is clear V=0"""
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BVC {oct(offset)}')
    if psw.v() == 0:
        reg.setpcoffset(offset)
    else:
        reg.incpc()


def BVS(offset):
    """10 24 XXX Branch if overflow is set V=1"""
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BVS {oct(offset)}')
    if psw.v() == 1:
        reg.setpcoffset(offset)
    else:
        reg.incpc()


def BCC(offset):
    """10 30 XXX branch if higher or same, BHIS is the sme as BCC"""
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BHIS {oct(offset)}')
    if psw.c() == 0:
        reg.setpcoffset(offset)
    else:
        reg.incpc()


def BCS(offset):
    """10 34 XXX branch if lower. BCS is the same as BLO"""
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BLO {oct(offset)}')
    if psw.c() == 1:
        reg.setpcoffset(offset)
    else:
        reg.incpc()

def setup_branch_instructions():
    branch_instructions[0o000400] = BR
    branch_instructions[0o001000] = BNE
    branch_instructions[0o001400] = BEQ
    branch_instructions[0o002000] = BGE
    branch_instructions[0o002400] = BLT
    branch_instructions[0o003000] = BGT
    branch_instructions[0o003400] = BLE
    branch_instructions[0o100000] = BPL
    branch_instructions[0o100400] = BMI
    branch_instructions[0o101000] = BHI
    branch_instructions[0o101400] = BLOS
    branch_instructions[0o102000] = BVC
    branch_instructions[0o102400] = BVS
    branch_instructions[0o103000] = BCC  # BHIS
    branch_instructions[0o103400] = BCS  # BLO

def is_branch(instruction):
    """Using instruction bit pattern, determine whether it's a branch instruction"""
    # *0 ** xxx
    # bit 15 can be 1 or 0;mask = 0o100000
    # bits 14-12 = 0; mask = 0o070000
    # bit 11,10,9,8; mask = 0o007400
    # bits 7,6, 5,4,3, 2,1,0 are the offset; mask = 0o000377
    highbits = instruction & 0o070000 == 0o000000
    lowbits = instruction & 0o007400 in [0o0400, 0o1000, 0o1400, 0o2000, 0o2400, 0o3000, 0o3400]
    bpl = instruction & 0o107400 == 0o100000
    return (highbits and lowbits) or bpl


def do_branch(instruction):
    """dispatch a branch opcode"""
    #parameter: opcode of form 0 000 000 *** *** ***
    opcode = (instruction & 0o177400)
    offset = instruction & maskbyte
    #print(f'{oct(reg.getpc())} {oct(instruction)} branch opcode:{oct(opcode)} offset:{oct(offset)}')
    try:
        branch_instructions[opcode](offset)
    except KeyError:
        print(f'branch not found in dictionary')


# ****************************************************
# Single-Operand instructions -
# 00 50 DD - 00 77 DD
# 10 50 DD - 10 77 DD
# ****************************************************

def JMP(instruction, dest, operand):
    """00 01 DD JMP jump 4-56"""
    print(f'{oct(reg.getpc())} {oct(instruction)} JMP {oct(dest)} {oct(operand)}')
    run = reg.getpc() != 0 # *** only for development
    reg.setpc(dest)

def SWAB(instruction, dest, operand):
    """00 03 DD Swap Bytes 4-17"""
    print(f'{oct(reg.getpc())} {oct(instruction)} JMP {oct(dest)} {oct(operand)}')
    run = reg.getpc() != 0 # *** only for development
    reg.setpc(dest)


def CLR(instruction, dest, operand):
    print(f'{oct(reg.getpc())} {oct(instruction)} CLR {oct(dest)} {oct(operand)}')
    result = 0o0
    psw.setpsw(N=0, Z=1, V=0, C=0)
    return result


def COM(instruction, dest, operand):
    print(f'{oct(reg.getpc())} {oct(instruction)} COM {oct(dest)} {oct(operand)}')
    result = ~operand & maskword
    n = 0
    if result & maskwordmsb == maskwordmsb:
        n = 1
    z = 0
    if result == 0:
        z = 1
    psw.setpsw(N=n, Z=z, V=0, C=1)
    return result


def COMB(instruction, dest, operand):
    print(f'{oct(reg.getpc())} {oct(instruction)} COMB {oct(dest)} {oct(operand)}')
    result = ~operand & maskbyte
    n = 0
    if result & maskbytemsb == maskbytemsb:
        n = 1
    z = 0
    if result == 0:
        z = 1
    psw.setpsw(N=n, Z=z, V=0, C=1)
    return result


def INC(instruction, dest, operand):
    print(f'{oct(reg.getpc())} {oct(instruction)} INC {oct(dest)} {oct(operand)}')
    # *** this is incomplete as words need their own special little operators
    result = operand + 1 & maskword
    n = 0
    if result < 0:
        n = 1
    z = 0
    if result == 0:
        z = 1
    v = 0
    if dest == 0o077777:
        v = 1
    psw.setpsw(N=n, Z=z, V=v)
    return result


def INCB(instruction, dest, operand):
    print(f'{oct(reg.getpc())} {oct(instruction)} INCB {oct(dest)} {oct(operand)}')
    # *** this is incomplete as bytes need their own special little operators
    result = operand + 1 & maskbyte
    n = 0
    if result < 0:
        n = 1
    z = 0
    if result == 0:
        z = 1
    v = 0
    if dest == 0o077777:
        v = 1
    psw.setpsw(N=n, Z=z, V=v)
    return result


def DEC(instruction, dest, operand):
    print(f'{oct(reg.getpc())} {oct(instruction)} DEC {oct(dest)} {oct(operand)}')
    # *** this is incomplete as words need their own special little operators
    result = operand - 1 & maskbyte
    n = 0
    if result < 0:
        n = 1
    z = 0
    if result == 0:
        z = 1
    v = 0
    if dest == 0o100000:
        v = 1
    psw.setpsw(N=n, Z=z, V=v)
    return result


def DECB(instruction, dest, operand):
    print(f'{oct(reg.getpc())} {oct(instruction)} DECB {oct(dest)} {oct(operand)}')
    # *** this is incomplete as bytes need their own special little operators
    result = operand - 1 & maskbyte
    n = 0
    if result < 0:
        n = 1
    z = 0
    if result == 0:
        z = 1
    v = 0
    if dest == 0o100000:
        v = 1
    psw.setpsw(N=n, Z=z, V=v)
    return result


def NEG(instruction, dest, operand):
    print(f'{oct(reg.getpc())} {oct(instruction)} NEG {oct(dest)} {oct(operand)}')
    result = -operand & maskword
    return result


def NEGB(instruction, dest, operand):
    print(f'{oct(reg.getpc())} {oct(instruction)} NEGB {oct(dest)} {oct(operand)}')
    result = -operand & maskbyte
    return result

def SXT(instruction, dest, operand):
    print(f'{oct(reg.getpc())} {oct(instruction)} SXT {oct(dest)} {oct(operand)}')
    # *** this is incomplete as words need their own special little operators
    if psw.n() == 0:
        result = 0
    else:
        result = -1
    z = 0
    if result == 0:
        z = 1
    psw.setpsw(Z=z)
    return result


def setup_single_operand_instructions():
    """set up table of single-operand instructions"""
    single_operand_instructions[0o001000] = JMP
    single_operand_instructions[0o005000] = CLR
    single_operand_instructions[0o005100] = COM
    single_operand_instructions[0o005200] = INC
    single_operand_instructions[0o005300] = DEC
    single_operand_instructions[0o005400] = NEG
    single_operand_instructions[0o005500] = CLR  # ADC
    single_operand_instructions[0o005600] = CLR  # SBC
    single_operand_instructions[0o005700] = CLR  # TST
    single_operand_instructions[0o006000] = CLR  # ROR
    single_operand_instructions[0o006100] = CLR  # ROL
    single_operand_instructions[0o006200] = CLR  # ASR
    single_operand_instructions[0o006300] = CLR  # ASL
    single_operand_instructions[0o006400] = CLR  # MARK
    single_operand_instructions[0o006500] = MFPI
    single_operand_instructions[0o006600] = MTPI
    single_operand_instructions[0o006700] = SXT  # SXT
    single_operand_instructions[0o105000] = CLR
    single_operand_instructions[0o105100] = COM
    single_operand_instructions[0o105200] = INCB
    single_operand_instructions[0o105300] = DECB
    single_operand_instructions[0o105400] = NEGB
    single_operand_instructions[0o105500] = CLR  # ADCB
    single_operand_instructions[0o105600] = CLR  # SBCB
    single_operand_instructions[0o105700] = CLR  # TSTB
    single_operand_instructions[0o106000] = CLR  # RORB
    single_operand_instructions[0o106100] = CLR  # ROLB
    single_operand_instructions[0o106200] = CLR  # ASRB
    single_operand_instructions[0o106300] = CLR  # ASLB
    single_operand_instructions[0o106500] = CLR  # MFPD
    single_operand_instructions[0o106600] = CLR  # MTPD


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
    bits_14_13_12 = instruction & 0o070000 == 0o000000
    bits_11_10_9 = instruction & 0o007000 in [0o006000, 0o005000]
    return bits_14_13_12 and bits_11_10_9

def do_single_operand(instruction):
    """dispatch a single-operand opcode"""
    # parameter: opcode of form * 000 1** *** *** ***
    # single operands
    # 15-6 opcode
    # 15 is 1 to indicate a byte instruction
    # 15 is 0 to indicate a word instruction
    # 5-0 dst

    #print(f'{oct(reg.getpc())} decoding {oct(instruction)}')

    byte = (instruction & 0o100000) >> 16
    opcode = (instruction & 0o107700)
    addressmode = (instruction & 0o000070) >> 3
    register = instruction & 0o000007
    operandaddress = 0o177776
    operand = 0o177776

    #print(f'byte:{byte} opcode:{oct(opcode)} addressmode:{oct(addressmode)} register:{oct(register)}')

    if byte == 1:
        read = ram.readbyte
        write = ram.writebyte
        crement = 1
    else:
        read = ram.readword
        write = ram.writeword
        crement = 2
    if register == 6 or register == 7:
        crement = 2

    if addressmode == 0:  # register direct
        #print('register direct')
        operand = reg.get(register)
        operandaddress = 0o0
    elif addressmode == 1:  # register deferred
        #print('register deferred')
        operandaddress = reg.get(register)
        operand = read(operandaddress)
    elif addressmode == 2:  # autoincrement direct
        #print('autoincrement direct')
        operandaddress = reg.get(register)
        operand = read(operandaddress)
    elif addressmode == 3:  # autoincrement deferred
        #print('autoincrement deferred')
        operandaddress = reg.get(register)
        operand = read(operandaddress)
    elif addressmode == 4:  # autodecrement direct
        #print('autodecrement direct')
        reg.set(register, reg.get(register) - crement)
        operandaddress = reg.get(register)
        operand = read(operandaddress)
    elif addressmode == 5:  # autodecrement deferred
        #print('autodecrement deferred')
        reg.set(register, reg.get(register) - 2)
        operandaddress = reg.get(register)
        operand = read(operandaddress)
    elif addressmode == 6: # index
        operandaddress = reg.get(register)
        operand = read(operandaddress) + read(reg.getpc()+2)
    elif addressmode == 7: # index deferred
        operandaddress = reg.get(register)
        operandaddress = read(operandaddress) + read(reg.getpc()+2)
        operand = read(operandaddress)

    try:
        #print(f'{oct(reg.getpc())} {oct(instruction)} single_operand opcode:{oct(opcode)} mode:{addressmode} @operand:{oct(operandaddress)} operand:{oct(operand)}')
        result = single_operand_instructions[opcode](instruction, operandaddress, operand)
    except KeyError:
        print(f'{oct(reg.getpc())} {oct(instruction)} single_operandmethod {oct(opcode)} was not implemented')
        result = operand

    if addressmode == 0:  # register direct
        reg.set(register, result)
    if addressmode == 1:  # register deferred
        write(operandaddress, result)
    elif addressmode == 2:  # autoincrement direct
        write(operandaddress, result)
        reg.set(register, reg.get(register) + crement)
    elif addressmode == 3:  # autoincrement deferred
        write(operandaddress, result)
        reg.set(register, reg.get(register) + 2)
    elif addressmode == 4:  # autodecrement direct
        write(operandaddress, result)
    elif addressmode == 5:  # autodecrement deferred
        write(operandaddress, result)
    elif addressmode == 6:  # index
        write(operandaddress, result)
        reg.incpc()
    elif addressmode == 7:  # index deferred
        write(operandaddress, result)
        reg.incpc()

    reg.incpc()

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

    psw.setpsw(N=N, Z=Z, V=V, C=C)
    reg.incpc()

def MOV(b, read, write, source, dest):
    """01 SS DD move 4-23"""
    print(f'{oct(reg.getpc())} {oct(instruction)} MOV{b} {oct(source)} {oct(dest)}')
    write(dest, read(source))
    reg.incpc()
    # code in example is
    # 002000 012702  177564 -> mov     #177564,r2
    # we interpret this as
    # 0o2000 0o12702 MOV 0o27 0o2
    # 01 SS DD: SS = 0o27   DD = 0o02
    # that means R7 which is special. That's the PC
    # that 2 means it's an immediate-mode instruction:
    # operand follows the instruction
    # Page 3-3 makes it clear.
    # O have to generalize the mode thing somehow.

def CMP(b, read, write, source, dest):
    """compare 4-24"""
    print(f'{oct(reg.getpc())} {oct(instruction)} CMP{b} {oct(source)} {oct(dest)}')
    result = read(source) - read(dest)
    set_condition_codes(result)

def BIT(b, read, write, source, dest):
    """bit test 4-28"""
    print(f'{oct(reg.getpc())} {oct(instruction)} BIT{b} {oct(source)} {oct(dest)}')
    souce = read(src)
    dest = read(dest)
    result = source & dest
    write(dest, result)
    set_condition_codes(source, dest, result)
    reg.incpc()


def BIC(b, read, write, source, dest):
    """bit clear 4-29"""
    print(f'{oct(reg.getpc())} {oct(instruction)} BIC{b} {oct(source)} {oct(dest)}')
    souce = read(src)
    dest = read(dest)
    result = ~source & dest
    write(dest, result)
    set_condition_codes(source, dest, result)
    reg.incpc()


def BIS(b, read, write, source, dest):
    """bit set 4-30"""
    print(f'{oct(reg.getpc())} {oct(instruction)} BIS{b} {oct(source)} {oct(dest)}')
    souce = read(src)
    dest = read(dest)
    result = source | dest
    write(dest, result)
    set_condition_codes(source, dest, result)
    reg.incpc()

def ADD(b, read, write, source, dest):
    """06 SS DD ADD add 4-25"""
    print(f'{oct(reg.getpc())} {oct(instruction)} ADD{b} {oct(source)} {oct(dest)}')
    souce = read(src)
    dest = read(dest)
    result = source + dest
    write(dest, result)
    set_condition_codes(source, dest, result)
    reg.incpc()

def SUB(b, read, write, source, dest):
    """06 SS DD SUB add 4-25"""
    print(f'{oct(reg.getpc())} {oct(instruction)} SUB{b} {oct(source)} {oct(dest)}')
    souce = read(src)
    dest = read(dest)
    result = source + ~dest + 1
    write(dest, result)
    set_condition_codes(source, dest, result)
    reg.incpc()

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
    bits14_12 = instruction & 0o070000 in [0o010000, 0o020000, 0o030000, 0o040000, 0o050000, 0o060000]
    return bits14_12

def do_double_operand_SSDD(instruction):
    """dispatch a double-operand opcode.
    parameter: opcode of form * +++ *** *** *** ***
    where +++ = not 000 and not 111 and not 110 """
    # print(f'double_operand_SSDD{oct(instruction)}')
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

    byte = (instruction & 0o100000) >> 16
    opcode = (instruction & 0o070000)
    source = (instruction & 0o007700) >> 6
    dest = instruction & 0o000077

    if byte == 1:
        read = ram.readbyte
        write = ram.writebyte
        b = 'B'
    else:
        read = ram.readword
        write = ram.writeword
        b = ''

    try:
        double_operand_SSDD_instructions[opcode](b, read, write, source, dest)
    except KeyError:
        print(f'{oct(reg.getpc())} {oct(instruction)} {oct(opcode)} is not a double operand instruction')


# ****************************************************
# Double-Operand RSS instructions - 07 0R SS through 07 7R SS
# ****************************************************

def MUL(register, source):
    """07 0R SS MUL 4-31"""
    print(f'{oct(reg.getpc())} {oct(instruction)} MUL unimplemented')
    reg.incpc()

def DIV(register, source):
    """07 1R SS DIV 4-32"""
    print(f'{oct(reg.getpc())} {oct(instruction)} DIV unimplemented')
    reg.incpc()

def ASH(register, source):
    """07 2R SS ASH"""
    print(f'{oct(reg.getpc())} {oct(instruction)} ASH unimplemented')
    reg.incpc()

def ASHC(register, source):
    """07 3R SS ASHC"""
    print(f'{oct(reg.getpc())} {oct(instruction)} ASHC unimplemented')
    reg.incpc()

def XOR(register, dest):
    """07 4R DD XOR"""
    print(f'{oct(reg.getpc())} {oct(instruction)} XOR unimplemented')
    reg.incpc()

def SOB(register, source):
    """07 7R NN SOB"""
    print(f'{oct(reg.getpc())} {oct(instruction)} SOB unimplemented')
    reg.incpc()

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
    dest = instruction & 0o000077
    try:
        double_operand_RSS_instructions[opcode](instruction, register, dest)
    except KeyError:
        print(f'{oct(reg.getpc())} double_operand_RSS {oct(instruction)} {oct(opcode)} {oct(register)} {oct(dest)} KeyError')
    reg.incpc()


# ****************************************************
# Other instructions
# ****************************************************

def RTS(instruction):
    """00 20 0R RTS return from subroutine 00020R 4-60"""
    print(f'{oct(reg.getpc())} {oct(instruction)} RTS unimplemented')
    reg.incpc()

def JSR(instruction):
    """00 4R DD JSR jump to subroutine

    |  004RDD 4-58
    |  pushstack(reg)
    |  reg <- PC+2
    |  PC <- (dst)
    """
    print(f'{oct(reg.getpc())} {oct(instruction)} JSR')
    pushstack(ram.readword(register))
    reg.set(register, reg.incpc())
    reg.setpc(dest)

def MARK(instruction):
    """00 64 NN mark 46-1"""
    print(f'{oct(reg.getpc())} {oct(instruction)} MARK unimplemented')
    reg.incpc()

def MFPI(instruction):
    """00 65 SS move from previous instruction space 4-77"""
    print(f'{oct(reg.getpc())} {oct(instruction)} MFPI unimplemented')
    reg.incpc()

def MTPI(instruction, dest, operand):
    """00 66 DD move to previous instruction space 4-78"""
    print(f'{oct(reg.getpc())} {oct(instruction)} MTPI unimplemented')
    reg.incpc()

def other_opcode(instruction):
    """dispatch a leftover opcode"""
    # parameter: opcode of form that doesn't fit the rest
    print(f'{oct(reg.getpc())} {oct(instruction)} other_opcode')
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

# ****************************************************
# General Instruction Dispatch
# ****************************************************
def dispatch_opcode(instruction):
    """ top-level dispatch"""
    # print(f'{oct(reg.getpc())} {oct(instruction)}')
    if is_branch(instruction):
        do_branch(instruction)

    elif is_no_operand(instruction):
        do_no_operand(instruction)

    elif is_single_operand(instruction):
        do_single_operand(instruction)

    elif is_double_operand_RSS(instruction):
        do_double_operand_RSS(instruction)

    elif is_double_operand_SSDD(instruction):
        do_double_operand_SSDD(instruction)

    else:
        other_opcode(instruction)


print('begin PDP11 emulator')

setup_branch_instructions()
setup_no_operand_instructions()
setup_single_operand_instructions()
setup_double_operand_SSDD_instructions()
setup_double_operand_RSS_instructions()

#load_machine_code(bootstrap_loader, bootaddress)

load_machine_code(hello_world, hello_address)

# start the processor loop
run = True

while run:
    instruction = ram.readword(reg.getpc())
    dispatch_opcode(instruction)
