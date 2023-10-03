import pytest
from pdp11_hardware import Registers as reg
from pdp11_hardware import Ram
from pdp11_hardware import PSW
from pdp11_hardware import Stack
from pdp11_hardware import AddressModes as am
from pdp11SingleOperandOps import singleOperandOps as sopr

MASK_WORD = 0o177777
MASK_WORD_MSB = 0o100000
MASK_BYTE_MSB = 0o000200
MASK_LOW_BYTE = 0o000377
MASK_HIGH_BYTE = 0o177400

class TestClass():
    reg = reg()
    ram = Ram(reg)
    psw = PSW(ram)
    stack = Stack(reg, ram, psw)
    am = am(reg, ram, psw)
    sopr = sopr(reg, ram, psw, am)

    def test_CLR(self):
        print('test_CLR')
        self.psw.set_psw(psw=0)
        self.reg.set(1, 0o013333)

        instruction = 0o05001  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        self.sopr.do_single_operand(instruction)

        r1 = self.reg.get(1)
        assert r1 == 0o0

        condition_codes = self.psw.get_nvzc_string()
        assert condition_codes == "0100"

    def test_COM(self):
        print('test_COM')
        self.psw.set_psw(psw=0)
        self.reg.set(1, 0o013333)

        instruction = 0o05101 # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        self.sopr.do_single_operand(instruction)

        r1 = self.reg.get(1)
        assert r1 == 0o164444

        condition_codes = self.psw.get_nvzc_string()
        assert condition_codes == "1001"

    def test_INC(self):
        print('test_CLR')
        self.psw.set_psw(psw=0)
        self.reg.set(1, 0o013333)

        instruction = 0o05201  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        self.sopr.do_single_operand(instruction)

        r1 = self.reg.get(1)
        assert r1 == 0o013334

        condition_codes = self.psw.get_nvzc_string()
        assert condition_codes == "0000"

