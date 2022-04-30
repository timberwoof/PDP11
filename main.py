"""PDP-11 Emulator"""
from pdp11psw import psw
from pdp11ram import ram
from pdp11reg import reg

maskbyte = 0o000377
maskword = 0o177777
maskwordmsb = 0o100000
maskbytemsb = 0o000200

nooperandmethods = {}
branchmethods = {}
singleoperandmethods = {}
run = True

reg = reg()
ram = ram()
psw = psw(ram)

def JMP(offset):
    """jump 0001DD 4-56"""
    run = reg.getpc() != 0
    reg.setpc(offset)

def JSR(offset):
    """jump to subroutine 004RDD 4-58"""
    run = reg.getpc() != 0
    reg.setpc(offset)


def RTS(offset):
    """return from subroutine 00020R 4-60"""
    reg.incpc()


def SWAB(offset):
    """Swap Bytes 0003DO 4-17"""
    reg.incpc()


def MFPI(offset):
    """move from previous instruction space 4-77"""
    reg.incpc()


def MTPI(offset):
    """move to previous instruction space 4-78"""
    reg.incpc()

def BR(offset):  # Branch
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


def BNE(offset):  # branch if not equal Z=0
    print(f'{oct(reg.getpc())} {oct(instruction)} BNE {oct(offset)}')
    if psw.Z() == 0:
        reg.setpc(reg.getpc() + 2 * offset)
    else:
        reg.incpc()


def BEQ(offset):  # branch if equal Z=1
    print(f'{oct(reg.getpc())} {oct(instruction)} BEQ {oct(offset)}')
    if psw.Z() == 1:
        reg.setpc(reg.getpc() + 2 * offset)
    else:
        reg.incpc()


# Symbols in DEC book and Python operators
# A = boolean AND = &
# V = boolean OR = |
# -v = exclusive OR = ^
# ~ = boolean NOT = ~

def BGE(offset):  # branch if greater than or equal 4-47
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BGE {oct(offset)}')
    if psw.N() | psw.V() == 0:
        reg.setpc(reg.getpc() + 2 * offset)
    else:
        reg.incpc()


def BLT(offset):  # branch if less thn zero
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BLT {oct(offset)}')
    if psw.N() ^ psw.V() == 1:
        reg.setpc(reg.getpc() + 2 * offset)
    else:
        reg.incpc()


def BGT(offset):  # branch if equal Z=1
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BGT {oct(offset)}')
    if psw.Z() | (psw.N() ^ psw.V()) == 0:
        reg.setpc(reg.getpc() + 2 * offset)
    else:
        reg.incpc()


def BLE(offset):  # branch if equal Z=1
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BLE {oct(offset)}')
    if psw.Z() | (psw.N() ^ psw.V()) == 1:
        reg.setpc(reg.getpc() + 2 * offset)
    else:
        reg.incpc()


def BHI(offset):  # branch if higher 101000
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BHI {oct(offset)}')
    if psw.C() == 0 and psw.Z() == 0:
        reg.setpc(reg.getpc() + 2 * offset)
    else:
        reg.incpc()


def BLOS(offset):  # branch if lower or same 101400
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BLOS {oct(offset)}')
    if psw.C() | psw.Z() == 1:
        reg.setpc(reg.getpc() + 2 * offset)
    else:
        reg.incpc()


def BHIS(offset):  # branch if higher or same 103000
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BHIS {oct(offset)}')
    if psw.C() == 0:
        reg.setpc(reg.getpc() + 2 * offset)
    else:
        reg.incpc()


def BLO(offset):  # branch if lower 103400
    """BLO is the same as BCS"""
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BLO {oct(offset)}')
    if psw.C() == 1:
        reg.setpc(reg.getpc() + 2 * offset)
    else:
        reg.incpc()


def BPL(offset):  # branch if positive N=0
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BPL {oct(offset)}')
    if psw.N() == 0:
        reg.setpc(reg.getpc() + 2 * offset)
    else:
        reg.incpc()


