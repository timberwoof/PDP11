# test_hardware.py
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
    stack = stack(psw, ram, reg)
    am = am(psw, ram, reg)

    def test_ram_basic(self):
        assert ram.top_of_memory == 0o177777
        assert ram.PSW_address   == ram.top_of_memory - 1
        assert ram.io_space      == ram.top_of_memory - 0o1000

    def test_ram_byte_1(self):
        test_value = 0o107
        test_address = 0o4123
        self.ram.write_byte(test_address,test_value)
        assert ram.memory[test_address] == test_value
        assert self.ram.read_byte(test_address) == test_value

    def test_ram_byte_2(self):
        test_value = 0o270
        test_address = 0o4123
        self.ram.write_byte(test_address,test_value)
        assert ram.memory[test_address] == test_value
        assert self.ram.read_byte(test_address) == test_value

    def test_ram_bytes(self):
        test_value = 0o105
        test_address = ram.top_of_memory - 1
        self.ram.write_byte(test_address,test_value)
        assert self.ram.read_byte(test_address) == test_value

        for i in range (0,0o277,1):
            mem_test_value =  i
            self.ram.write_byte(i, mem_test_value)

        for i in range (0,0o277,2):
            mem_test_value =  i
            assert self.ram.read_byte(i) == mem_test_value


    def test_ram_word_1(self):
        test_value = 0o107070
        test_address = 0o6234

        self.ram.write_word(test_address,test_value)

        actual_value = self.ram.read_word(test_address)
        assert ram.memory[test_address] == test_value & mask_low_byte
        assert ram.memory[test_address+1] == (test_value & mask_high_byte) >> 8
        assert  actual_value == test_value

    def test_ram_word_2(self):
        test_value = 0o170707
        test_address = 0o6234

        self.ram.write_word(test_address,test_value)

        actual_value = self.ram.read_word(test_address)
        assert ram.memory[test_address] == test_value & mask_low_byte
        assert ram.memory[test_address+1] == (test_value & mask_high_byte) >> 8
        assert  actual_value == test_value

    def test_ram_word_top(self):
        test_value = 0o123232
        test_address = ram.top_of_memory - 2

        self.ram.write_word(test_address,test_value)

        assert ram.memory[test_address] == test_value & mask_low_byte
        assert ram.memory[test_address+1] == (test_value & mask_high_byte) >> 8
        assert self.ram.read_word(test_address) == test_value

    def test_ram_words(self):
        test_value = 0o123234
        for i in range (1000,2000,2):
            mem_test_value = test_value + i
            self.ram.write_word(i, mem_test_value)

        for i in range (1000,2000,2):
            expected_value = test_value + i
            actual_value = self.ram.read_word(i)
            assert actual_value == expected_value

    def test_ram_wordbyte(self):
        test_base = 0o10000
        test_range = 0o30000
        for value in range(0, test_range, 2):
            test_address = test_base + value
            self.ram.write_word(test_address, value)

        for value in range(0, test_range, 2):
            test_address_low = test_base + value
            test_address_high = test_base + value +1

            low_byte = self.ram.read_byte(test_address_low)
            high_byte = self.ram.read_byte(test_address_high)
            sum = low_byte + (high_byte << 8)

            expected_low_byte = value & mask_low_byte
            expected_high_byte = (value & mask_high_byte) >> 8

            assert low_byte == expected_low_byte
            assert high_byte == expected_high_byte

    def test_psw(self):
        test_value = 0o123236
        self.psw.set_PSW(PSW=test_value)
        assert self.psw.PSW == test_value

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

        test_offset = 0o123232
        self.reg.set_pc_2x_offset(test_offset)
        expected_value = expected_value + 2 + (test_offset & mask_low_byte) * 2
        assert self.reg.get_pc() == expected_value

    def test_sp(self):
        test_value = 0o123221
        self.reg.set_sp(test_value)
        assert self.reg.get_sp() == test_value

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