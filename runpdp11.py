from pdp11 import pdp11CPU
from pdp11 import pdp11Run

# instantiate the PDP11
pdp11 = pdp11CPU()
run = pdp11Run(pdp11)

# power on
run.runInTerminal()