# test_hardware_ram    .py
# test the pdp11Hardware.py module using pytest
# pip3 install --upgrade pip
# pip install -U pytest

import pytest
from pdp11 import pdp11
from pdp11Boot import boot

mask_word = 0o177777
mask_word_msb = 0o100000
mask_byte_msb = 0o000200
mask_low_byte = 0o000377
mask_high_byte = 0o177400

# http://www.retrocmp.com/how-tos/interfacing-to-a-pdp-1105/146-interfacing-with-a-pdp-1105-test-programs-and-qhello-worldq
hello_world = [0o012702,  # 2000 start:  MOV 0o27 0o2
               0o177564,  # serial+4,r2  ; r2 points to DL11
               0o012701,  # 2004 MOV
               0o002032,  # string,r1    ; r1 points to current char
               0o112100,  # 2010 nxtchr: MOVB (r1)+,r0) ; load xmt char
               0o001405,  # 2012 BEQ done     ; string is terminated with 0
               0o110062,  # 2014 MOVB r0,2(r2) ; write char to transmit buffer
               0o000002,  #
               0o105712,  # 2020 wait: TSTB (r2) ; character transmitted?
               0o100376,  # BPL wait     ; no, loop
               0o000771,  # BR nxtchr ; transmit next character
               0o000000,  # 2026 halt
               0o000763,  # br start
               0o62510, 0o66154, 0o26157, 0o73440, 0o71157, 0o62154, 0o12]
# Following are bytes, not words.
# 0o110,     0o145,     0o154,  # .ascii /Hello, world/
# 0o154,     0o157,     0o054,
# 0o040,     0o167,     0o157,
# 0o162,     0o154,     0o144,
# 0o012,     0o000]    # lf, end
hello_address = 0o2000

class TestClass():

    def test_hello_world(self):
        self.pdp11 = pdp11()
        self.boot = boot(self.pdp11.reg, self.pdp11.ram)
        self.boot.load_machine_code(hello_world, hello_address)
        self.pdp11.reg.set_pc(0o2000, "load_machine_code")
        self.pdp11.ram.dump(0o2000, 0o2064)
        self.pdp11.run()

