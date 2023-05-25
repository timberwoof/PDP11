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
        print('test_ram_basic')
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
        test_value = 0o107
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
        print('test_ram_word 1')
        test_value = 0o107070
        self.ram.write_word(0,test_value)
        actual_value = self.ram.read_word(0)
        print(f'{oct(test_value)}:{oct(actual_value)}')
        assert  actual_value == test_value

    def test_ram_word_2(self):
        test_value = 0o170707
        self.ram.write_word(0,test_value)
        actual_value = self.ram.read_word(0)
        print(f'{oct(test_value)}:{oct(actual_value)}')
        assert  actual_value == test_value

    def test_ram_word_top(self):
        test_value = 0o123232
        test_address = ram.top_of_memory - 2
        self.ram.write_word(test_address,test_value)
        assert self.ram.read_word(test_address) == test_value

    def test_ram_words(self):
        test_value = 0o123232
        for i in range (1000,2000,2):
            mem_test_value = test_value + i
            self.ram.write_word(i, mem_test_value)

        for i in range (1000,2000,2):
            expected_value = test_value + i
            actual_value = self.ram.read_word(i)
            print(f'{i}, {oct(expected_value)}:{oct(actual_value)}')
            assert actual_value == expected_value

    def test_ram_wordbyte(self):
        print('test_ram_wordbyte')
        test_base = 0o10000
        test_range = 0o30000
        for value in range(0, test_range, 2):
            test_address = test_base + value
            #print(f'{oct(test_address)}:{oct(value)}')
            self.ram.write_word(test_address, value)

        for value in range(0, test_range, 2):
            test_address_low = test_base + value
            test_address_high = test_base + value +1

            low_byte = self.ram.read_byte(test_address_low)
            high_byte = self.ram.read_byte(test_address_high)
            sum = low_byte + (high_byte << 8)
            print(f'{oct(test_address_low)}:{oct(high_byte)}:{oct(low_byte)}:{oct(sum)}')

            expected_low_byte = value & mask_low_byte
            expected_high_byte = (value & mask_high_byte) >> 8

            assert low_byte == expected_low_byte
            assert high_byte == expected_high_byte
