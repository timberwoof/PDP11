"""test condition code operators"""

# pdp11-40 ref p. 4-79

from pdp11_hardware import Registers as reg
from pdp11_hardware import Ram
from pdp11_hardware import PSW
from pdp11_hardware import AddressModes as am
from pdp11_condition_code_ops import ConditionCodeOps as ccops
from stopwatches import StopWatches as sw

class TestClass():
    reg = reg()
    ram = Ram(reg)
    psw = PSW(ram)
    sw = sw()
    ccops = ccops(psw, sw)

    set_opcode = 0o000260
    clear_opcode = 0o000240
    psw_bits = 0o000017

    def CLX(self, cvzn):
        return self.clear_opcode | cvzn

    def SEX(self, cvzn):
        return self.set_opcode | cvzn

    def test_set_opcodes(self):
        test_code = 0o01
        while test_code <= 0o17:
            self.psw.set_psw(psw=0)
            instruction = self.SEX(test_code)
            assert self.ccops.is_condition_code_operation(instruction)

            self.ccops.do_condition_code_operation(instruction)

            result_code = self.psw.get_psw() & self.psw_bits
            print(f'instruction:{oct(instruction)} {oct(test_code)}->{oct(result_code)}')
            assert test_code == result_code

            test_code = test_code + 1


    def test_clr_opcodes(self):
        test_code = 0o00
        while test_code <= 0o17:
            self.psw.set_psw(psw=0o17)
            instruction = self.CLX(test_code)
            assert self.ccops.is_condition_code_operation(instruction)

            expected = (self.psw.get_psw() & self.psw_bits) & ~test_code

            self.ccops.do_condition_code_operation(instruction)

            result_code = self.psw.get_psw() & self.psw_bits
            print(f'instruction:{oct(instruction)} {oct(test_code)}->{oct(result_code)}')
            assert expected == result_code

            test_code = test_code + 1

