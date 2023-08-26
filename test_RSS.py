import pytest
from pdp11Hardware import registers as reg
from pdp11Hardware import ram
from pdp11Hardware import psw
from pdp11Hardware import stack
from pdp11Hardware import addressModes as am
from pdp11DoubleOperandOps import doubleOperandOps as dopr

mask_word = 0o177777
mask_word_msb = 0o100000
mask_byte_msb = 0o000200
mask_low_byte = 0o000377
mask_high_byte = 0o177400

class TestClass():
    reg = reg()
    ram = ram()
    psw = psw(ram)
    stack = stack(reg, ram, psw)
    am = am(reg, ram, psw)
    dopr = dopr(reg, ram, psw, am)


    def test_MUL(self):
        print('test_MUL')
        R = 1
        a = 0o001212
        b = 0o24

        self.psw.set_PSW(PSW=0)
        self.reg.set(R, a)
        instruction = 0o070000 | R << 6 | b
        print(oct(instruction)) # 0o0171312
        assert self.dopr.is_double_operand_RSS(instruction)
        self.dopr.do_double_operand_RSS(instruction)

        product = self.reg.get(R)
        print(f'product:{product}')
        assert product == a * b

        condition_codes = self.psw.NZVC()
        assert condition_codes == "0000"

    def test_DIV(self):
        R = 2 # must be even
        a = 0o1536230
        b = 0o75 # max 0o77
        Rv1 = R + 1

        print(f'test_DIV {oct(a)} / {oct(b)} R:{R} Rv1:{Rv1} ')

        self.psw.set_PSW(PSW=0)

        # set up R and Rv1
        self.reg.set(R, a >> 16)
        self.reg.set(Rv1, a & mask_word)

        instruction = 0o071000 | R << 6 | b
        print(f'test_DIV instruction:{oct(instruction)}') # 0o0171312
        assert self.dopr.is_double_operand_RSS(instruction)
        self.dopr.do_double_operand_RSS(instruction)

        quotient = self.reg.get(R)
        remainder = self.reg.get(Rv1)
        print(f'quotient:{oct(quotient)}')
        print(f'remainder:{oct(remainder)}')
        assert quotient == a // b
        assert remainder == a % b

        condition_codes = self.psw.NZVC()
        assert condition_codes == "0000"

