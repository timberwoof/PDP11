import pytest
from pdp11Hardware import registers as reg
from pdp11Hardware import ram
from pdp11Hardware import psw
from pdp11Hardware import stack
from pdp11Hardware import addressModes as am
from pdp11SingleOperandOps import singleOperandOps as sopr

mask_word = 0o177777
mask_word_msb = 0o100000
mask_byte_msb = 0o000200
mask_low_byte = 0o000377
mask_high_byte = 0o177400

class TestClass():
    reg = reg()
    ram = ram(reg)
    psw = psw(ram)
    stack = stack(reg, ram, psw)
    am = am(reg, ram, psw)
    sopr = sopr(reg, ram, psw, am)

    def test_CLR(self):
        print('test_CLR')
        self.psw.set_PSW(PSW=0)
        self.reg.set(1, 0o013333)

        instruction = 0o05001  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        self.sopr.do_single_operand(instruction)

        r1 = self.reg.get(1)
        assert r1 == 0o0

        condition_codes = self.psw.NZVC()
        assert condition_codes == "0100"

    def test_COM(self):
        print('test_COM')
        self.psw.set_PSW(PSW=0)
        self.reg.set(1, 0o013333)

        instruction = 0o05101 # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        self.sopr.do_single_operand(instruction)

        r1 = self.reg.get(1)
        assert r1 == 0o164444

        condition_codes = self.psw.NZVC()
        assert condition_codes == "1001"

    def test_INC(self):
        print('test_CLR')
        self.psw.set_PSW(PSW=0)
        self.reg.set(1, 0o013333)

        instruction = 0o05201  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        self.sopr.do_single_operand(instruction)

        r1 = self.reg.get(1)
        assert r1 == 0o013334

        condition_codes = self.psw.NZVC()
        assert condition_codes == "0000"

