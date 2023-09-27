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
    ram = ram(reg)
    psw = psw(ram)
    stack = stack(reg, ram, psw)
    am = am(reg, ram, psw)
    dopr = dopr(reg, ram, psw, am)

    def SS(self, mode, register):
        return (mode << 3 | register) << 6

    def DD(self, mode, register):
        return (mode << 3 | register)

    def op(self, opcode, modeS=0, regS=0, modeD=0, regD=1):
        return opcode | self.SS(modeS, regS) | self.DD(modeD, regD)

    def test_BIC(self):
        print('test_BIC')
        self.psw.set_PSW(PSW=0)
        self.reg.set(1, 0b1010101010101010)
        self.reg.set(2, 0b1111111111111111)

        instruction = self.op(opcode=0o040000, modeS=0, regS=1, modeD=0, regD=2)   # mode 0 R1
        assert self.dopr.is_double_operand_SSDD(instruction)
        self.dopr.do_double_operand_SSDD(instruction)

        r2 = self.reg.get(2)
        assert r2 == 0b0101010101010101

        condition_codes = self.psw.NZVC()
        assert condition_codes == "0000"

    def test_BICB(self):
        print('test_BICB')
        self.psw.set_PSW(PSW=0)
        # evil test puts word data into a byte test and expects byte result
        self.reg.set(1, 0b1010101010101010)
        self.reg.set(2, 0b1111111111111111)

        instruction = self.op(opcode=0o140000, modeS=0, regS=1, modeD=0, regD=2)   # mode 0 R1
        assert self.dopr.is_double_operand_SSDD(instruction)
        self.dopr.do_double_operand_SSDD(instruction)

        r2 = self.reg.get(2)
        assert r2 == 0b0000000001010101

        condition_codes = self.psw.NZVC()
        assert condition_codes == "0000"

