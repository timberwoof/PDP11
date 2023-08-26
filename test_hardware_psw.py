# test_hardware_psw.py
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

    def test_psw_address(self):
        assert psw.PSW_address == ram.top_of_memory - 1

    def test_psw_set(self):
        test_value = 0o123236
        self.psw.set_PSW(PSW=test_value)
        assert self.psw.PSW == test_value

    def test_psw_mode(self):
        # mode, priority, trap, N, Z, V, C, PSW
        self.psw.set_PSW(mode=0)
        self.psw.set_PSW(mode=3)
        actual_psw = self.psw.PSW & 0o140000
        expected_PSW = 0o140000
        assert actual_psw == expected_PSW

    def test_psw_priority(self):
        self.psw.set_PSW(priority=0)
        self.psw.set_PSW(priority=15)
        actual_psw = self.psw.PSW & 0o000340
        expected_PSW = 0o000340
        assert actual_psw == expected_PSW

    def test_psw_trap(self):
        self.psw.set_PSW(trap=0)
        self.psw.set_PSW(trap=1)
        actual_psw = self.psw.PSW & 0o000020
        expected_PSW = 0o000020
        assert actual_psw == expected_PSW

    def test_psw_N(self):
        self.psw.set_PSW(N=0)
        self.psw.set_PSW(N=1)
        actual_psw = self.psw.PSW & 0o000010
        expected_PSW = 0o000010
        assert actual_psw == expected_PSW

    def test_psw_Z(self):
        self.psw.set_PSW(Z=0)
        self.psw.set_PSW(Z=1)
        actual_psw = self.psw.PSW & 0o000004
        expected_PSW = 0o000004
        assert actual_psw == expected_PSW

    def test_psw_V(self):
        self.psw.set_PSW(V=0)
        self.psw.set_PSW(V=1)
        actual_psw = self.psw.PSW & 0o000002
        expected_PSW = 0o000002
        assert actual_psw == expected_PSW

    def test_psw_C(self):
        self.psw.set_PSW(C=0)
        self.psw.set_PSW(C=1)
        actual_psw = self.psw.PSW & 0o000001
        expected_PSW = 0o000001
        assert actual_psw == expected_PSW

    def test_psw_addb(self):
        self.psw.set_PSW(PSW=0)
        a = 3
        b = 4
        sum = self.psw.addb(a,b)
        assert sum == a + b
        assert self.psw.V() == 0
        assert self.psw.Z() == 0

    def test_psw_addb_v(self):
        self.psw.set_PSW(PSW=0)
        a = 191
        b = 191
        sum = self.psw.addb(a,b)
        assert sum == 126
        assert self.psw.V() == 1
        assert self.psw.Z() == 0



    #def test_psw_addb_z(self):

    #def test_psw_addw(self):
    #def test_psw_addw_v(self):
    #def test_psw_addw_z(self):

    #def test_psw_subbd(self):
    #def test_psw_subbd_n(self):

    #def tesT_psw_subw(self):
    #def tesT_psw_subw_n(self):