def BMI(offset):  # branch if negative N=1
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BMI {oct(offset)}')
    if psw.N() == 1:
        reg.setpc(reg.getpc() + 2 * offset)
    else:
        reg.incpc()


def BVC(offset):  # Branch if overflow is clear V=0
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BVC {oct(offset)}')
    if psw.V() == 0:
        reg.setpc(reg.getpc() + 2 * offset)
    else:
        reg.incpc()


def BVS(offset):  # Branch if overflow is set V=1
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BVS {oct(offset)}')
    if psw.V() == 1:
        reg.setpc(reg.getpc() + 2 * offset)
    else:
        reg.incpc()


def BCC(offset):  # Branch if Carry is clear C=0
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BCC {oct(offset)}')
    if psw.C() == 0:
        reg.setpc(reg.getpc() + 2 * offset)
    else:
        reg.incpc()


def BCS(offset):  # Branch if Carry is set C=1
    global pc
    print(f'{oct(reg.getpc())} {oct(instruction)} BCS {oct(offset)}')
    if psw.C() == 1:
        reg.setpc(reg.getpc() + 2 * offset)
    else:
        reg.incpc()

def setupbranchmethods():
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
    opcode = (instruction & 0o177400)
    offset = instruction & maskbyte
    print(f'{oct(reg.getpc())} {oct(instruction)} branch opcode:{oct(opcode)} offset:{oct(offset)}')
    try:
        branchmethods[opcode](offset)
    except KeyError:
        print(f'branch not found in dictionary')



def HALT(instruction):  # Halt
    print (f'{oct(reg.getpc())} {oct(instruction)} HALT')
    global run
    run = False

def WAIT(instruction):  # Wait 4-75
    print (f'{oct(reg.getpc())} {oct(instruction)} WAIT unimplemented')
    reg.incpc()

def RTI(instruction):  # RTI 4-69
    print (f'{oct(reg.getpc())} {oct(instruction)} RTI unimplemented')
    reg.incpc()

def BPT(instruction):  # BPT 4-67
    print (f'{oct(reg.getpc())} {oct(instruction)} BPT unimplemented')
    reg.incpc()

def IOT(instruction):  # IOT 4-68
    print (f'{oct(reg.getpc())} {oct(instruction)} IOT unimplemented')
    reg.incpc()

def RESET(instruction):  # RESET 4-76
    print (f'{oct(reg.getpc())} {oct(instruction)} RESET unimplemented')
    reg.incpc()

def RTT(instruction):  # RTT 4-70
    print (f'{oct(reg.getpc())} {oct(instruction)} RTT unimplemented')
    reg.incpc()

def NOP(instruction):  # no operation 000240
    print (f'{oct(reg.getpc())} {oct(instruction)} NOP')
    reg.incpc()

def setupnooperandmethods():
    nooperandmethods[0o000000] = HALT
    nooperandmethods[0o000001] = WAIT
    nooperandmethods[0o000002] = RTI
    nooperandmethods[0o000003] = BPT
    nooperandmethods[0o000004] = IOT
    nooperandmethods[0o000005] = RESET
    nooperandmethods[0o000006] = RTT
    nooperandmethods[0o000240] = NOP

def isnooperand(instruction):
    return instruction & 0o074000 == 0o000000

def nooperand(instruction):
    """dispatch a no-operand opcode
    parameter: opcode of form * 000 0** *** *** *** """
    #print(f'{oct(reg.getpc())} {oct(instruction)} nooperand {oct(instruction)}')
    try:
        method = nooperandmethods[instruction]
        nooperandmethods[instruction](instruction)
    except KeyError:
        print(f'{oct(instruction)} is not a nooperand')


def CLR(instruction, dest, operand):
    print(f'{oct(reg.getpc())} {oct(instruction)} CLR {oct(dest)} {oct(operand)}')
    result = 0o0
    psw.setPSW(N=0, Z=1, V=0, C=0)
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
    psw.setPSW(N=n, Z=z, V=0, C=1)
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
    psw.setPSW(N=n, Z=z, V=0, C=1)
    return result

