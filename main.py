"""PDP-11 Emulator"""
topofmemory = 0o377777 # 0xFFFF which is 16 bits
iospace = topofmemory - 0o27777

registers = [0, 0, 0, 0, 0, 0, 0]  # R0 R1 R2 R3 R4 R5 R6 R7
memory = bytearray(topofmemory)
pc = 0
nooperandmethods = {}
branchmethods = {}


# 104000-104377 EMT (trap & interrupt)
# 104400-104777 TRAP (trap & interrupt)

# 013400 0 001 011 100 000 000 BCS (branch)
# 16SSDD 1 110 *** *** *** *** subtract src from dst (double)
# 06SSDD 0 110 *** *** *** *** ADD add src to dst (double)

# PSW bit meanings and masks
# 15 14 current mode        0o140000
# 13 12 previous mode       0o030000
# 7 6 5 priority            0o000340
# 4 T trap                  0o000020
# 3 N result was negative   0o000010
# 2 Z result was zero       0o000004
# 1 V overflow              0o000002
# 0 C result had carry      0o000001

PSWaddress = topofmemory-3
cmodemask = 0o140000
pmoremask = 0o030000
modemask = 0o170000
prioritymask = 0o000340
trapmask = 0o000020
Nmask = 0o000010
Zmask = 0o000004
Vmask = 0o000002
Cmask = 0o000001


def PSW():
    return readmemoryword(PSWaddress)


def setPSW(mode=-1, priority=-1, trap=-1, N=-1, Z=-1, V=-1, C=-1):
    psw = PSW()
    if mode > -1:
        oldmode = psw & modemask
        psw = psw & ~cmodemask | mode << 14 | oldmode >> 2
    if priority > -1:
        psw = psw & ~prioritymask | priority << 5
    if trap > -1:
        psw = psw & ~trapmask | trap << 4
    if N > -1:
        psw = psw & ~Nmask | N << 3
    if Z > -1:
        psw = psw & ~Zmask | Z << 2
    if V > -1:
        psw = psw & ~Vmask | V << 1
    if C > -1:
        psw = psw & ~Cmask | C
    writememoryword(PSWaddress, psw)


def N():
    return PSW() & ~Nmask >> 3


def Z():
    return PSW() & ~Zmask >> 2


def V():
    return PSW() & ~Vmask >> 1


def C():
    return PSW() & ~Cmask


def readmemorybyte(address):
    """Read a byte of memory.
    Return 0o377 for anything in the vector space.
    Return 0o111 for anything in the iospace.
    Return 0 for anything else."""
    if address in range(0o0, 0o274):
        return 0o377
    elif address in range(300, iospace):
        return memory[address]
    elif address in range(iospace, topofmemory):
        return 0o111
    else:
        return 0o222


def readmemoryword(address):
    """Read a word of memory.
    Low bytes are stored at even-numbered memory locations
    and high bytes at odd-numbered memory locations.
    Returns two bytes."""
    #print(f'readmemoryword({oct(address)})')
    hi = memory[address+1]
    low = memory[address]
    # print(f'{oct(hi)} {oct(low)}')
    return (hi << 8) + low


def writememoryword(address, data):
    """write a two-word data chunk to memory.
    address needs to be even"""
    # print(f'writememoryword({oct(address)}, {oct(data)})')
    hi = (data & 0o177400) >> 8  # 1 111 111 100 000 000
    lo = data & 0o000377  # 0 000 000 011 111 111
    # print(f'hi:{oct(hi)} lo:{oct(lo)}')
    memory[address+1] = hi
    memory[address] = lo
    # print(f'hi:{oct(memory[address])} lo:{oct(memory[address-1])}')


def writememorybyte(address, data):
    """write a byte to memory.
    address can be even or odd"""
    memory[address] = data


def JMP(pc, psw, offset):
    """jump 4-56"""
    run = pc != 0
    return offset, psw


def RTS(pc, psw, offset):
    """jump to subroutine 4-58"""
    return pc + 2, psw


def SWAB(pc, psw, offset):
    """Swap Bytes 0003DO 4-17"""
    return pc + 2, psw


def MFPI(pc, psw, offset):
    """move from previous instruction space 4-77"""
    return pc + 2, psw


def MTPI(pc, psw, offset):
    """move to previous instruction space 4-78"""
    return pc + 2, psw


