# test_Tek4010.py
# test the 4010 emulator
# This test class helps define the needs placed on the
# as yet unwritten configuration system

from pdp11 import PDP11
from pdp11 import pdp11Run
from pdp11_boot import pdp11Boot

MASK_WORD = 0o177777
MASK_WORD_MSB = 0o100000
MASK_BYTE_MSB = 0o000200
MASK_LOW_BYTE = 0o000377
MASK_HIGH_BYTE = 0o177400

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
        pdp11 = PDP11('TEK4010') # this is where I need configuration
        print('test_echo pdp11Boot()')
        boot = pdp11Boot(pdp11.reg, pdp11.ram)
        print('test_echo load_machine_code()')
        boot.load_machine_code(echo, echo_address)
        pdp11.reg.set_pc(echo_address, "load_machine_code")
        pdp11.ram.dump(echo_address, echo_address + 0o10)
        run = pdp11Run(pdp11)
        run.run_with_TEK4010_emulator()