def INC(instruction, dest, operand):
    print(f'{oct(reg.getpc())} {oct(instruction)} INC {oct(dest)} {oct(operand)} incomplete')
    # *** this is incomplete as words need their own special little operators
    result = operand+1 & maskword
    n = 0
    if result < 0:
        n = 1
    z = 0
    if result == 0:
        z = 1
    v = 0
    if dest == 0o077777:
        v = 1
    psw.setPSW(N=n, Z=z, V=v)
    return result

def INCB(instruction, dest, operand):
    print(f'{oct(reg.getpc())} {oct(instruction)} INCB {oct(dest)} {oct(operand)} incomplete')
    # *** this is incomplete as bytes need their own special little operators
    result = operand+1 & maskbyte
    n = 0
    if result < 0:
        n = 1
    z = 0
    if result == 0:
        z = 1
    v = 0
    if dest == 0o077777:
        v = 1
    psw.setPSW(N=n, Z=z, V=v)
    return result

def DEC(instruction, dest, operand):
    print(f'{oct(reg.getpc())} {oct(instruction)} DEC {oct(dest)} {oct(operand)} incomplete')
    # *** this is incomplete as words need their own special little operators
    result = operand-1 & maskbyte
    n = 0
    if result < 0:
        n = 1
    z = 0
    if result == 0:
        z = 1
    v = 0
    if dest == 0o100000:
        v = 1
    psw.setPSW(N=n, Z=z, V=v)
    return result

def DECB(instruction, dest, operand):
    print(f'{oct(reg.getpc())} {oct(instruction)} DECB {oct(dest)} {oct(operand)} incomplete')
    # *** this is incomplete as bytes need their own special little operators
    result = operand-1 & maskbyte
    n = 0
    if result < 0:
        n = 1
    z = 0
    if result == 0:
        z = 1
    v = 0
    if dest == 0o100000:
        v = 1
    psw.setPSW(N=n, Z=z, V=v)
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
    print(f'{oct(reg.getpc())} {oct(instruction)} SXT {oct(dest)} {oct(operand)} incomplete')
    # *** this is incomplete as words need their own special little operators
    if psw.N() == 0:
        result = 0
    else:
        result = -1
    z = 0
    if result == 0:
        z = 1
    psw.setPSW(Z=z)
    return result

def setupsingleoperand():
    singleoperandmethods[0o00050] = CLR
    singleoperandmethods[0o00051] = COM
    singleoperandmethods[0o00052] = INC
    singleoperandmethods[0o00053] = DEC
    singleoperandmethods[0o00054] = NEG
    singleoperandmethods[0o00055] = CLR  #ADC
    singleoperandmethods[0o00056] = CLR  #SBC
    singleoperandmethods[0o00057] = CLR  #TST
    singleoperandmethods[0o00060] = CLR  #ROR
    singleoperandmethods[0o00061] = CLR  #ROL
    singleoperandmethods[0o00062] = CLR  #ASR
    singleoperandmethods[0o00063] = CLR  #ASL
    singleoperandmethods[0o00064] = CLR  #MARK
    singleoperandmethods[0o00065] = MFPI
    singleoperandmethods[0o00066] = MTPI
    singleoperandmethods[0o00067] = SXT  #SXT
    singleoperandmethods[0o10050] = CLR
    singleoperandmethods[0o10051] = COM
    singleoperandmethods[0o10052] = INCB
    singleoperandmethods[0o10053] = DECB
    singleoperandmethods[0o10054] = NEGB
    singleoperandmethods[0o10055] = CLR  #ADCB
    singleoperandmethods[0o10056] = CLR  #SBCB
    singleoperandmethods[0o10057] = CLR  #TSTB
    singleoperandmethods[0o10060] = CLR  #RORB
    singleoperandmethods[0o10061] = CLR  #ROLB
    singleoperandmethods[0o10062] = CLR  #ASRB
    singleoperandmethods[0o10063] = CLR  #ASLB
    singleoperandmethods[0o10065] = CLR  #MFPD
    singleoperandmethods[0o10066] = CLR  #MTPD

