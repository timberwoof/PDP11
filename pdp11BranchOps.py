"""pdp11BranchOps.py branch instructions"""

from pdp11Hardware import ram
from pdp11Hardware import registers as reg
from pdp11Hardware import psw

# masks for accessing words and bytes
mask_byte = 0o000377
mask_word = 0o177777
mask_word_msb = 0o100000
mask_byte_msb = 0o000200

class branchOps:
    def __init__(self, psw, ram, reg):
        print('initializing pdp11BranchOps.br')
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

        self.branch_instruction_names = {}
        self.branch_instruction_names[0o000400] = "BR"
        self.branch_instruction_names[0o001000] = "BNE"
        self.branch_instruction_names[0o001400] = "BEQ"
        self.branch_instruction_names[0o002000] = "BGE"
        self.branch_instruction_names[0o002400] = "BLT"
        self.branch_instruction_names[0o003000] = "BGT"
        self.branch_instruction_names[0o003400] = "BLE"
        self.branch_instruction_names[0o100000] = "BPL"
        self.branch_instruction_names[0o100400] = "BMI"
        self.branch_instruction_names[0o101000] = "BHI"
        self.branch_instruction_names[0o101400] = "BLOS"
        self.branch_instruction_names[0o102000] = "BVC"
        self.branch_instruction_names[0o102400] = "BVS"
        self.branch_instruction_names[0o103000] = "BCC"  # BHIS
        self.branch_instruction_names[0o103400] = "BCS"  # BLO


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
        if offset & 0o200 == 0o200:
            # offset is negative, say 0o0371 0o11111001
            offset = offset - 0o377
        oldpc = self.reg.get_pc()
        newpc = self.reg.get_pc() + 2 * offset -2
        if oldpc == newpc:
            global run
            run = False
        else:
            self.reg.set_pc(newpc, "BR")
        # with the Branch instruction at location 500 see p. 4-37

    def BNE(self, instruction, offset):
        """00 10 XXX branch if not equal Z=0"""
        if self.psw.Z() == 0:
            self.reg.set_pc_2x_offset(offset, "BNE")

    def BEQ(self, instruction, offset):
        """00 14 XXX branch if equal Z=1"""
        if self.psw.Z() == 1:
            self.reg.set_pc_2x_offset(offset, "BEQ")

    def BGE(self, instruction, offset):
        """00 20 XXX branch if greater than or equal 4-47"""
        if self.psw.N() | self.psw.V() == 0:
            self.reg.set_pc_2x_offset(offset, "BGE")

    def BLT(self, instruction, offset):
        """"00 24 XXX branch if less thn zero"""
        if self.psw.N() ^ self.psw.V() == 1:
            self.reg.set_pc_2x_offset(offset, "BLT")

    def BGT(self, instruction, offset):
        """00 30 XXX branch if equal Z=1"""
        if self.psw.Z() | (self.psw.N() ^ self.psw.V()) == 0:
            self.reg.set_pc_2x_offset(offset, "BTG")

    def BLE(self, instruction, offset):
        """00 34 XXX branch if equal Z=1"""
        if self.psw.Z() | (self.psw.N() ^ self.psw.V()) == 1:
            self.reg.set_pc_2x_offset(offset, "BLE")

    def BPL(self, instruction, offset):
        """01 00 XXX branch if positive N=0"""
        if self.psw.N() == 0 and self.psw.Z() == 0:
            self.reg.set_pc_2x_offset(offset, 'BPL')

    def BMI(self, instruction, offset):
        """10 04 XXX branch if negative N=1"""
        if self.psw.N() == 1:
            self.reg.set_pc_2x_offset(offset, 'BMI')

    def BHI(self, instruction, offset):
        """10 10 XXX branch if higher"""
        if self.psw.C() == 0 and self.psw.Z() == 0:
            self.reg.set_pc_2x_offset(offset, 'BHI')

    def BLOS(self, instruction, offset):
        """10 14 XXX branch if lower or same"""
        if self.psw.C() | self.psw.Z() == 1:
            self.reg.set_pc_2x_offset(offset, 'BLOS')

    def BVC(self, instruction, offset):
        """10 20 XXX Branch if overflow is clear V=0"""
        if self.psw.V() == 0:
            self.reg.set_pc_2x_offset(offset, 'BVC')

    def BVS(self, instruction, offset):
        """10 24 XXX Branch if overflow is set V=1"""
        if self.psw.V() == 1:
            self.reg.set_pc_2x_offset(offset, 'BVS')

    def BCC(self, instruction, offset):
        """10 30 XXX branch if higher or same, BHIS is the sme as BCC"""
        if self.psw.C() == 0:
            self.reg.set_pc_2x_offset(offset, 'BCC')

    def BCS(self, instruction, offset):
        """10 34 XXX branch if lower. BCS is the same as BLO"""
        if self.psw.C() == 1:
            self.reg.set_pc_2x_offset(offset, 'BCS')

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
        print(f'{oct(self.reg.get_pc()-2)} {oct(instruction)} {self.branch_instruction_names[opcode]} {oct(offset)}')
        result = True
        self.branch_instructions[opcode](instruction, offset)
        return result
