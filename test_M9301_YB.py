import pytest
from pdp11 import PDP11
from pdp11 import pdp11Run
from pdp11_boot import pdp11Boot
class TestClass():

    def not_test_M9301_YB(self):
        """The M9301-YB is designed specifically for PDP-ll/04 and PDP-ll/34 end user systems."""
        # *** this needs a much bigger memory space. This will fail.
        print('test_M9301-YB')
        pdp11 = PDP11()
        boot = pdp11Boot(pdp11.reg, pdp11.ram)
        Boot0 = pdp11.boot.read_pdp11_assembly_file('source/M9301-YB.txt')
        pdp11.reg.set_pc(0o173000, "test_M9301-YB") # 0o165000
        run = pdp11Run(pdp11)
        run.run_in_terminal()