def issingleoperand(instruction):
    # bits 14-12 = 0
    # bit 11 = 1
    # bits 10-9 in [1, 2]
    bits14_12 = instruction & 0o070000 == 0o000000
    bit11 = instruction & 0o006000 == 0o006000
    bits10_9 = instruction & 0o003000 in [0o001000, 0o002000]
    return bits14_12 and bit11 and bits10_9


def singleoperand(instruction):
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

    opcode = (instruction & 0o107700) >> 6
    byte = (instruction & 0o100000) >> 16
    addressmode = (instruction & 0o000070) >> 3
    register = instruction & 0o000007
    address = 0o0

    if addressmode == 0:  # register
        operand = reg.get(register)
    elif addressmode == 2:  # autoincrement
        operandaddress = reg.get(register)
        if byte == 1:
            operand = ram.readbyte(operandaddress)
        else:
            operand = ram.readword(operandaddress)
        reg.set(register, reg.get(register)+1)
    elif addressmode == 4:  # autodecrement
        reg.set(register, reg.get(register)-1)
        if byte == 1:
            operand = ram.readbyte(reg.get(register))
        else:
            operand = ram.readword(reg.get(register))
    elif addressmode == 6:  # index
        operandaddress = reg.get(register) + ram.readword(reg.getpc()+2)
        if byte == 1:
            operand = ram.readbyte(reg.get(operandaddress))
        else:
            operand = ram.readword(reg.get(operandaddress))

    try:
        result = singleoperandmethods[opcode](instruction, operand)
    except KeyError:
        print(f'{oct(reg.getpc())} {oct(instruction)} singleoperandmethod {oct(opcode)} was not implemented')
        result = 0

    if addressmode == 0:  # register
        reg.set(register, result)
        reg.incpc()
    elif addressmode == 2 or addressmode == 4:  # auto__crement
        if byte == 1:
            ram.writebyte(operandaddress, result)
        else:
            ram.writeword(operandaddress, result)
        reg.incpc()
    elif addressmode == 6:  # index
        if byte == 1:
            ram.writebyte(operandaddress, result)
        else:
            ram.writeword(operandaddress, result)
        reg.incpc()
        reg.incpc()


def isrssoperand(instruction):
    # 077R00 0 111 111 *** 000 000 SOB (jump & subroutine)
    # bit 15 = 0
    # bits 14-12 = 7
    # bits 9 10 11 in [0,1,2,3,4,7]
    bit15 = instruction & 0o100000 == 0o000000
    bits14_12 = instruction & 0o070000 == 0o070000
    bits11_9 = instruction & 0o007000 in [0o000000, 0o001000, 0o002000, 0o003000, 0o004000, 0o007000]


def rssoperand(instruction):
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
    print(f'{oct(reg.getpc())} rssoperand {oct(instruction)} {oct(opcode)} {oct(r)} {oct(dest)}')

    reg.incpc()


def MOV(byte, sourceadd, source, destadd, dest):
    """move 4-23"""
    print(f'{oct(reg.getpc())} {oct(instruction)} MOV{byte} {oct(sourceadd)}:{oct(source)} {oct(destadd)}:{oct(dest)}')
    if byte == "B":
        ram.writebyte(destadd, source)
    else:
        ram.writeword(destadd, source)
    reg.incpc()


def CMP(byte, sourceadd, source, destadd, dest):
    """compare 4-24"""
    print(f'{oct(reg.getpc())} {oct(instruction)} CMP{byte} {oct(source)} {oct(dest)}')
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
    reg.incpc(), newpsw


