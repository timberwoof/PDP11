from pdp11_hardware import Registers as reg
from pdp11_hardware import Ram
from pdp11_hardware import PSW
from pdp11_hardware import Stack
from pdp11_hardware import AddressModes as am

from pdp11_br_ops import br_ops
from pdp11_cc_ops import cc_ops
from pdp11_noopr_ops import noopr_ops
from pdp11_other_ops import other_ops
from pdp11_rss_ops import rss_ops
from pdp11_ss_ops import ss_ops
from pdp11_ssdd_ops import ssdd_ops

from stopwatches import StopWatches as sw

MASK_WORD = 0o177777
MASK_WORD_MSB = 0o100000
MASK_BYTE_MSB = 0o000200
MASK_LOW_BYTE = 0o000377
MASK_HIGH_BYTE = 0o177400

class TestClass():
    reg = reg()
    ram = Ram(reg)
    psw = PSW(ram)
    stack = Stack(reg, ram, psw)
    am = am(reg, ram, psw)
    sw = sw()

    rss_ops = rss_ops(reg, ram, psw, am, sw)

    def test_MUL(self):
        print('test_MUL')
        R = 1
        a = 0o001212
        b = 0o24

        self.psw.set_psw(psw=0)
        self.reg.set(R, a)
        instruction = 0o070000 | R << 6 | b
        print(oct(instruction))  # 0o0171312
        assert self.rss_ops.is_rss_op(instruction)
        self.rss_ops.do_rss_op(instruction)

        product = self.reg.get(R)
        print(f'product:{product}')
        assert product == a * b

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    def test_DIV(self):
        R = 2  # must be even
        a = 0o1536230
        b = 0o75  # max 0o77
        Rv1 = R + 1

        print(f'test_DIV {oct(a)} / {oct(b)} R:{R} Rv1:{Rv1} ')

        self.psw.set_psw(psw=0)

        # set up R and Rv1
        self.reg.set(R, a >> 16)
        self.reg.set(Rv1, a & MASK_WORD)

        instruction = 0o071000 | R << 6 | b
        print(f'test_DIV instruction:{oct(instruction)}')  # 0o0171312
        assert self.rss_ops.is_rss_op(instruction)
        self.rss_ops.do_rss_op(instruction)

        quotient = self.reg.get(R)
        remainder = self.reg.get(Rv1)
        print(f'quotient:{oct(quotient)}')
        print(f'remainder:{oct(remainder)}')
        assert quotient == a // b
        assert remainder == a % b

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