def HALT(pc, psw, offset):  # Halt
    return 0, psw


def NOP():  # no operation
    return pc, psw


def isbranch(instruction):
    # *0 ** xxx
    # bit 15 can be 1 or 0;mask = 0o100000
    # bits 14-12 = 0; mask = 0o070000
    # bit 11,10,9,8; mask = 0o007400
    # bits 7,6, 5,4,3, 2,1,0 are the offset; mask = 0o000377
    highbits = instruction & 0o070000 == 0o000000
    lowbits = instruction & 0o007400 in [0o0400, 0o1000, 0o1400, 0o2000, 0o2400, 0o3000, 0o3400]
    bpl = instruction & 0o107400 == 0o100000
    return (highbits and lowbits) or bpl


def branch(instruction):
    """dispatch a branch opcode
    parameter: opcode of form 0 000 000 *** *** *** """
    global pc, psw
    opcode = (instruction & 0o177400)
    offset = instruction & 0o000377
    #print(f'branch {oct(instruction)} opcode {oct(opcode)} offset {oct(offset)}')
    try:
        branchmethods[opcode](offset)
    except KeyError:
        print(f'branch not found in dictionary')
    return pc, psw


def BR(offset):  # Branch
    global pc
    print(f'{oct(pc)} BR {oct(offset)}')
    return pc + 2 * offset, psw
    # with the Branch instruction at location 500 see p. 4-37


def BNE(offset):  # branch if not equal Z=0
    global pc
    print(f'{oct(pc)} BNE {oct(offset)}')
    if Z() == 0:
        pc = pc + 2 * offset
    else:
        pc = pc + 2


def BEQ(offset):  # branch if equal Z=1
    global pc
    print(f'{oct(pc)} BEQ {oct(offset)}')
    if Z() == 1:
        pc = pc + 2 * offset
    else:
        pc = pc + 2


# Symbols in DEC book and Python operators
# A = boolean AND = &
# V = boolean OR = |
# -v = exclusive OR = ^
# ~ = boolean NOT = ~

def BGE(offset):  # branch if greater than or equal 4-47
    global pc
    print(f'{oct(pc)} BGE {oct(offset)}')
    if N() | V() == 0:
        pc = pc + 2 * offset
    else:
        pc = pc + 2


def BLT(offset):  # branch if less thn zero
    global pc
    print(f'{oct(pc)} BLT {oct(offset)}')
    if N() ^ V() == 1:
        pc = pc + 2 * offset
    else:
        pc = pc + 2


def BGT(offset):  # branch if equal Z=1
    global pc
    print(f'{oct(pc)} BGT {oct(offset)}')
    if Z() | (N() ^ V()) == 0:
        pc = pc + 2 * offset
    else:
        pc = pc + 2


def BLE(offset):  # branch if equal Z=1
    global pc
    print(f'{oct(pc)} BLE {oct(offset)}')
    if Z() | (N() ^ V()) == 1:
        pc = pc + 2 * offset
    else:
        pc = pc + 2


def BHI(offset):  # branch if higher 101000
    global pc
    print(f'{oct(pc)} BHI {oct(offset)}')
    if C() == 0 and Z() == 0:
        pc = pc + 2 * offset
    else:
        pc = pc + 2


def BLOS(offset):  # branch if lower or same 101400
    global pc
    print(f'{oct(pc)} BLOS {oct(offset)}')
    if C() | Z() == 1:
        pc = pc + 2 * offset
    else:
        pc = pc + 2


def BHIS(offset):  # branch if higher or same 103000
    global pc
    print(f'{oct(pc)} BHIS {oct(offset)}')
    if C() == 0:
        pc = pc + 2 * offset
    else:
        pc = pc + 2


def BLO(offset):  # branch if lower 103400
    """BLO is the same as BCS"""
    global pc
    print(f'{oct(pc)} BLO {oct(offset)}')
    if C() == 1:
        pc = pc + 2 * offset
    else:
        pc = pc + 2


def BPL(offset):  # branch if positive N=0
    global pc
    print(f'{oct(pc)} BPL {oct(offset)}')
    if N() == 0:
        pc = pc + 2 * offset
    else:
        pc = pc + 2


def BMI(offset):  # branch if negative N=1
    global pc
    print(f'{oct(pc)} BMI {oct(offset)}')
    if N() == 1:
        pc = pc + 2 * offset
    else:
        pc = pc + 2