def BIT(byte, sourceadd, source, destadd, dest):
    """bit test 4-28"""
    print(f'{oct(reg.getpc())} {oct(instruction)} BIT{byte} {oct(source)} {oct(dest)}')
    if byte == "B":
        ram.writebyte(dest, ram.readbyte(source))
    else:
        ram.writeword(dest, ram.readword(source))
    reg.incpc()


def BIC(byte, sourceadd, source, destadd, dest):
    """bit clear 4-29"""
    print(f'{oct(reg.getpc())} {oct(instruction)} BIC{byte} {oct(source)} {oct(dest)}')
    if byte == "B":
        ram.writebyte(dest, ram.readbyte(source))
    else:
        ram.writeword(dest, ram.readword(source))
    reg.incpc()


def BIS(byte, sourceadd, source, destadd, dest):
    """bit set 4-30"""
    print(f'{oct(reg.getpc())} {oct(instruction)} BIS{byte} {oct(source)} {oct(dest)}')
    if byte == "B":
        ram.writebyte(dest, ram.readbyte(source))
    else:
        ram.writeword(dest, ram.readword(source))
    reg.incpc()


def isdoubleoperand(instruction):
    # bits 14 - 12 in [1, 2, 3, 4, 5, 6]
    bits14_12 = instruction & 0o070000 in [0o010000, 0o020000, 0o030000, 0o040000, 0o050000, 0o060000]


def doubleoperand(instruction):
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
        source = ram.readbyte(sourceadd)
        dest = ram.readbyte(destadd)
    else:
        byte = ""
        source = ram.readword(sourceadd)
        dest = ram.readword(destadd)

    if opcode == 0o1:
        MOV(byte, sourceadd, source, destadd, dest)
    elif opcode == 0o2:
        CMP(byte, sourceadd, source, destadd, dest)
    elif opcode == 0o3:
        BIT(byte, sourceadd, source, destadd, dest)
    elif opcode == 0o4:
        BIC(byte, sourceadd, source, destadd, dest)
    elif opcode == 0o5:
        BIS(byte, sourceadd, source, destadd, dest)
    else:
        print(f'{oct(reg.getpc())} {oct(instruction)} is not a double operand instruction')


def otheropcode(instruction):
    """dispatch a leftover opcode
    parameter: opcode of form that doesn't fit the rest """
    print(f'{oct(reg.getpc())} {oct(instruction)} otheropcode')
    reg.incpc()


def dispatchopcode(instruction):
    """ top-level dispatch"""
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

    #print(f'{oct(reg.getpc())} {oct(instruction)}')
    if isbranch(instruction):
        branch(instruction)
    elif isnooperand(instruction):
        nooperand(instruction)
    elif issingleoperand(instruction):
        singleoperand(instruction)
    elif isrssoperand(instruction):
        rssoperand(instruction)
    elif isdoubleoperand(instruction):
        doubleoperand(instruction)
    else:
        otheropcode(instruction)


print('begin PDP11 emulator')

reg.setpc(0o000744)
setupbranchmethods()
setupnooperandmethods()

# salt memory to help with debugging
ram.writeword(0o6700, 0o1444444)
ram.writeword(0o2700, 0o1555555)

# put the boot loader into memory
# from pdp-11/40 book
bootaddress = 0o000744
bootstraploader = [0o016701, 0o000240, 0o012702, 0o000240,
                   0o005211, 0o105711, 0o100476, 0o116162,
                   0o000002, 0o000400, 0o005267, 0o177756,
                   0o000765, 0o177560]
for instruction in bootstraploader:
    # print()
    # print(f'bootaddress:{oct(bootaddress)}  instruction: {oct(instruction)}')
    ram.writeword(bootaddress, instruction)
    # print(f'{oct(bootaddress)}:{oct(ram.readword(bootaddress))}')
    bootaddress = bootaddress + 2

# start the processor
run = True
while run:
    instruction = ram.readword(reg.getpc())
    dispatchopcode(instruction)
