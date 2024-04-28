import pdp11_util as u
import logging
from pdp11_logger import Logger

MASK_WORD = 0o177777
MASK_WORD_MSB = 0o100000
MASK_BYTE_MSB = 0o000200
MASK_LOW_BYTE = 0o000377
MASK_HIGH_BYTE = 0o177400

class TestClass():

    def test_oct3(self):
        assert u.oct3(0o27) == "027"

    def test_oct6(self):
        assert u.oct6(0o2127) == "002127"

    def test_pad(self):
        assert u.pad("arf", 6) == "arf   "

    def test_2cn(self):
        assert u.twosCompletentNegative(0) == 0
        assert u.twosCompletentNegative(1) == 65535
        assert u.twosCompletentNegative(2) == 65534
        assert u.twosCompletentNegative(586) == 64950
