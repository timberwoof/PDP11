import logging
import pdp11_util as u
from pdp11_hardware import Registers as reg
from pdp11_hardware import Ram
from pdp11_hardware import PSW
from pdp11_hardware import Stack
from pdp11_hardware import AddressModes as am

from pdp11_br_ops import br_ops
from pdp11_cc_ops import cc_ops
from pdp11_noopr_ops import noopr_ops
from pdp11_other_ops import other_ops
from pdp11_rss_ops import rss_ops
from pdp11_ss_ops import ss_ops
from pdp11_ssdd_ops import ssdd_ops

from stopwatches import StopWatches as sw

MASK_WORD = 0o177777
MASK_WORD_MSB = 0o100000
MASK_BYTE_MSB = 0o000200
MASK_LOW_BYTE = 0o000377
MASK_HIGH_BYTE = 0o177400

P = 0o764 # 500
p = 0o265 # 181
z = 0 # 0o0
n = u.twosComplementNegative(p)
N = u.twosComplementNegative(P)

class TestClass():
    reg = reg()
    ram = Ram(reg)
    psw = PSW(ram)
    stack = Stack(reg, ram, psw)
    am = am(reg, ram, psw)
    sw = sw()

    br_ops = br_ops(reg, ram, psw, sw)
    cc_ops = cc_ops(psw, sw)
    noopr_ops = noopr_ops(reg, ram, psw, stack, sw)
    other_ops = other_ops(reg, ram, psw, am, sw)
    rss_ops = rss_ops(reg, ram, psw, am, sw)
    ss_ops = ss_ops(reg, ram, psw, am, sw)
    ssdd_ops = ssdd_ops(reg, ram, psw, am, sw)

    def SS_part(self, mode, register):
        return (mode << 3 | register) << 6

    def DD_part(self, mode, register):
        return (mode << 3 | register)

    def make_ssdd_op(self, opcode, modeS=0, regS=0, modeD=0, regD=1):
        return opcode | self.SS_part(modeS, regS) | self.DD_part(modeD, regD)

    def make_rss_op(self, opcode, regD=0, modeS=0, regS=0):
        # documentation calls second parameter SS which here uses DD_part to make
        return opcode | regD << 6 | self.DD_part(modeS, regS)

    def test_BIC(self):
        print('\ntest_BIC')
        self.psw.set_psw(psw=0)
        self.reg.set(1, 0b1010101010101010)
        self.reg.set(2, 0b1111111111111111)

        instruction = self.make_ssdd_op(opcode=0o040000, modeS=0, regS=1, modeD=0, regD=2)   # mode 0 R1
        assert self.ssdd_ops.is_ssdd_op(instruction)
        run, operand1, operand2, assembly, report = self.ssdd_ops.do_ssdd_op(instruction)
        assert assembly == 'BIC R1,R2'

        r2 = self.reg.get(2)
        assert r2 == 0b0101010101010101

        condition_codes = self.psw.get_nzvc()
        assert condition_codes == "0000"

    def test_BICB(self):
        print('\ntest_BICB')
        self.psw.set_psw(psw=0)
        # evil test shows that The high byte is unaffected.
        self.reg.set(1, 0b1010101010101010)
        self.reg.set(2, 0b1111111111111111)


        instruction = self.make_ssdd_op(opcode=0o140000, modeS=0, regS=1, modeD=0, regD=2)   # mode 0 R1
        assert self.ssdd_ops.is_ssdd_op(instruction)
        run, operand1, operand2, assembly, report = self.ssdd_ops.do_ssdd_op(instruction)
        assert assembly == 'BICB R1,R2'

        r2 = self.reg.get(2)
        assert r2 == 0b1111111101010101

        condition_codes = self.psw.get_nzvc()
        assert condition_codes == "0000"

    def test_BIC_2(self):
        print('\ntest_BIC_2')
        # PDP-11/40 p. 4-21
        self.psw.set_psw(psw=0o777777)
        # evil test puts word data into a byte test and expects byte result
        self.reg.set(3, 0o001234)
        self.reg.set(4, 0o001111)

        instruction = self.make_ssdd_op(opcode=0o040000, modeS=0, regS=3, modeD=0, regD=4)
        assert self.ssdd_ops.is_ssdd_op(instruction)
        run, operand1, operand2, assembly, report = self.ssdd_ops.do_ssdd_op(instruction)
        assert assembly == "BIC R3,R4"

        assert self.reg.get(3) == 0o001234
        assert self.reg.get(4) == 0o000101

        condition_codes = self.psw.get_nzvc()
        assert condition_codes == "0001"

    def test_BICB_2(self):
        print('\ntest_BICB_2')
        # PDP-11/40 p. 4-21
        self.psw.set_psw(psw=0)
        # evil test puts word data into a byte test and expects byte result
        self.reg.set(3, 0o001234)
        self.reg.set(4, 0o001111)

        instruction = self.make_ssdd_op(opcode=0o140000, modeS=0, regS=3, modeD=0, regD=4)
        assert self.ssdd_ops.is_ssdd_op(instruction)
        run, operand1, operand2, assembly, report = self.ssdd_ops.do_ssdd_op(instruction)
        assert assembly == "BICB R3,R4"

        assert self.reg.get(3) == 0o001234
        assert self.reg.get(4) == 0o001101

        condition_codes = self.psw.get_nzvc()
        assert condition_codes == "0000"

    def test_MOV_0(self):
        print('\ntest_MOV_0')
        self.psw.set_psw(psw=0o777777)
        self.reg.set(3,0o123456)
        self.reg.set(4,0o000000)
        instruction = self.make_ssdd_op(opcode=0o010000, modeS=0, regS=3, modeD=0, regD=4)   # mode 0 R1
        assert self.ssdd_ops.is_ssdd_op(instruction)
        run, operand1, operand2, assembly, report = self.ssdd_ops.do_ssdd_op(instruction)
        assert assembly == "MOV R3,R4"

        r3 = self.reg.get(3)
        assert r3 == 0o123456

        r4 = self.reg.get(4)
        assert r4 == 0o123456

        condition_codes = self.psw.get_nzvc()
        assert condition_codes == "1001"

    def test_MOV_2(self):
        print('\ntest_MOV_2')
        # 010322 MOV R3,(R2)+
        # from M9001_YA that broke
        self.psw.set_psw(psw=0o777777)
        self.reg.set(3,0o177777)
        self.reg.set(2,0o000000)
        instruction = self.make_ssdd_op(opcode=0o010000, modeS=0, regS=3, modeD=2, regD=2)   # mode 0 R1
        assert self.ssdd_ops.is_ssdd_op(instruction)
        print('setup done; running make_ssdd_op')
        run, operand1, operand2, assembly, report = self.ssdd_ops.do_ssdd_op(instruction)
        assert assembly == "MOV R3,(R2)+"
        print('make_ssdd_op done; checking results')

        r3 = self.reg.get(3)
        assert r3 == 0o177777

        r2 = self.reg.get(2)
        assert r2 == 0o02

        target = self.ram.read_word(0o000000)
        assert target == r3

        condition_codes = self.psw.get_nzvc()
        assert condition_codes == "1001"

    def test_MOVB_01(self):
        print('\ntest_MOVB_01')
        self.psw.set_psw(psw=0o777777)
        self.reg.set(3,0b1010011100101110)
        self.reg.set(4,0b0000000000000000)
        instruction = self.make_ssdd_op(opcode=0o110000, modeS=0, regS=3, modeD=0, regD=4)   # mode 0 R1
        assert self.ssdd_ops.is_ssdd_op(instruction)
        run, operand1, operand2, assembly, report = self.ssdd_ops.do_ssdd_op(instruction)
        assert assembly == "MOVB R3,R4"

        r3 = self.reg.get(3)
        assert r3 == 0b1010011100101110

        r4 = self.reg.get(4)
        assert r4 == 0b0000000000101110

        condition_codes = self.psw.get_nzvc()
        assert condition_codes == "0001"

    def test_MOVB_02(self):
        print('\ntest_MOVB_02')
        self.psw.set_psw(psw=0o777777)
        self.reg.set(3,0b1010011110101110)
        self.reg.set(4,0b0000000000000000)
        instruction = self.make_ssdd_op(opcode=0o110000, modeS=0, regS=3, modeD=0, regD=4)   # mode 0 R1
        assert self.ssdd_ops.is_ssdd_op(instruction)
        run, operand1, operand2, assembly, report = self.ssdd_ops.do_ssdd_op(instruction)
        assert assembly == "MOVB R3,R4"

        r3 = self.reg.get(3)
        assert r3 == 0b1010011110101110

        r4 = self.reg.get(4)
        assert r4 == 0b0000000010101110

        condition_codes = self.psw.get_nzvc()
        assert condition_codes == "1001"

    def test_MOVB_03(self):
        print('\ntest_MOVB_03')
        self.psw.set_psw(psw=0o777777)
        self.reg.set(3,0b0000000010101110)
        self.reg.set(4,0b1010011100000000)
        instruction = self.make_ssdd_op(opcode=0o110000, modeS=0, regS=3, modeD=0, regD=4)   # mode 0 R1
        assert self.ssdd_ops.is_ssdd_op(instruction)
        run, operand1, operand2, assembly, report = self.ssdd_ops.do_ssdd_op(instruction)
        assert assembly == "MOVB R3,R4"

        r3 = self.reg.get(3)
        assert r3 == 0b0000000010101110

        r4 = self.reg.get(4)
        assert r4 == 0b1010011110101110

        condition_codes = self.psw.get_nzvc()
        assert condition_codes == "1001"

    def test_MOVB_04(self):
        print('\ntest_MOVB_04')
        # 165250 112512 MOVB (R5)+,@R2 from M9301-YA
        # MOVB (R5)+,@R2
        self.psw.set_psw(psw=0o777777)
        self.reg.set(2,0o000500)
        self.ram.write_word(0o000500, 0)
        assert self.ram.read_word(0o000500) == 0

        self.reg.set(5,0o165320)
        self.ram.write_word(0o165320, 0o177777)
        assert self.ram.read_word(self.reg.get(5)) == 0o177777

        instruction = 0o112512
        self.reg.set_pc(0o165250)
        assert self.ssdd_ops.is_ssdd_op(instruction)
        run, operand1, operand2, assembly, report = self.ssdd_ops.do_ssdd_op(instruction)
        assert assembly == "MOVB (R5)+,@R2"
        assert self.reg.get(5) == 0o165321
        atr2  = self.ram.read_byte(self.reg.get(2))
        print(f'@R2={oct(atr2)} {bin(atr2)}')
        assert atr2 == 0o377

    def test_MUL_pp(self):
        a = p
        b = p
        RD = 1
        RS = 2

        print(f'\ntest_MUL_pp {a} * {b} = {oct(a)} * {oct(b)}')

        instruction = 0o070000
        self.psw.set_psw(psw=0)
        self.reg.set(RD, a)
        self.reg.set(RS, b)
        instruction = self.make_rss_op(instruction, regD=RD, modeS=0, regS=RS)
        print(oct(instruction))  # 070RSS
        assert self.rss_ops.is_rss_op(instruction)
        self.rss_ops.do_rss_op(instruction)

        product = self.reg.get(RD)
        print(f'product:{oct(product)}')
        assert product == a * b

        condition_codes = self.psw.get_nzvc()
        assert condition_codes == "0000"

    def test_MUL_pP(self):
        a = p
        b = P
        RD = 2
        RS = 4

        print(f'\ntest_MUL_pP {a} * {b} = {oct(a)} * {oct(b)}')

        instruction = 0o070000
        self.psw.set_psw(psw=0)
        self.reg.set(RD, a)
        self.reg.set(RS, b)
        instruction = self.make_rss_op(instruction, regD=RD, modeS=0, regS=RS)
        print(oct(instruction))  # 070RSS
        assert self.rss_ops.is_rss_op(instruction)
        self.rss_ops.do_rss_op(instruction)

        high_word = self.reg.get(RD)
        low_word = self.reg.get(RD+1)
        print(f'high_word:{oct(high_word)} low_word:{oct(low_word)}')
        product = (high_word << 16) | low_word
        print(f'product:{oct(product)}')
        assert product == a * P

        condition_codes = self.psw.get_nzvc()
        assert condition_codes == "0000"

    def test_MUL_np(self):
        RD = 1
        RS = 2
        a = n
        b = p

        print(f'\ntest_MUL_np {a} * {b} = {oct(a)} * {oct(b)}')

        instruction = 0o070000
        self.psw.set_psw(psw=0)
        self.reg.set(RD, a)
        self.reg.set(RS, b)
        instruction = self.make_rss_op(instruction, regD=RD, modeS=0, regS=RS)
        print(oct(instruction))  # 070RSS
        assert self.rss_ops.is_rss_op(instruction)
        self.rss_ops.do_rss_op(instruction)

        expected = u.pythonifyPDP11Word(a) * u.pythonifyPDP11Word(b)
        print(f'product expected:{oct(expected)}')

        actual = self.reg.get(RD)
        print(f'product actual:{oct(actual)}')
        assert actual == expected

        condition_codes = self.psw.get_nzvc()
        assert condition_codes == "1000"

    def test_MUL_pn(self):
        RD = 1
        RS = 2
        a = p
        b = n

        print(f'\ntest_MUL_pn {a} * {b} = {oct(a)} * {oct(b)}')

        instruction = 0o070000
        self.psw.set_psw(psw=0)
        self.reg.set(RD, a)
        self.reg.set(RS, b)
        instruction = self.make_rss_op(instruction, regD=RD, modeS=0, regS=RS)
        print(oct(instruction))  # 070RSS
        assert self.rss_ops.is_rss_op(instruction)
        self.rss_ops.do_rss_op(instruction)

        expected = u.pythonifyPDP11Word(a) * u.pythonifyPDP11Word(b)
        print(f'product expected:{oct(expected)}')

        actual = self.reg.get(RD)
        print(f'product actual:{oct(actual)}')
        assert actual == expected

        condition_codes = self.psw.get_nzvc()
        assert condition_codes == "1000"

    def test_MUL_nP(self):
        a = n
        b = P
        RD = 4
        RS = 0

        print(f'\ntest_MUL_nP {a} * {b} = {oct(a)} * {oct(b)}')

        instruction = 0o070000
        self.psw.set_psw(psw=0)
        self.reg.set(RD, a)
        self.reg.set(RS, b)
        instruction = self.make_rss_op(instruction, regD=RD, modeS=0, regS=RS)
        print(oct(instruction))  # 070RSS
        assert self.rss_ops.is_rss_op(instruction)
        self.rss_ops.do_rss_op(instruction)

        expected = u.pythonifyPDP11Word(a) * u.pythonifyPDP11Word(b)
        print(f'product expected:{oct(expected)}')

        # The contents of the destination register and source taken as two's complement integers
        # are multiplied and stored in the destination register and the succeeding register (if R is even).
        # If R is Even
        #   Store high-order result in R
        #   Store low-order result in R+1
        # Else
        #   Store result in R

        high_word = self.reg.get(RD)
        low_word = self.reg.get(RD+1)
        print(f'high_word:{oct(high_word)} low_word:{oct(low_word)}')
        high_word_shifted = high_word << 16
        print(f'high_word shifted:{oct(high_word_shifted)}')
        actual = high_word_shifted | low_word
        print(f'actual:{oct(actual)}')
        print(f'product actual:{oct(actual)}')
        assert actual == expected

        condition_codes = self.psw.get_nzvc()
        assert condition_codes == "1000"

    def test_MUL_nn(self):
        RD = 1
        RS = 2
        a = n
        b = n

        print(f'\ntest_MUL_nn {a} * {b} = {oct(a)} * {oct(b)}')

        instruction = 0o070000
        self.psw.set_psw(psw=0)
        self.reg.set(RD, a)
        self.reg.set(RS, b)
        instruction = self.make_rss_op(instruction, regD=RD, modeS=0, regS=RS)
        print(oct(instruction))  # 070RSS
        assert self.rss_ops.is_rss_op(instruction)
        self.rss_ops.do_rss_op(instruction)

        expected = u.pythonifyPDP11Word(a) * u.pythonifyPDP11Word(b)
        print(f'product expected:{oct(expected)}')

        actual = self.reg.get(RD)
        print(f'product actual:{oct(actual)}')
        assert actual == expected

        condition_codes = self.psw.get_nzvc()
        assert condition_codes == "0000"

    def test_MUL_nN(self):
        a = n
        b = P
        RD = 2
        RS = 4

        print(f'\ntest_MUL_nN {a} * {b} = {oct(a)} * {oct(b)}')

        instruction = 0o070000
        self.psw.set_psw(psw=0)
        self.reg.set(RD, a)
        self.reg.set(RS, b)
        instruction = self.make_rss_op(instruction, regD=RD, modeS=0, regS=RS)
        print(oct(instruction))  # 070RSS
        assert self.rss_ops.is_rss_op(instruction)
        self.rss_ops.do_rss_op(instruction)

        expected = u.pythonifyPDP11Word(a) * u.pythonifyPDP11Word(b)
        print(f'product expected:{oct(expected)}')

        high_word = self.reg.get(RD)
        low_word = self.reg.get(RD+1)
        print(f'high_word:{oct(high_word)} low_word:{oct(low_word)}')
        actual = (high_word << 16) | low_word
        print(f'actual:{oct(actual)}')
        print(f'product actual:{oct(actual)}')
        assert actual == expected

        condition_codes = self.psw.get_nzvc()
        assert condition_codes == "0000"

    def test_DIV(self):
        RD = 2
        RS = 4
        # N n z p P
        a = p * P
        b = p
        Rvl = RD + 1

        print(f'\ntest_DIV {a} / {b} = {oct(a)} / {oct(b)}')
        print(f'test_DIV R:{RD} Rvl:{Rvl} ')

        self.psw.set_psw(psw=0)

        # set up R and Rvl
        self.reg.set(RD, a >> 16)            # high-order word
        self.reg.set(Rvl, a & MASK_WORD)    # low-order word
        self.reg.set(RS, b)

        instruction = 0o071000
        instruction = self.make_rss_op(instruction, regD=RD, modeS=0, regS=RS)
        print(f'test_DIV instruction:{oct(instruction)}')  #
        assert self.rss_ops.is_rss_op(instruction)
        self.rss_ops.do_rss_op(instruction)

        quotient = self.reg.get(RD)
        remainder = self.reg.get(Rvl)
        print(f'test_DIV quotient:{oct(quotient)}')
        print(f'test_DIV remainder:{oct(remainder)}')
        expected_quotient = a // b
        expected_remainder = a % b
        print(f'test_DIV expected_quotient:{oct(expected_quotient)}')
        print(f'test_DIV expected_remainder:{oct(expected_remainder)}')
        assert quotient == expected_quotient
        assert remainder == expected_remainder

        condition_codes = self.psw.get_nzvc()
        assert condition_codes == "0000"

