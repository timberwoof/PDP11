import pytest
from pdp11 import pdp11

mask_word = 0o177777
mask_word_msb = 0o100000
mask_byte_msb = 0o000200
mask_low_byte = 0o000377
mask_high_byte = 0o177400

class TestClass():

    def test_CLR(self):
        print('test_M9301-YA')
        self.pdp11 = pdp11()

        address = self.pdp11.boot.read_PDP11_assembly_file('source/M9301-YA.txt')
        self.pdp11.reg.set_pc(address, "test_M9301-YA") # 0o165000
        self.pdp11.ram.dump(0o165000, 0o165007)
        #self.ram.dump(0o165000, 0o165777)
        #self.ram.dump(0o173000, 0o173776)

        self.pdp11.run()