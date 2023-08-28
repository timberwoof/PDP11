import pytest
from pdp11 import pdp11CPU
from pdp11 import pdp11Run
from pdp11Boot import pdp11Boot

mask_word = 0o177777
mask_word_msb = 0o100000
mask_byte_msb = 0o000200
mask_low_byte = 0o000377
mask_high_byte = 0o177400

class TestClass():

    def test_CLR(self):
        print('test_M9301-YA')
        pdp11 = pdp11CPU()
        boot = pdp11Boot(pdp11.reg, pdp11.ram)
        address = pdp11.boot.read_PDP11_assembly_file('source/M9301-YA.txt')
        pdp11.reg.set_pc(address, "test_M9301-YA") # 0o165000
        pdp11.ram.dump(0o165000, 0o165007)
        run = pdp11Run(pdp11)
        run.runInTerminal()
