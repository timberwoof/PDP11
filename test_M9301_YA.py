from pdp11 import PDP11
from pdp11 import pdp11Run
from pdp11_boot import pdp11Boot
class TestClass():

    def test_M9301_YA(self):
        """The M9301-YA is designed specifically for PDP-ll/04 and PDP-ll/34 OEM systems."""
        print('test_M9301-YA')
        pdp11 = PDP11()
        boot = pdp11Boot(pdp11.reg, pdp11.ram)
        Boot0 = pdp11.boot.read_pdp11_assembly_file('source/M9301-YA.txt')
        pdp11.reg.set_pc(0o165000, "test_M9301-YA")  # 0o165000
        run = pdp11Run(pdp11)
        run.run_in_terminal()
