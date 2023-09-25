# test_echo.py
# load a small pdp11 program that echoes inputs back to outputs

import pytest
from pdp11 import pdp11CPU
from pdp11 import pdp11Run
from pdp11Boot import pdp11Boot

mask_word = 0o177777
mask_word_msb = 0o100000
mask_byte_msb = 0o000200
mask_low_byte = 0o000377
mask_high_byte = 0o177400

# http://www.retrocmp.com/how-tos/interfacing-to-a-pdp-1105/146-interfacing-with-a-pdp-1105-test-programs-and-qhello-worldq
echo = [0o012700, 0o177560,  # start: mov #kbs, r0
        0o105710,  # wait: tstb (r0)       ; character received?
        0o100376,  # bpl wait        ; no, loop
        0o016060, 0o000002, 0o000006,  # mov 2(r0),6(r0) ; transmit data
        0o000772]  # br wait         ; get next character
echo_address = 0o001000

class TestClass():

    def test_echo(self):
        print('test_echo pdp11CPU()')
        pdp11 = pdp11CPU()
        print('test_echo pdp11Boot()')
        boot = pdp11Boot(pdp11.reg, pdp11.ram)
        print('test_echo load_machine_code()')
        boot.load_machine_code(echo, echo_address)
        pdp11.reg.set_pc(echo_address, "load_machine_code")
        pdp11.ram.dump(echo_address, echo_address+64)
        run = pdp11Run(pdp11)
        run.runInTerminal()

