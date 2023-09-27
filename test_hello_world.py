# test_hardware_ram    .py
# test the pdp11Hardware.py module using pytest
# pip3 install --upgrade pip
# pip install -U pytest

import pytest
from pdp11 import pdp11CPU
from pdp11 import pdp11Run
from pdp11Boot import pdp11Boot
from stopwatch import stopWatchList as sw

mask_word = 0o177777
mask_word_msb = 0o100000
mask_byte_msb = 0o000200
mask_low_byte = 0o000377
mask_high_byte = 0o177400

# http://www.retrocmp.com/how-tos/interfacing-to-a-pdp-1105/146-interfacing-with-a-pdp-1105-test-programs-and-qhello-worldq
hello_world = [0o012702,  # 2000 start:  MOV 0o27 0o2
               0o177564,  # 2002         serial+4,r2    ; r2 points to DL11
               0o012701,  # 2004         MOV
               0o002032,  # 2006         string,r1      ; r1 points to current char
               0o112100,  # 2010 nxtchr: MOVB (r1)+,r0) ; load xmt char
               0o001405,  # 2012         BEQ done       ; string is terminated with 0
               0o110062,  # 2014         MOVB r0,2(r2)  ; write char to transmit buffer
               0o000002,  # 2016
               0o105712,  # 2020 wait:   TSTB (r2)      ; character transmitted?
               0o100376,  # 2022         BPL wait       ; no, loop
               0o000771,  # 2024         BR nxtchr      ; transmit next character
               0o000000,  # 2026         halt
               0o000763,  # 2030         br start
               0o62510, 0o66154, 0o26157, 0o73440, 0o71157, 0o62154, 0o6441, 0o012]
# Following are bytes, not words.
# .ascii /Hello, world!/
# 0o110,    0o145,
# 0o154,    0o154,
# 0o157,    0o054,
# 0o040,    0o167,
# 0o157,    0o162,
# 0o154,    0o144,
# 0o041,    0o015,
# 0o012,    0o000]    # lf, end
hello_address = 0o2000

class TestClass():

    def test_hello_world(self):
        print('test_hello_world pdp11CPU()')
        pdp11 = pdp11CPU(sw())
        print('test_hello_world pdp11Boot()')
        boot = pdp11Boot(pdp11.reg, pdp11.ram)
        print('test_hello_world load_machine_code()')
        boot.load_machine_code(hello_world, hello_address)
        pdp11.reg.set_pc(0o2000, "load_machine_code")
        pdp11.ram.dump(0o2000, 0o2064)
        run = pdp11Run(pdp11)
        run.runInTerminal()

