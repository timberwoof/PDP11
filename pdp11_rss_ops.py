"""pdp11_rss_ops.py double operand instructions"""
import logging
import pdp11_util as u
MASK_WORD = 0o177777
MASK_WORD_MSB = 0o100000
MASK_BYTE_MSB = 0o000200
MASK_LOW_BYTE = 0o000377
MASK_HIGH_BYTE = 0o177400

class rss_ops:
    """Implements PDP11 double-operand RSS instructions"""
    def __init__(self, reg, ram, psw, am, sw):
        logging.info('initializing doubleOperandOps')
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

    def MUL(self, rDest, source):
        """07 0R SS MUL 4-31

        (R, R+1) < (R, R+1) * (src)"""
        # get_c: set if the result < -2^15 or result >= 2^15-1
        # logging.info(f'    MUL {register} * {source}')
        # The contents of the destination register and source taken as two's complement integers
        # are multiplied and stored in the destination register and the succeeding register (if R is even).
        # If R is odd only the low order product is stored. Assembler syntax is : MUL S,R.
        # If R is Even
        #   Store high-order result in R
        #   Store low-order result in R+1
        # Else
        #   Store result in R
        dest = self.reg.get(rDest)

        py_source = u.pythonifyPDP11Word(source)
        py_dest = u.pythonifyPDP11Word(dest)
        #print (f'MUL(r:{oct(dest)}, SS:{oct(source)}) = (r:{py_dest}, SS:{py_source})')
        result = u.pythonifyPDP11Word(py_source) * u.pythonifyPDP11Word(py_dest)
        #print (f'MUL result: {oct(result)} = {result}')

        n = 0
        if result < 0:
            #print(f'MUL {result} < 0; setting n bit in PSW')
            n = 1
        self.psw.set_psw(n=n)
        self.psw.set_z('', result)
        self.psw.set_psw(v=0)
        self.psw.set_psw(c=0)  # **** this needs to be handled

        # if rDest is even, store the high value in the +1 register
        if rDest % 2 == 0:
            pdp11result = u.PDP11LongifyPythonInteger(result)
            high_result = pdp11result >> 16
            low_result = pdp11result & MASK_WORD
            #print(f'MUL high register:{oct(rDest)} low register:{oct(rDest+1)}')
            #print(f'MUL high_result:{oct(high_result)} low_result:{oct(low_result)}')
            self.reg.set(rDest + 1, low_result)
            return high_result, '' # this is where we set the other regsiter
        else:
            return u.PDP11WordifyPythonInteger(result), ''

    def DIV(self, rDest, denominator):
        """07 1R SS DIV 4-32

        (R, R+1) < (R, R+1) / (src)"""
        # The 32-bit two's complement integer in R and Rvl is divided by the source operand.
        # The pyquotient is left in R; the pyremainder in Rvl.
        # Division will be performed so that the pyremainder is of the same sign as the dividend.
        # R must be even.
        # get_n: set if pyquotient <0; cleared otherwise
        # get_z: set if pyquotient =0; cleared otherwise
        # get_v: set if source =0 or if the absolute value of the register is larger than the absolute value of the source. (In this case the instruction is aborted because the pyquotient would exceed 15 bits.)
        # get_c: set if divide 0 attempted; cleared otherwise
        if rDest % 2 == 1:
            # check for even R1
            #print('DIV R was not even')
            return 0, 'DIV R was not even'

        R = self.reg.get(rDest)         # high-order word
        Rvl = self.reg.get(rDest + 1)   # low-order word
        # this is why we have to pass in the R number and not the contents
        #print(f'DIV R:{oct(R)} Rvl:{oct(Rvl)} src:{oct(denominator)}' )
        pynumerator = u.pythonifyPDP11Long((R << 16) | Rvl)
        pydenominator = u.pythonifyPDP11Word(denominator)
        #print(f'DIV pynumerator:{oct(pynumerator)} = {pynumerator}  pydenominator:{oct(pydenominator)} = {pydenominator}')

        if pynumerator == 0:
            # *** divide by zero needs to trap
            v = 0
            c = 0
            self.psw.set_psw(v=v, c=c)
            #print('DIV divide by zero')
            return 0, 'DIV Divide by Zero'

        pyquotient = pynumerator // pydenominator
        pyremainder = pynumerator % pydenominator

        # Fix for error in the way Python does remainder
        if pynumerator < 0 or pydenominator < 0:
            pyquotient = pyquotient + 1
            pyremainder = pynumerator - (pydenominator * pyquotient)
        #print(f'DIV pyquotient:{pyquotient} pyremainder:{pyremainder}')

        pdp11quotient = u.PDP11WordifyPythonInteger(pyquotient)

        self.reg.set(rDest, pdp11quotient)
        self.reg.set(rDest + 1, u.PDP11WordifyPythonInteger(pyremainder))
        self.psw.set_n('', pdp11quotient)
        self.psw.set_z('', pdp11quotient)
        self.psw.set_psw(v=0, c=0)
        return pdp11quotient, ''

    def ASH(self, rDest, source):
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
        R = self.reg.get(rDest)
        register_sign = rDest & 0o100000
        shifts = source & 0o037
        shift_sign = source & 0o040
        if shift_sign == 0:
            result = self.reg.get(rDest) << shifts
        else:
            result = self.reg.get(rDest) >> (shifts + 1)
        self.psw.set_n('', result)
        self.psw.set_z('', result)
        result_sign = result & 0o100000
        if result_sign != register_sign:
            v = 1
        else:
            v = 0
        # *** need to calculate Carry status
        self.psw.set_psw(v=v, c=0)
        return result, ''

    def ASHC(self, rDest, source):
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

        result = self.reg.get(rDest) >> source
        self.psw.set_n('', result)
        self.psw.set_z('', result)
        return result, ''

    def XOR(self, rDest, source):
        """07 4R DD XOR 4-35

        (dst) < R ^ (dst)"""
        # The exclusive OR of the register and destination operand
        # is stored in the destination address. Contents of register
        # are unaffected. Assembler format is: XOR R.D
        # get_n: set if the result <0: cleared otherwise
        # get_z set if result = 0: cleared otherwise
        # get_v: cleared
        # get_c: unaffected
        result = self.reg.get(rDest) ^ source
        self.psw.set_n('', result)
        self.psw.set_z('', result)
        return result, ''

    def SOB(self, rDest, source):
        """07 7R NN SOB sutract one and branch 4-63

        R < R -1, then maybe branch"""
        result = self.reg.get(rDest) * source
        return result, 'SOB unimplemented'

    def is_rss_op(self, instruction):
        """Using instruction bit pattern, determine whether it's an RSS RDD RNN instruction"""
        # 077R00 0 111 111 *** 000 000 SOB (jump & subroutine)
        # bit 15 = 0
        # bits 14-12 = 7
        # bits 9 10 11 in [0,1,2,3,4,7]
        bit15 = instruction & 0o100000 == 0o000000
        bits14_12 = instruction & 0o070000 == 0o070000
        bits11_9 = instruction & 0o077000 in [0o070000, 0o071000, 0o072000, 0o073000, 0o074000, 0o077000]
        return bit15 and bits14_12 and bits11_9

    def do_rss_op(self, instruction):
        """dispatch an RSS opcode"""
        # parameter: opcode of form 0 111 *** *** *** ***
        # register source
        # 15-9 opcode
        # 8-6 reg
        # 5-0 src
        self.sw.start("rss")
        opcode = instruction & 0o077000
        register = (instruction & 0o000700) >> 6
        source = instruction & 0o000077

        run = True
        assembly = f'{self.double_operand_RSS_instruction_names[opcode]}'
        destination_value, destination_register, destination_address, operand1, assembly1, destination_addressmode = self.am.addressing_mode_get(
            'B', source)
        result, report = self.double_operand_RSS_instructions[opcode](register, destination_value)
        logging.info(f'    result:{oct(result)}')
        self.reg.set(register, result)
        self.sw.stop("rss")
        return run, "", "", assembly, report
