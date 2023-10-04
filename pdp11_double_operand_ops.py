"""pdp11_double_operand_ops.py double operand instructions"""

MASK_WORD = 0o177777
MASK_WORD_MSB = 0o100000
MASK_BYTE_MSB = 0o000200
MASK_LOW_BYTE = 0o000377
MASK_HIGH_BYTE = 0o177400

class DoubleOperandOps:
    """Implements PDP11 double-operand instructions"""
    def __init__(self, reg, ram, psw, am, sw):
        #print('initializing doubleOperandOps')
        self.reg = reg
        self.ram = ram
        self.psw = psw
        self.am = am
        self.sw = sw

        self.double_operand_RSS_instructions = {}
        self.double_operand_RSS_instructions[0o070000] = self.MUL
        self.double_operand_RSS_instructions[0o071000] = self.DIV
        self.double_operand_RSS_instructions[0o072000] = self.ASH
        self.double_operand_RSS_instructions[0o073000] = self.ASHC
        self.double_operand_RSS_instructions[0o074000] = self.XOR
        self.double_operand_RSS_instructions[0o077000] = self.SOB

        self.double_operand_RSS_instruction_names = {}
        self.double_operand_RSS_instruction_names[0o070000] = "MUL"
        self.double_operand_RSS_instruction_names[0o071000] = "DIV"
        self.double_operand_RSS_instruction_names[0o072000] = "ASH"
        self.double_operand_RSS_instruction_names[0o073000] = "ASHC"
        self.double_operand_RSS_instruction_names[0o074000] = "XOR"
        self.double_operand_RSS_instruction_names[0o077000] = "SOB"

        self.double_operand_SSDD_instructions = {}
        # SSDD instructions with B variants the usual way
        self.double_operand_SSDD_instructions[0o010000] = self.MOV
        self.double_operand_SSDD_instructions[0o020000] = self.CMP
        self.double_operand_SSDD_instructions[0o030000] = self.BIT
        self.double_operand_SSDD_instructions[0o040000] = self.BIC
        self.double_operand_SSDD_instructions[0o050000] = self.BIS

        # SSDD instructions that break the rule
        self.double_operand_SSDD_instructions[0o060000] = self.ADDSUB

        self.double_operand_SSDD_instruction_names = {}
        self.double_operand_SSDD_instruction_names[0o010000] = "MOV"
        self.double_operand_SSDD_instruction_names[0o020000] = "CMP"
        self.double_operand_SSDD_instruction_names[0o030000] = "BIT"
        self.double_operand_SSDD_instruction_names[0o040000] = "BIC"
        self.double_operand_SSDD_instruction_names[0o050000] = "BIS"
        self.double_operand_SSDD_instruction_names[0o060000] = "ADD"
        self.double_operand_SSDD_instruction_names[0o110000] = "MOVB"
        self.double_operand_SSDD_instruction_names[0o120000] = "CMPB"
        self.double_operand_SSDD_instruction_names[0o130000] = "BITB"
        self.double_operand_SSDD_instruction_names[0o140000] = "BICB"
        self.double_operand_SSDD_instruction_names[0o150000] = "BISB"
        self.double_operand_SSDD_instruction_names[0o160000] = "SUB"

    # ****************************************************
    # Double-Operand RSS instructions - 07 0R SS through 07 7R SS
    # ****************************************************

    # Where a register pair is used
    # (written below as "(Reg, Reg+1)",
    # the first register contains the low-order portion of the operand
    # and must be an even numbered register.
    # The next higher numbered register contains
    # the high-order portion of the operand (or the remainder).
    # An exception is the multiply instruction; Reg may be odd,
    # but if it is, the high 16 bits of the result are not stored.

    def MUL(self, register, source):
        """07 0R SS MUL 4-31

        (R, R+1) < (R, R+1) * (src)"""
        # get_c: set if the result < -2^15 or result >= 2^15-1
        #print(f'    MUL {register} * {source}')
        a = self.reg.registers[register]
        result = a * source
        self.psw.set_n('', result)
        self.psw.set_z('', result)
        self.psw.set_psw(v=0)
        self.psw.set_psw(c=0) # **** this needs to be handled
        return result

    def DIV(self, register, source):
        """07 1R SS DIV 4-32

        (R, R+1) < (R, R+1) / (src)"""
        # The 32-bit two's complement integer in R andRvl is divided by the source operand.
        # The quotient is left in R; the remain- der in Rvl.
        # Division will be performed so that the remainder is of the same sign as the dividend.
        # R must be even.
        # get_n: set if quotient <0; cleared otherwise
        # get_z: set if quotient =0; cleared otherwise
        # get_v: set if source =0 or if the absolute value of the register is larger than the absolute value of the source. (In this case the instruction is aborted because the quotient would exceed 15 bits.)
        # get_c: set if divide 0 attempted; cleared otherwise
        if source == 0:
            v = 0
            c = 0
            self.psw.set_psw(v=v, c=c)
            return 0

        R = self.reg.registers[register]
        Rv1 = self.reg.registers[register + 1]

        numerator = (R << 16) + Rv1
        quotient = numerator // source
        remainder = numerator % source
        self.reg.registers[register] = quotient
        self.reg.registers[register + 1] = remainder
        self.psw.set_n('', quotient)
        self.psw.set_z('', quotient)
        self.psw.set_psw(v=0, c=0)
        return quotient

    def ASH(self, register, source):
        """07 2R SS ASH arithmetic shift 4-33

        R < R >> NN """
        # The contents of the register are shifted right or left
        # the number of times specified by the shift count.
        # The shift count is taken as the low order 6 bits of the source operand.
        # This number ranges from -32 to + 31.
        # Negative is a a right shift and positive is a left shift.
        #
        # get_n: set if result <0; cleared otherwise
        # get_z: set if result ..0; cleared otherwise
        # get_v: set if sign of register changed during shift; cleared other- wise
        # get_c: loaded from last bit shifted out of register
        register_sign = register & 0o100000
        shifts = source & 0o037
        shift_sign = source & 0o040
        if shift_sign == 0:
            result = self.reg.registers[register] << shifts
        else:
            result = self.reg.registers[register] >> (shifts + 1)
        self.psw.set_n('', result)
        self.psw.set_z('', result)
        result_sign = result & 0o100000
        if result_sign != register_sign:
            v = 1
        else:
            v = 0
        # *** need to calculate Carry status
        self.psw.set_psw(v=v, c=0)
        return result

    def ASHC(self, register, source):
        """07 3R SS ASHC arithmetic shift combined 4-34

        (R, R+1) < (R, R+1) >> get_n"""
        # The contents of the register and the register ORed with
        # one are treated as one 32 bit word, R + 1 (bits 0-15)
        # and R (bits 16-31) are shifted right or left the number
        # of times specified by the shift count The shift count
        # is taken as the low order 6 bits of the source operand.
        # This number ranges from -32 to +31. Negative is a right
        # shift and positive is a left shift When the register
        # chosen is an odd number the register and the register
        # OR'ed with one are the same. In this case the right shift
        # becomes a rotate (for up to a shift of 16). The 16 bit
        # word is rotated right the number of bits specified by
        # the shift count

        # get_n: set if result <0; cleared otherwise
        # get_z: set if result =0; cleared otherwise
        # get_v: set if sign bit changes during the shift; cleared otherwise
        # get_c: loaded with high order bit when left Shift;
        #    loaded with low order bit when right shift
        #    (loaded with the last bit shifted out of the 32-bit operand)

        result = self.reg.registers[register] >> source
        self.psw.set_n('', result)
        self.psw.set_z('', result)
        return result

    def XOR(self, register, source):
        """07 4R DD XOR 4-35

        (dst) < R ^ (dst)"""
        # The exclusive OR of the register and destination operand
        # is stored in the destination address. Contents of register
        # are unaffected. Assembler format is: XOR R.D
        # get_n: set if the result <0: cleared otherwise
        # get_z set if result = 0: cleared otherwise
        # get_v: cleared
        # get_c: unaffected
        result = self.reg.registers[register] ^ source
        self.psw.set_n('', result)
        self.psw.set_z('', result)
        return result

    def SOB(self, register, source):
        """07 7R NN SOB sutract one and branch 4-63

        R < R -1, then maybe branch"""
        print('SOB unimplemented')
        result = self.reg.registers[register] * source
        return result

    def is_double_operand_RSS(self, instruction):
        """Using instruction bit pattern, determine whether it's an RSS RDD RNN instruction"""
        # 077R00 0 111 111 *** 000 000 SOB (jump & subroutine)
        # bit 15 = 0
        # bits 14-12 = 7
        # bits 9 10 11 in [0,1,2,3,4,7]
        bit15 = instruction & 0o100000 == 0o000000
        bits14_12 = instruction & 0o070000 == 0o070000
        bits11_9 = instruction & 0o077000 in [0o070000, 0o071000, 0o072000, 0o073000, 0o074000, 0o077000]
        return bit15 and bits14_12 and bits11_9

    def do_double_operand_RSS(self, instruction):
        """dispatch an RSS opcode"""
        # parameter: opcode of form 0 111 *** *** *** ***
        # register source or destination
        # 15-9 opcode
        # 8-6 reg
        # 5-0 src or dst
        opcode = instruction & 0o077000
        register = (instruction & 0o000700) >> 6
        source = instruction & 0o000077

        run = True
        print(f'    {self.double_operand_RSS_instruction_names[opcode]} {oct(instruction)} double_operand_RSS '
              f'r{register}={oct(self.reg.registers[register])} {oct(source)}')
        result = self.double_operand_RSS_instructions[opcode](register, source)
        #print(f'    result:{oct(result)}')
        self.reg.registers[register] = result
        return run

    # ****************************************************
    # Double-Operand SSDD instructions
    # 01 SS DD through 06 SS DD
    # 11 SS DD through 16 SS DD
    # ****************************************************

    def MOV(self, BW, source, dest):
        """01 SS DD move 4-23

        (dst) < (src)"""
        result = source
        #print(f'    MOV source:{oct(source)} dest:{oct(dest)} result:{oct(result)}')
        self.psw.set_n(BW, source)
        self.psw.set_z(BW, source)
        self.psw.set_psw(v=0)
        return result #, "**0-"

    def CMP(self, BW, source, dest):
        """compare 4-24
        (src)-(dst)"""
        # subtract dest from source
        # set the condition code based on that result
        # but don't change the destination
        result = source - dest
        #print(f'    CMP source:{source} dest:{dest} result:{result}')
        self.psw.set_n(BW, result)
        self.psw.set_z(BW, result)
        self.psw.set_v(BW, result)
        return dest #, "***-"

    def BIT(self, BW, source, dest):
        """bit test 4-28

        (src) ^ (dst)"""
        #
        # Performs logical "and" comparison of the source and destination
        # and modifies condition codes accordingly.
        # Neither the source nor destination operands are affected.
        result = source & dest
        #print(f'    BIT source:{source} dest:{dest} result:{result}')
        self.psw.set_n(BW, result)
        self.psw.set_z(BW, result)
        self.psw.set_psw(v=0)
        return result #, "**0-"

    def BIC(self, BW, source, dest):
        """bit clear 4-29

        (dst) < ~(src)&(dst)"""
        result = ~source & dest
        self.psw.set_n(BW, result)
        self.psw.set_z(BW, result)
        self.psw.set_psw(v=0)
        return result #, "**0-"

    def BIS(self, BW, source, dest):
        """bit set 4-30
        (dst) < (src) get_v (dst)"""
        result = source | dest
        #print(f'    BIS {oct(source)} {oct(dest)} -> {oct(result)}')
        self.psw.set_n(BW, result)
        self.psw.set_z(BW, result)
        self.psw.set_psw(v=0)
        return result #, "**0-"

    def ADDSUB(self, BW, source, dest):
        """06 SS DD: ADD 4-25 (dst) < (src) + (dst)
        | 16 SS DD: SUB 4-26 (dst) < (dst) + ~(src) + 1
        The ADD and SUB instructions use word addressing,
        and have no byte-oriented variations.
        """
        # SUB is the "byte" version of ADD
        if BW == 'W':
            result = source + dest
        else:
            result = abs(source + ~dest + 1)
        self.psw.set_n(BW, result)
        self.psw.set_z(BW, result)
        self.psw.set_v(BW, result)
        # need to detect overflow, truncate result
        return result #, "****"

    def is_double_operand_SSDD(self, instruction):
        """Using instruction bit pattern, determine whether it's a souble operand instruction"""
        # bits 14 - 12 in [1, 2, 3, 4, 5, 6]
        #print (f'is_double_operand_SSDD {oct(instruction)}&0o070000={instruction & 0o070000}')
        bits14_12 = instruction & 0o070000 in [0o010000, 0o020000, 0o030000, 0o040000, 0o050000, 0o060000]
        return bits14_12

    def do_double_operand_SSDD(self, instruction):
        """dispatch a double-operand opcode.
        parameter: opcode of form * +++ *** *** *** ***
        where +++ = not 000 and not 111 and not 110 """
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

        self.sw.start("double operand")
        self.reg.PC_increment = 0
        if (instruction & 0o100000) >> 15 == 1:
            bw = 'B'
        else:
            bw = 'W'
        opcode = instruction & 0o070000
        name_opcode = instruction & 0o170000
        print(f'    {self.double_operand_SSDD_instruction_names[name_opcode]} {oct(instruction)} double_operand_SSDD ')

        source = (instruction & 0o007700) >> 6
        dest = instruction & 0o000077
        #print(f'    source_value  = addressing_mode_get')
        source_value, source_register, source_address = self.am.addressing_mode_get(bw, source)
        #print(f'    dest_value = addressing_mode_get')
        dest_value, dest_register, dest_address = self.am.addressing_mode_get(bw, dest)
        #print(f'    S:{oct(source_value)} R:{oct(source_register)} @:{oct(source_address)}  D:{oct(dest_value)} R:{oct(dest_register)} @:{oct(dest_address)}')

        run = True
        #print(f'    result = double_operand_SSDD_instructions')
        result = self.double_operand_SSDD_instructions[opcode](bw, source_value, dest_value)
        #print(f'    result:{oct(result)}   get_nvzc_string:{self.psw.get_nvzc_string()}  PC:{oct(self.reg.get_pc())}')
        #print(f'    addressing_mode_set')
        self.am.addressing_mode_set(bw, result, dest_register, dest_address)
        self.sw.stop("double operand")

        return run