def BVC(offset):  # Branch if overflow is clear V=0
    global pc
    print(f'{oct(pc)} BVC {oct(offset)}')
    if V() == 0:
        pc = pc + 2 * offset
    else:
        pc = pc + 2


def BVS(offset):  # Branch if overflow is set V=1
    global pc
    print(f'{oct(pc)} BVS {oct(offset)}')
    if V() == 1:
        pc = pc + 2 * offset
    else:
        pc = pc + 2


def BCC(offset):  # Branch if Carry is clear C=0
    global pc
    print(f'{oct(pc)} BCC {oct(offset)}')
    if C() == 0:
        pc = pc + 2 * offset
    else:
        pc = pc + 2


def BCS(offset):  # Branch if Carry is set C=1
    global pc
    print(f'{oct(pc)} BCS {oct(offset)}')
    if C() == 1:
        pc = pc + 2 * offset
    else:
        pc = pc + 2


def setupmethods():
    nooperandmethods[0o000000] = HALT
    nooperandmethods[0o000001] = HALT  # WAIT
    nooperandmethods[0o000002] = HALT  # RTI
    nooperandmethods[0o000003] = HALT  # BPT
    nooperandmethods[0o000004] = HALT  # IOT
    nooperandmethods[0o000005] = HALT  # RESET
    nooperandmethods[0o000006] = HALT  # RTT
    nooperandmethods[0o000240] = HALT  # clear
    nooperandmethods[0o000260] = HALT  # set
    branchmethods[0o000400] = BR
    branchmethods[0o001000] = BNE
    branchmethods[0o001400] = BEQ
    branchmethods[0o002000] = BGE
    branchmethods[0o002400] = BLT
    branchmethods[0o003000] = BGT
    branchmethods[0o003400] = BLE
    branchmethods[0o100000] = BPL
    branchmethods[0o100400] = BMI
    branchmethods[0o101000] = BHI
    branchmethods[0o101400] = BLOS
    branchmethods[0o102000] = BVC
    branchmethods[0o102400] = BVS
    branchmethods[0o103000] = BCC  # BHIS
    branchmethods[0o103400] = BCS  # BLO


def nooperand(pc, psw, instruction):
    """dispatch a no-operand opcode
    parameter: opcode of form * 000 0** *** *** *** """
    print(f'{oct(pc)} nooperand {oct(instruction)}')
    try:
        method = nooperandmethods[instruction]
        method
    except KeyError:
        print(f'{oct(instruction)} is not a nooperand')
    return pc + 2, psw


def INC(pc, psw, byte, destadd, dest):
    print(f'INC{byte} {oct(destadd)}')
    if byte:
        writememorybyte(destadd, dest + 1)
    else:
        writememoryword(destadd, dest + 1)
    return pc + 2, psw


def singleoperand(pc, psw, instruction):
    """dispatch a single-operand opcode
    parameter: opcode of form * 000 1** *** *** *** """
    # single operands
    # 15-6 opcode
    # 15 is 1 to indicate a byte instruction
    # 15 is 0 to indicate a word instruction
    # 5-0 dst

    #        * 000 1** *** *** ***
    # •050DD * 000 101 000 *** *** CLR clear (single)
    # •051DD * 000 101 001 *** *** COM complement (single)
    # •052DD * 000 101 010 *** *** INC increment (single)
    # •053DD * 000 101 011 *** *** DEC decrement (single)
    # •054DD * 000 101 100 *** *** NEG negate (single)
    # •055DD * 000 101 101 *** *** ADC add carry (single)
    # •056DD * 000 101 110 *** *** subtract carry (single)
    # •057DD * 000 101 111 *** *** TST test (single)
    # •060DD * 000 110 000 *** *** ROR rotate right (single)
    # •061DD * 000 110 001 *** *** ROL rotate left (single)
    # •062DD * 000 110 010 *** *** ASR artithmetic shift right (single)
    # •063DD * 000 110 011 *** *** ASL arithmetic shift left (single)
    # •067DD * 000 110 111 *** *** SXT sign extent (single)

    opcode = (instruction & 0o007700) >> 6
    destadd = instruction & 0o000077

    if instruction & 0o100000 == 0o100000:
        byte = "B"
        dest = readmemorybyte(destadd)
    else:
        byte = ""
        dest = readmemoryword(destadd)
    if opcode == 0o0005200:
        pc, psw = INC(pc, psw, byte, destadd, dest)
    else:
        print(f'{oct(pc)} singleoperand {oct(instruction)} {oct(opcode)} {oct(destadd)}')
    return pc + 2, psw


