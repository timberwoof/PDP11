from pdp11 import PDP11
from pdp11 import pdp11Run
class TestClass():

    def test_M9301_YA(self):
        """The M9301-YA is designed specifically for PDP-ll/04 and PDP-ll/34 OEM systems."""
        print('test_M9301-YA')
        pdp11 = PDP11()
        run = pdp11Run(pdp11)
        run.run_in_terminal()
