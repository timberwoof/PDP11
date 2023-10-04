"""run PDP11 in terminal emulator"""
from pdp11 import PDP11
from pdp11 import pdp11Run

# instantiate the PDP11
pdp11 = PDP11()
run = pdp11Run(pdp11)

# power on
run.run_in_terminal()
