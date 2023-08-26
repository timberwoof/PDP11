# test_hardware_ram    .py
# test the pdp11Hardware.py module using pytest
# pip3 install --upgrade pip
# pip install -U pytest

import pytest
from pdp11Hardware import ram
from pdp11Hardware import registers as reg
from pdp11Hardware import psw
from pdp11Hardware import stack
from pdp11Hardware import addressModes as am

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

    def test_registers(self):
        for i in range(0,7):
            test_value = 0o123223 + i
            self.reg.set(i, test_value)
            assert self.reg.get(i) == test_value

    def test_pc(self):
        test_value = 0o1232225
        expected_value = test_value & mask_word
        self.reg.set_pc(test_value)
        assert self.reg.get_pc() == expected_value
        self.reg.inc_pc()
        assert self.reg.get_pc() == expected_value + 2
        self.reg.set_pc(test_value)
        self.reg.inc_pc(2)
        assert self.reg.get_pc() == expected_value + 2

        test_offset = 0o123232
        self.reg.set_pc_2x_offset(test_offset)
        expected_value = expected_value + 2 + (test_offset & mask_low_byte) * 2
        assert self.reg.get_pc() == expected_value

    def test_sp(self):
        test_value = 0o123221
        self.reg.set_sp(test_value)
        assert self.reg.get_sp() == test_value

