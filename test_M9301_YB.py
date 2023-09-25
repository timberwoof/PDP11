import pytest
from pdp11 import pdp11CPU
from pdp11 import pdp11Run
from pdp11Boot import pdp11Boot
class TestClass():

    def test_M9301_YB(self):
        """The M9301-YB is designed specifically for PDP-ll/04 and PDP-ll/34 end user systems."""
        print('test_M9301-YB')
        pdp11 = pdp11CPU()
        boot = pdp11Boot(pdp11.reg, pdp11.ram)
        Boot0 = pdp11.boot.read_PDP11_assembly_file('source/M9301-YA.txt')
        pdp11.reg.set_pc(0o173000, "test_M9301-YB") # 0o165000
        run = pdp11Run(pdp11)
        run.runInTerminal()