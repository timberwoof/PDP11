from pdp11_hardware import Registers as reg
from pdp11_hardware import Ram
from pdp11_hardware import PSW
from pdp11_hardware import Stack
from pdp11_hardware import AddressModes as am
from pdp11_single_operand_ops import SingleOperandOps as sopr
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
    sopr = sopr(reg, ram, psw, am, sw)

    def test_CLR(self):
        print('test_CLR')
        self.psw.set_psw(psw=0)
        self.reg.set(1, 0o013333)

        instruction = 0o05001  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        self.sopr.do_single_operand(instruction)

        r1 = self.reg.get(1)
        assert r1 == 0o0

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0100"

    def test_COM(self):
        print('test_COM')
        self.psw.set_psw(psw=0)
        self.reg.set(1, 0o013333)

        instruction = 0o05101 # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        self.sopr.do_single_operand(instruction)

        r1 = self.reg.get(1)
        assert r1 == 0o164444

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "1001"

    def test_INC(self):
        print('test_INC')
        self.psw.set_psw(psw=0)
        self.reg.set(1, 0o013333)

        instruction = 0o05201  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        self.sopr.do_single_operand(instruction)

        r1 = self.reg.get(1)
        assert r1 == 0o013334

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    def test_INCB(self):
        print('test_INCB')
        self.psw.set_psw(psw=0)
        self.reg.set(1, 0o000033)

        instruction = 0o105201  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        self.sopr.do_single_operand(instruction)

        r1 = self.reg.get(1)
        assert r1 == 0o000034

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    def test_SWAB1(self):
        print('test_SWAB1')
        # from pdp11 book 0111111111111111 -> 1111111101111111
        self.psw.set_psw(psw=0o0177777)
        self.reg.set(1, 0o077777)

        instruction = 0o000301  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        self.sopr.do_single_operand(instruction)

        r1 = self.reg.get(1)
        assert r1 == 0o177577

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    def test_SWAB2(self):
        print('test_SWAB2')
        # reverse of pdp11 book 1111111101111111 -> 0111111111111111
        self.psw.set_psw(psw=0o0177777)
        self.reg.set(1, 0o177577)

        instruction = 0o000301  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        self.sopr.do_single_operand(instruction)

        r1 = self.reg.get(1)
        assert r1 == 0o077777

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "1000"

    def test_SWAB3(self):
        print('test_SWAB3')
        # BFI reverse bits 0000000011111111 -> 1111111100000000
        self.psw.set_psw(psw=0o0177777)
        # 0 000 000 011 111 111
        self.reg.set(1, 0o000377)

        instruction = 0o000301  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        self.sopr.do_single_operand(instruction)

        r1 = self.reg.get(1)
        # 1 111 111 100 000 000
        assert r1 == 0o177400

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0100" # NZVC

    def test_SWAB4(self):
        print('test_SWAB4')
        # BFI reverse bits back 1111111100000000 -> 0000000011111111
        self.psw.set_psw(psw=0o0177777)
        # 0 000 000 011 111 111
        self.reg.set(1, 0o177400)

        instruction = 0o000301  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        self.sopr.do_single_operand(instruction)

        r1 = self.reg.get(1)
        # 1 111 111 100 000 000
        assert r1 == 0o000377

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "1000" # NZVC
