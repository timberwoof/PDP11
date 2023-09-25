# test_DL11.py
# test the pdp11DL11.py module using pytest

import pytest
import random
from pdp11 import pdp11CPU
from pdp11 import pdp11Run
from pdp11DL11 import dl11

class TestClass():
    test_character = 0

    def make_test_character(self):
        tc = random.randint(32,128)
        self.test_character = tc
        return tc

    def test_receive(self):
        """whitebox testing of receive status and buffer.
        check status bits, stick a byte in. recheck status bits."""
        pdp11 = pdp11CPU()
        print('test_receive')

        # verify that the receive status register says nothing's ready
        RCSR = pdp11.ram.read_word(pdp11.dl11.RCSR_address)
        assert RCSR == 0o0

        # simulate receivig a byte
        pdp11.ram.write_word(pdp11.dl11.RBUF_address, self.make_test_character())

        # verify the receiver got a byte
        RCSR = pdp11.ram.read_word(pdp11.dl11.RCSR_address)
        assert RCSR & pdp11.dl11.RCSR_RCVR_DONE == pdp11.dl11.RCSR_RCVR_DONE

        # read the buffer and verify it's what we sent
        RBUF = pdp11.ram.read_word(pdp11.dl11.RBUF_address)
        assert RBUF == self.test_character

        # verify that the receiver is now empty
        RCSR = pdp11.ram.read_word(pdp11.dl11.RCSR_address)
        assert RCSR & pdp11.dl11.RCSR_RCVR_DONE == 0o0
        print('test_receive done')

    def test_transmit(self):
        """whitebox testing of transmit status and buffer
        check status bits, stick a byte in. rechech status bits."""
        pdp11 = pdp11CPU()
        print('test_transmit')

        # verify that the transmitter is ready to transmit
        XCSR = pdp11.ram.read_word(pdp11.dl11.XCSR_address)
        assert XCSR & pdp11.dl11.XCSR_XMIT_RDY == pdp11.dl11.XCSR_XMIT_RDY

        # simulate transmitting a byte
        pdp11.ram.write_word(pdp11.dl11.XBUF_address, self.make_test_character())

        # verify that transmit buffer is not ready for another byte
        XCSR = pdp11.ram.read_word(pdp11.dl11.XCSR_address)
        assert XCSR & pdp11.dl11.XCSR_XMIT_RDY == 0

        # read the bugger and verify it's what we sset
        XBUF = pdp11.ram.read_word(pdp11.dl11.XBUF_address)
        assert XBUF == self.test_character

        # verify  that  the transmit buffer is ready for another byte
        XCSR = pdp11.ram.read_word(pdp11.dl11.XCSR_address)
        assert XCSR & pdp11.dl11.XCSR_XMIT_RDY == pdp11.dl11.XCSR_XMIT_RDY
        print('test_transmit done')

    def test_maintenance(self):
        """set maintenance bit and verify that bytes go in and bytes go out"""
        pdp11 = pdp11CPU()
        print('test_maintenance')

        # set the maintenance bit and verify it.
        # This means DL11 connects its X output to R input
        pdp11.ram.write_word(pdp11.dl11.XCSR_address, pdp11.dl11.XCSR_MAINT)
        XCSR = pdp11.ram.read_word(pdp11.dl11.XCSR_address)
        assert XCSR & pdp11.dl11.XCSR_MAINT == pdp11.dl11.XCSR_MAINT

        # verify that there's no byte to read
        RCSR = pdp11.ram.read_word(pdp11.dl11.RCSR_address)
        assert RCSR == 0o0

        # verify that transmitter is ready
        XCSR = pdp11.ram.read_word(pdp11.dl11.XCSR_address)
        print(f'XCSR:{oct(XCSR)}') # maintenance mode should be set; ready should be set
        assert XCSR & pdp11.dl11.XCSR_XMIT_RDY == pdp11.dl11.XCSR_XMIT_RDY

        # transmit a byte
        pdp11.ram.write_word(pdp11.dl11.XBUF_address, self.make_test_character())

        # verify that we've transmitted it
        XCSR = pdp11.ram.read_word(pdp11.dl11.XCSR_address)
        assert XCSR & pdp11.dl11.XCSR_XMIT_RDY == 0

        # verify that a byte is ready to read
        RCSR = pdp11.ram.read_word(pdp11.dl11.RCSR_address)
        print(f'RCSR:{oct(RCSR)}') # maintenance mode should be set; ready should be set
        assert RCSR & pdp11.dl11.RCSR_RCVR_DONE == pdp11.dl11.RCSR_RCVR_DONE

        # receive the byte
        XBUF = pdp11.ram.read_word(pdp11.dl11.XBUF_address)
        assert XBUF == self.test_character

        # verify that the transmitted is ready again
        XCSR = pdp11.ram.read_word(pdp11.dl11.XCSR_address)
        assert XCSR & pdp11.dl11.XCSR_XMIT_RDY == pdp11.dl11.XCSR_XMIT_RDY

        print('test_maintenance done')
