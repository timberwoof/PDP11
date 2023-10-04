from pdp11_hardware import Registers as reg
from pdp11_hardware import Ram
from pdp11_hardware import PSW
from pdp11_hardware import Stack
from pdp11_hardware import AddressModes as am
from pdp11_double_operand_ops import DoubleOperandOps as dopr
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
    dopr = dopr(reg, ram, psw, am, sw)

    def SS(self, mode, register):
        return (mode << 3 | register) << 6

    def DD(self, mode, register):
        return (mode << 3 | register)

    def op(self, opcode, modeS=0, regS=0, modeD=0, regD=1):
        return opcode | self.SS(modeS, regS) | self.DD(modeD, regD)

    def test_BIC(self):
        print('test_BIC')
        self.psw.set_psw(psw=0)
        self.reg.set(1, 0b1010101010101010)
        self.reg.set(2, 0b1111111111111111)

        instruction = self.op(opcode=0o040000, modeS=0, regS=1, modeD=0, regD=2)   # mode 0 R1
        assert self.dopr.is_double_operand_SSDD(instruction)
        self.dopr.do_double_operand_SSDD(instruction)

        r2 = self.reg.get(2)
        assert r2 == 0b0101010101010101

        condition_codes = self.psw.get_nvzc_string()
        assert condition_codes == "0000"

    def test_BICB(self):
        print('test_BICB')
        self.psw.set_psw(psw=0)
        # evil test puts word data into a byte test and expects byte result
        self.reg.set(1, 0b1010101010101010)
        self.reg.set(2, 0b1111111111111111)

        instruction = self.op(opcode=0o140000, modeS=0, regS=1, modeD=0, regD=2)   # mode 0 R1
        assert self.dopr.is_double_operand_SSDD(instruction)
        self.dopr.do_double_operand_SSDD(instruction)

        r2 = self.reg.get(2)
        assert r2 == 0b0000000001010101

        condition_codes = self.psw.get_nvzc_string()
        assert condition_codes == "0000"
