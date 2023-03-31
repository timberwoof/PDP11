"""pdp11br.py branch instructions"""

from pdp11psw import psw
from pdp11ram import ram
from pdp11reg import reg

# masks for accessing words and bytes
mask_byte = 0o000377
mask_word = 0o177777
mask_word_msb = 0o100000
mask_byte_msb = 0o000200

class br:
    def __init__(self, psw, ram, reg):
        print('initializing pdp11br')
        self.psw = psw
        self.ram = ram
        self.reg = reg
        self.branch_instructions = {}
        self.branch_instructions[0o000400] = self.BR
        self.branch_instructions[0o001000] = self.BNE
        self.branch_instructions[0o001400] = self.BEQ
        self.branch_instructions[0o002000] = self.BGE
        self.branch_instructions[0o002400] = self.BLT
        self.branch_instructions[0o003000] = self.BGT
        self.branch_instructions[0o003400] = self.BLE
        self.branch_instructions[0o100000] = self.BPL
        self.branch_instructions[0o100400] = self.BMI
        self.branch_instructions[0o101000] = self.BHI
        self.branch_instructions[0o101400] = self.BLOS
        self.branch_instructions[0o102000] = self.BVC
        self.branch_instructions[0o102400] = self.BVS
        self.branch_instructions[0o103000] = self.BCC  # BHIS
        self.branch_instructions[0o103400] = self.BCS  # BLO

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

    def BR(self, instruction, offset):
        """00 04 XXX Branch"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} BR {oct(offset)}')
        if offset & 0o200 == 0o200:
            # offset is negative, say 0o0371 0o11111001
            offset = offset - 0o377
        oldpc = self.reg.get_pc()
        newpc = self.reg.get_pc() + 2 * offset + 2
        if oldpc == newpc:
            print(f'    {oct(self.reg.get_pc())} {oct(instruction)} BR {oct(offset)} halts')
            global run
            run = False
        else:
            self.reg.set_pc(newpc, "BR")
        # with the Branch instruction at location 500 see p. 4-37

    def BNE(self, instruction, offset):
        """00 10 XXX branch if not equal Z=0"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} BNE {oct(offset)}')
        if self.psw.Z() == 0:
            self.reg.set_pc_offset(offset, "BNE")
        else:
            self.reg.inc_pc('BNE')

    def BEQ(self, instruction, offset):
        """00 14 XXX branch if equal Z=1"""
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} BEQ {oct(offset)}')
        if self.psw.Z() == 1:
            self.reg.set_pc_offset(offset, "BEQ")
        else:
            self.reg.inc_pc('BEQ')

    def BGE(self, instruction, offset):
        """00 20 XXX branch if greater than or equal 4-47"""
        global pc
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} BGE {oct(offset)}')
        if self.psw.N() | self.psw.V() == 0:
            self.reg.set_pc_offset(offset, "BGE")
        else:
            self.reg.inc_pc('BGE')

    def BLT(self, instruction, offset):
        """"00 24 XXX branch if less thn zero"""
        global pc
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} BLT {oct(offset)}')
        if self.psw.N() ^ self.psw.V() == 1:
            self.reg.set_pc_offset(offset, "BLT")
        else:
            self.reg.inc_pc('BLT')

    def BGT(self, instruction, offset):
        """00 30 XXX branch if equal Z=1"""
        global pc
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} BGT {oct(offset)}')
        if self.psw.Z() | (self.psw.N() ^ self.psw.V()) == 0:
            self.reg.set_pc_offset(offset, "BTG")
        else:
            self.reg.inc_pc('BGT')

    def BLE(self, instruction, offset):
        """00 34 XXX branch if equal Z=1"""
        global pc
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} BLE {oct(offset)}')
        if self.psw.Z() | (self.psw.N() ^ self.psw.V()) == 1:
            self.reg.set_pc_offset(offset, "BLE")
        else:
            self.reg.inc_pc('BLE')

    def BPL(self, instruction, offset):
        """10 00 XXX branch if positive N=0"""
        global pc
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} BPL {oct(offset)}')
        if self.psw.N() == 0:
            self.reg.set_pc_offset(offset, 'BPL')
        else:
            self.reg.inc_pc('BPL')

    def BMI(self, instruction, offset):
        """10 04 XXX branch if negative N=1"""
        global pc
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} BMI {oct(offset)}')
        if self.psw.N() == 1:
            self.reg.set_pc_offset(offset, 'BMI')
        else:
            self.reg.inc_pc('BMI')

    def BHI(self, instruction, offset):
        """10 10 XXX branch if higher"""
        global pc
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} BHI {oct(offset)}')
        if self.psw.C() == 0 and self.psw.Z() == 0:
            self.reg.set_pc_offset(offset, 'BHI')
        else:
            self.reg.inc_pc('BHI')

    def BLOS(self, instruction, offset):
        """10 14 XXX branch if lower or same"""
        global pc
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} BLOS {oct(offset)}')
        if self.psw.C() | self.psw.Z() == 1:
            self.reg.set_pc_offset(offset, 'BLOS')
        else:
            self.reg.inc_pc('BLOS')

    def BVC(self, instruction, offset):
        """10 20 XXX Branch if overflow is clear V=0"""
        global pc
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} BVC {oct(offset)}')
        if self.psw.V() == 0:
            self.reg.set_pc_offset(offset, 'BVC')
        else:
            self.reg.inc_pc('BVC')

    def BVS(self, instruction, offset):
        """10 24 XXX Branch if overflow is set V=1"""
        global pc
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} BVS {oct(offset)}')
        if self.psw.V() == 1:
            self.reg.set_pc_offset(offset, 'BVS')
        else:
            self.reg.inc_pc('BVS')

    def BCC(self, instruction, offset):
        """10 30 XXX branch if higher or same, BHIS is the sme as BCC"""
        global pc
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} BHIS {oct(offset)}')
        if self.psw.C() == 0:
            self.reg.set_pc_offset(offset, 'BCC')
        else:
            self.reg.inc_pc('BCC')

    def BCS(self, instruction, offset):
        """10 34 XXX branch if lower. BCS is the same as BLO"""
        global pc
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} BLO {oct(offset)}')
        if self.psw.C() == 1:
            self.reg.set_pc_offset(offset, 'BCS')
        else:
            self.reg.inc_pc('BCS')

    def is_branch(self, instruction):
        """Using instruction bit pattern, determine whether it's a branch instruction"""
        # *0 ** xxx
        # bit 15 can be 1 or 0; mask = 0o100000
        # bits 14-12 = 0; mask = 0o070000
        # bit 11,10,9,8; mask = 0o007400
        # bits 7,6, 5,4,3, 2,1,0 are the offset; mask = 0o000377
        blankbits = instruction & 0o070000 == 0o000000
        lowbits0 = instruction & 0o107400 in [          0o000400, 0o001000, 0o001400, 0o002000, 0o002400, 0o003000, 0o003400]
        lowbits1 = instruction & 0o107400 in [0o100000, 0o100400, 0o101000, 0o101400, 0o102000, 0o102400, 0o103000, 0o103400]
        #print(f'{instruction} {blankbits} and ({lowbits0} or {lowbits1})')
        return blankbits and (lowbits0 or lowbits1)

    def do_branch(self, instruction):
        """dispatch a branch opcode"""
        #parameter: opcode of form 0 000 000 *** *** ***
        opcode = (instruction & 0o177400)
        offset = instruction & mask_byte
        #print(f'    {oct(self.reg.getpc())} {oct(instruction)} branch opcode:{oct(opcode)} offset:{oct(offset)}')
        result = True
        try:
            result = self.branch_instructions[opcode](instruction, offset)
        except KeyError:
            print(f'    {oct(self.reg.get_pc())} {oct(instruction)} branch not found in dictionary')
            result = False
        return result
