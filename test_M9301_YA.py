import logging

from pdp11_boot import pdp11Boot
from pdp11 import PDP11
from pdp11 import pdp11Run
class TestClass():

    def not_test_M9301_YA(self):
        """The M9301-YA is designed specifically for PDP-ll/04 and PDP-ll/34 OEM systems."""
        # not a test becuse there's no wau yet to run without the UI emulator
        logging.info('test_M9301-YA')
        pdp11 = PDP11(False)
        boot = pdp11Boot(pdp11.reg, pdp11.ram)
        Boot0 = boot.read_pdp11_assembly_file('source/M9301-YA.txt')
        pdp11.reg.set_pc(0o173000, "test_M9301-YA") # 0o165000
        run = pdp11Run(pdp11)
        run.run_with_VT52_emulator()
# http://ftpmirror.your.org/pub/misc/bitsavers/pdf/dec/pdp11/xxdp/diag_listings/MAINDEC-11-DQM9A-A-D_M9301_ROM_Bootstrap_Jan77.pdf