def rssoperand(pc, psw, instruction):
    """dispatch an RSS opcode
    parameter: opcode of form 0 111 *** *** *** *** """
    # register source or destination
    # 15-9 opcode
    # 8-6 reg
    # 5-0 src or dst

    # 004RDD 0 000 100 *** *** *** JSR (jump & subroutine)
    #        0 111 *** *** *** ***
    # 070RSS 0 111 000 *** *** *** MUL (register)
    # 071RSS 0 111 001 *** *** *** DIV (register)
    # 072RSS 0 111 010 *** *** *** ASH (register)
    # 073RSS 0 111 011 *** *** *** ASHC (register)
    # 074RDD 0 111 100 *** *** *** XOR (register)
    # 077R00 0 111 111 *** 000 000 SOB (jump & subroutine)
    opcode = (instruction & 0o077000) >> 9
    r = (instruction & 0o000700) >> 6
    dest = instruction & 0o000077
    print(f'{oct(pc)} rssoperand{oct(instruction)} {oct(opcode)} {oct(r)} {oct(dest)}')

    return pc + 2, psw


def MOV(pc, psw, byte, sourceadd, source, destadd, dest):
    """move 4-23"""
    print(f'{oct(pc)} MOV{byte} {oct(sourceadd)}:{oct(source)} {oct(destadd)}:{oct(dest)}')
    if byte == "B":
        writememorybyte(destadd, source)
    else:
        writememoryword(destadd, source)
    return pc + 2, psw


def CMP(pc, psw, byte, sourceadd, source, destadd, dest):
    """compare 4-24"""
    print(f'{oct(pc)} CMP{byte} {oct(source)} {oct(dest)}')
    result = source - dest
    N = 0
    if result < 0:
        N = 0o10
    Z = 0
    if result == 0:
        Z = 0o4
    signsource = source > 0
    signdest = dest > 0
    signresult = result > 0
    V = 0
    if (signsource != signdest) and (signdest == signresult):
        V = 0o2
    C = 0
    if byte:
        if result != 0o400:
            c = 0o1
    else:
        if result != 0o200000:
            c = 0o1
    newpsw = psw & 0o177760 + N + Z + V + C
    return pc + 2, newpsw


def BIT(pc, psw, byte, sourceadd, source, destadd, dest):
    """bit test 4-28"""
    print(f'{oct(pc)} BIT{byte} {oct(source)} {oct(dest)}')
    if byte == "B":
        writememorybyte(dest, readmemorybyte(source))
    else:
        writememoryword(dest, readmemoryword(source))
    return pc + 2, psw


def BIC(pc, psw, byte, sourceadd, source, destadd, dest):
    """bit clear 4-29"""
    print(f'{oct(pc)} BIC{byte} {oct(source)} {oct(dest)}')
    if byte == "B":
        writememorybyte(dest, readmemorybyte(source))
    else:
        writememoryword(dest, readmemoryword(source))
    return pc + 2, psw


def BIS(pc, psw, byte, sourceadd, source, destadd, dest):
    """bit set 4-30"""
    print(f'{oct(pc)} BIS{byte} {oct(source)} {oct(dest)}')
    if byte == "B":
        writememorybyte(dest, readmemorybyte(source))
    else:
        writememoryword(dest, readmemoryword(source))
    return pc + 2, psw


def doubleoperand(pc, psw, instruction):
    """dispatch a double-operand opcode.
    parameter: opcode of form * +++ *** *** *** ***
    where +++ = not 000 and not 111 and not 110 """
    # print(f'doubleoperand{oct(instruction)}')
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

    opcode = (instruction & 0o070000) >> 12
    sourceadd = (instruction & 0o007700) >> 6
    destadd = instruction & 0o000077

    if instruction & 0o100000 == 0o100000:
        byte = "B"
        source = readmemorybyte(sourceadd)
        dest = readmemorybyte(destadd)
    else:
        byte = ""
        source = readmemoryword(sourceadd)
        dest = readmemoryword(destadd)

    if opcode == 0o1:
        pc, psw = MOV(pc, psw, byte, sourceadd, source, destadd, dest)
    elif opcode == 0o2:
        pc, psw = CMP(pc, psw, byte, sourceadd, source, destadd, dest)
    elif opcode == 0o3:
        pc, psw = BIT(pc, psw, byte, sourceadd, source, destadd, dest)
    elif opcode == 0o4:
        pc, psw = BIC(pc, psw, byte, sourceadd, source, destadd, dest)
    elif opcode == 0o5:
        pc, psw = BIS(pc, psw, byte, sourceadd, source, destadd, dest)
    else:
        pc = 0
        psw = 0

    return pc, psw


