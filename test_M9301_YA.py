from pdp11 import PDP11
from pdp11 import pdp11Run
class TestClass():

    def test_M9301_YA(self):
        """The M9301-YA is designed specifically for PDP-ll/04 and PDP-ll/34 OEM systems."""
        print('test_M9301-YA')
        pdp11 = PDP11(False)
        run = pdp11Run(pdp11)

        #run.run_in_terminal()
        run.run(300)

# http://ftpmirror.your.org/pub/misc/bitsavers/pdf/dec/pdp11/xxdp/diag_listings/MAINDEC-11-DQM9A-A-D_M9301_ROM_Bootstrap_Jan77.pdf
