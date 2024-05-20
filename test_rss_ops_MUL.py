import logging
import pytest

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
# p * p = 32,761 which fits in a 16-bit word (32,768)
# p * P = 90,500 which fits in a 32-bit long word
# P * P = 250,000 which fits in a 32-bit long word
# *** need some longword overflow cases

# 'name, s, d, RS, RD, nzvc
multiplication_testcases = [
    ("pp", p, p, 2, 4, '0000'),
    ("pz", p, z, 2, 4, '0100'),
    ("pn", p, n, 2, 4, '1000'),
    ("zp", z, p, 2, 4, '0100'),
    ("zz", z, z, 2, 4, '0100'),
    ("zn", z, n, 2, 4, '0100'),
    ("np", n, p, 2, 4, '1000'),
    ("nz", n, z, 2, 4, '0100'),
    ("nn", n, n, 2, 4, '0000'),

    ("pP", p, P, 2, 4, '0000'),
    ("pN", p, N, 2, 4, '1000'),
    ("zP", z, P, 2, 4, '0100'),
    ("zN", z, N, 2, 4, '0100'),
    ("nP", n, P, 2, 4, '1000'),
    ("nN", n, N, 2, 4, '0000'),
    ("Pp", P, p, 2, 4, '0000'),
    ("Pz", P, z, 2, 4, '0100'),
    ("Pn", P, n, 2, 4, '1000'),
    ("Np", N, p, 2, 4, '1000'),
    ("Nz", N, z, 2, 4, '0100'),
    ("Nn", N, n, 2, 4, '0000'),

    ("PP", P, P, 2, 4, '0000'),
    ("PN", P, N, 2, 4, '1000'),
    ("NP", N, P, 2, 4, '1000'),
    ("NN", N, N, 2, 4, '0000'),
]

# There are limits on what sorts of numbers can be divided without blowing things up
smlPos = 0o44276
bigPos = 0o0042400042
smlNeg = u.twosComplementNegative(smlPos)
bigNeg = u.twosComplementNegativeLong(bigPos)

# name, numerator, denonminator, RS, RD, nzvc
# numerators are 32-bit pdp11 integers
division_testcases = [
    ("Pp", bigPos, smlPos, 2, 4, '0000'),
    ("Pn", bigPos, smlNeg, 2, 4, '1000'),
    ("Np", bigNeg, smlPos, 2, 4, '0000'),
    ("Np", bigNeg, smlNeg, 2, 4, '1000'),
]


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

    @pytest.mark.parametrize('name, s, d, RS, RD, CC', multiplication_testcases)
    def test_MUL(self, name, s, d, RS, RD, CC):
        #print(f'\ntest_MUL case name: {name}')
        #print(f'test_MUL assembly: MUL R{RS},R{RD} ; {oct(d)} * {oct(s)} = {u.pythonifyPDP11Word(d)} * {u.pythonifyPDP11Word(s)}')
        instruction = 0o070000
        self.psw.set_psw(psw=0)
        self.reg.set(RD, d)
        self.reg.set(RS, s)
        instruction = self.make_rss_op(instruction, regD=RD, modeS=0, regS=RS)
        #print(f'test_MUL instruction: {oct(instruction)}')  # 070RSS
        assert self.rss_ops.is_rss_op(instruction)
        self.rss_ops.do_rss_op(instruction)

        expected_product = u.PDP11LongifyPythonInteger(u.pythonifyPDP11Word(s) * u.pythonifyPDP11Word(d))
        #print(f'test_MUL expected_product:{expected_product}')

        high_word = self.reg.get(RD)
        low_word = self.reg.get(RD+1)
        #print(f'test_MUL high_word:{oct(high_word)} low_word:{oct(low_word)}')
        pdp11_actual_product = (high_word << 16) | low_word
        #print(f'test_MUL pdp11_actual_product:{pdp11_actual_product} = {oct(pdp11_actual_product)}')
        assert pdp11_actual_product == expected_product

        #print(f'test_MUL expected nzvc: {CC}');
        condition_codes = self.psw.get_nzvc()
        #print(f'test_MUL   actual nzvc: {condition_codes}');
        assert condition_codes == CC

    @pytest.mark.parametrize('name, numerator, denominator, RS, RD, CC', division_testcases)
    def test_DIV(self, name, numerator, denominator, RS, RD, CC):
        #DIV: (R, R+1) < (R, R+1) / (src)
        # The 32-bit two's complement integer in R and Rvl is divided by the source operand.
        # The quotient is left in R; the remainder in Rvl.
        # Division will be performed so that the remainder is of the same sign as the dividend.
        # R must be even.
        #
        # We reuse parameters and results from MUL
        pnumerator = u.pythonifyPDP11Long(numerator)
        pdenominator = u.pythonifyPDP11Word(denominator)
        print(f'\ntest_DIV assembly: DIV R{RS},R{RD} ; {oct(numerator)} / {oct(denominator)} = {pnumerator} / {pdenominator}')
        if denominator == 0:
            expected_quotient = 0
            expected_remainder = 0
        else:
            expected_quotient = pnumerator // pdenominator # *** this is complicateder than that because of rounding
            expected_remainder = pnumerator % pdenominator
        print(f'test_DIV expected_quotient:{oct(expected_quotient)} = {u.pythonifyPDP11Word(expected_quotient)}')
        print(f'test_DIV expected_remainder:{oct(expected_remainder)} = {u.pythonifyPDP11Word(expected_remainder)}')

        Rvl = RD + 1
        self.reg.set(RD, numerator >> 16)            # high-order word
        self.reg.set(Rvl, numerator & MASK_WORD)    # low-order word
        self.reg.set(RS, denominator)

        instruction = 0o071000
        self.psw.set_psw(psw=0)
        instruction = self.make_rss_op(instruction, regD=RD, modeS=0, regS=RS)
        print(f'test_DIV instruction: {oct(instruction)}')  # 070RSS
        assert self.rss_ops.is_rss_op(instruction)

        self.rss_ops.do_rss_op(instruction)

        actual_quotient = self.reg.get(RD)
        actual_remainder = self.reg.get(Rvl)
        print(f'test_DIV actual_quotient:{oct(actual_quotient)} = {u.pythonifyPDP11Word(actual_quotient)}')
        print(f'test_DIV actual_remainder:{oct(actual_remainder)} = {u.pythonifyPDP11Word(actual_remainder)}')

        assert actual_quotient == expected_quotient
        assert actual_remainder == expected_remainder

        condition_codes = self.psw.get_nzvc()
        assert condition_codes == CC