def otheropcode(pc, psw, instruction):
    """dispatch a leftover opcode
    parameter: opcode of form that doesn't fit the rest """
    print(f'{oct(pc)} otheropcode {oct(instruction)}')
    return pc + 2, psw


def issingleoperand(instruction):
    # bits 14-12 = 0
    # bit 11 = 1
    # bits 10-9 in [1, 2]
    bits14_12 = instruction & 0o060000 == 0o000000
    bit11 = instruction & 0o006000 == 0o006000
    bits10_9 = instruction & 0o003000 in [0o001000, 0o002000]
    return bits14_12 and bit11 and bits10_9


def isrssoperand(instruction):
    # 077R00 0 111 111 *** 000 000 SOB (jump & subroutine)
    # bit 15 = 0
    # bits 14-12 = 7
    # bits 9 10 11 in [0,1,2,3,4,7]
    bit15 = instruction & 0o100000 == 0o000000
    bits14_12 = instruction & 0o070000 == 0o070000
    bits11_9 = instruction & 0o007000 in [0o000000, 0o001000, 0o002000, 0o003000, 0o004000, 0o007000]


def isdoubleoperand(instruction):
    # bits 14 - 12 in [1, 2, 3, 4, 5, 6]
    bits14_12 = instruction & 0o070000 in [0o010000, 0o020000, 0o030000, 0o040000, 0o050000, 0o060000]


def dispatchopcode(pc, psw, instruction):
    """ top-level dispatch"""
    # print (f'dispatchopcode({oct(instruction)})')
    # Patterns
    # 0 000 000 *** *** *** branch
    # * 000 0** *** *** *** no operands
    # * 000 1** *** *** *** single operands
    # 0 111 *** *** *** *** RSS
    # ELSE
    # * +++ *** *** *** *** double operands
    # where +++ = not 000 and not 111 and not 110

    # dictionary of callables
    # https://softwareengineering.stackexchange.com/questions/182093/why-store-a-function-inside-a-python-dictionary

    if isbranch(instruction):
        pc, psw = branch(instruction)
    elif instruction & 0o074000 == 0o000000:
        pc, psw = nooperand(pc, psw, instruction)
    elif issingleoperand(instruction):
        pc, psw = singleoperand(pc, psw, instruction)
    elif isrssoperand(instruction):
        pc, psw = rssoperand(pc, psw, instruction)
    elif isdoubleoperand(instruction):
        pc, psw = doubleoperand(pc, psw, instruction)
    else:
        pc, psw = otheropcode(pc, psw, instruction)
    return pc, psw


print('begin PDP11 emulator')

print('init')
pc = 0o000744
psw = 0o000000
setupmethods()

bootstraploader = [0o016701, 0o000240, 0o012702, 0o000352,
                   0o005211, 0o105711, 0o100476, 0o116162,
                   0o000002, 0o000400, 0o005267, 0o177756,
                   0o000765, 0o177560]
# from pdp-11/40 book
bootaddress = 0o000744

# salt memory to help with debugging
writememoryword(0o6700, 0o1444444)
writememoryword(0o2700, 0o1555555)

# put the boot loader into memory
for instruction in bootstraploader:
    # print()
    # print(f'bootaddress:{oct(bootaddress)}  instruction: {oct(instruction)}')
    writememoryword(bootaddress, instruction)
    # print(f'{oct(bootaddress)}:{oct(readmemoryword(bootaddress))}')
    bootaddress = bootaddress + 2

# start the processor
run = 1
psw = 1
while run:
    instruction = readmemoryword(pc)
    # print(f'run {oct(pc)} {oct(psw)} {oct(instruction)}')
    pc, psw = dispatchopcode(pc, psw, instruction)
    run = psw != 0
