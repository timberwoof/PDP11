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
        print('\ntest_CLR')
        self.psw.set_psw(psw=0)
        self.reg.set(1, 0o013333)

        instruction = 0o05001  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        run, operand1, operand2, assembly, report = self.sopr.do_single_operand(instruction)
        assert assembly == "CLR R1"

        r1 = self.reg.get(1)
        assert r1 == 0o0

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0100"

    def test_COM_1(self):
        print('\ntest_COM_1  complement')
        # 0b0001011011011011
        # 0b1110100100100100
        self.psw.set_psw(psw=0)
        self.reg.set(1, 0o013333)

        instruction = 0o005101 # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        run, operand1, operand2, assembly, report = self.sopr.do_single_operand(instruction)
        assert assembly == "COM R1"

        r1 = self.reg.get(1)
        print(f'R1:{oct(r1)}')
        assert r1 == 0o164444

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "1001"

    def test_COM_2(self):
        print('\ntest_COM_2  complement')
        # 0b1110100100100100
        # 0b0001011011011011
        self.psw.set_psw(psw=0)
        self.reg.set(1, 0o164444)

        instruction = 0o005101 # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        run, operand1, operand2, assembly, report = self.sopr.do_single_operand(instruction)
        assert assembly == "COM R1"

        r1 = self.reg.get(1)
        assert r1 == 0o013333

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0001"

    def test_COMB_1(self):
        print('\ntest_COMB_1  complement')
        self.psw.set_psw(psw=0)
        self.reg.set(1, 0o000022)

        instruction = 0o105101 # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        run, operand1, operand2, assembly, report = self.sopr.do_single_operand(instruction)
        assert assembly == "COMB R1"

        r1 = self.reg.get(1)
        assert r1 == 0o355

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "1001"

    def test_INC(self):
        print('\ntest_INC')
        self.psw.set_psw(psw=0)
        self.reg.set(1, 0o013333)

        instruction = 0o05201  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        run, operand1, operand2, assembly, report = self.sopr.do_single_operand(instruction)
        assert assembly == "INC R1"

        r1 = self.reg.get(1)
        assert r1 == 0o013334

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    def test_INCB(self):
        print('\ntest_INCB')
        self.psw.set_psw(psw=0)
        self.reg.set(1, 0o000033)

        instruction = 0o105201  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        run, operand1, operand2, assembly, report = self.sopr.do_single_operand(instruction)
        assert assembly == "INCB R1"

        r1 = self.reg.get(1)
        assert r1 == 0o000034

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    def test_DEC1(self):
        print('\ntest_DEC1')
        self.psw.set_psw(psw=0)
        self.reg.set(1, 0o013333)

        instruction = 0o05301  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        run, operand1, operand2, assembly, report = self.sopr.do_single_operand(instruction)
        assert assembly == "DEC R1"

        r1 = self.reg.get(1)
        assert r1 == 0o013332

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    def test_DEC2(self):
        print('\ntest_DEC2')
        self.psw.set_psw(psw=0)
        self.reg.set(1, 0o0001)

        instruction = 0o05301  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        run, operand1, operand2, assembly, report = self.sopr.do_single_operand(instruction)
        assert assembly == "DEC R1"

        r1 = self.reg.get(1)
        assert r1 == 0

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0100"

    def test_DEC3(self):
        print('\ntest_DEC3')
        self.psw.set_psw(psw=0)
        self.reg.set(1, 0)

        instruction = 0o05301  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        run, operand1, operand2, assembly, report = self.sopr.do_single_operand(instruction)
        assert assembly == "DEC R1"

        r1 = self.reg.get(1)
        assert r1 == -1

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "1000"

    def test_DECB1(self):
        print('\ntest_DECB1')
        self.psw.set_psw(psw=0)
        self.reg.set(1, 0o000001)

        instruction = 0o105301  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        run, operand1, operand2, assembly, report = self.sopr.do_single_operand(instruction)
        assert assembly == "DECB R1"

        r1 = self.reg.get(1)
        assert r1 == 0o000000

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0010"

    def test_SWAB1(self):
        print('\ntest_SWAB1')
        # from pdp11 book 0111111111111111 -> 1111111101111111
        self.psw.set_psw(psw=0o0177777)
        self.reg.set(1, 0o077777)

        instruction = 0o000301  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        run, operand1, operand2, assembly, report = self.sopr.do_single_operand(instruction)
        assert assembly == "SWAB R1"

        r1 = self.reg.get(1)
        assert r1 == 0o177577

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    def test_SWAB2(self):
        print('\ntest_SWAB2')
        # reverse of pdp11 book 1111111101111111 -> 0111111111111111
        self.psw.set_psw(psw=0o0177777)
        self.reg.set(1, 0o177577)

        instruction = 0o000301  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        run, operand1, operand2, assembly, report = self.sopr.do_single_operand(instruction)
        assert assembly == "SWAB R1"

        r1 = self.reg.get(1)
        assert r1 == 0o077777

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "1000"

    def test_SWAB3(self):
        print('\ntest_SWAB3')
        # BFI reverse bits 0000000011111111 -> 1111111100000000
        self.psw.set_psw(psw=0o0177777)
        # 0 000 000 011 111 111
        self.reg.set(1, 0o000377)

        instruction = 0o000301  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        run, operand1, operand2, assembly, report = self.sopr.do_single_operand(instruction)
        assert assembly == "SWAB R1"

        r1 = self.reg.get(1)
        # 1 111 111 100 000 000
        assert r1 == 0o177400

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0100" # NZVC

    def test_SWAB4(self):
        print('\ntest_SWAB4')
        # BFI reverse bits back 1111111100000000 -> 0000000011111111
        self.psw.set_psw(psw=0o0177777)
        # 0 000 000 011 111 111
        self.reg.set(1, 0o177400)

        instruction = 0o000301  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        run, operand1, operand2, assembly, report = self.sopr.do_single_operand(instruction)
        assert assembly == "SWAB R1"

        r1 = self.reg.get(1)
        # 1 111 111 100 000 000
        assert r1 == 0o000377

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "1000" # NZVC

    def test_ROR_1(self):
        print('\ntest_ROR_1')
        self.psw.set_psw(psw=0o0177777)
        self.reg.set(1, 0b1111111100000000)
        instruction = 0o006001  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        run, operand1, operand2, assembly, report = self.sopr.do_single_operand(instruction)
        assert assembly == "ROR R1"
        r1 = self.reg.get(1)
        assert r1 == 0b0111111110000000
        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000" # NZVC

    def test_ROR_2(self):
        print('\ntest_ROR_2')
        self.psw.set_psw(psw=0o0177777)
        self.reg.set(1, 0b0000000011111111)
        instruction = 0o006001  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        run, operand1, operand2, assembly, report = self.sopr.do_single_operand(instruction)
        assert assembly == "ROR R1"
        r1 = self.reg.get(1)
        assert r1 == 0b1000000001111111
        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "1001" # NZVC

    def test_RORB_1(self):
        print('\ntest_RORB_1')
        self.psw.set_psw(psw=0o0177777)
        self.reg.set(1, 0b0000111111110000)
        instruction = 0o106001  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        run, operand1, operand2, assembly, report = self.sopr.do_single_operand(instruction)
        assert assembly == "RORB R1"
        print (report)
        r1 = self.reg.get(1)
        assert r1 == 0b1000011111111000
        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "1010" # NZVC

    def test_RORB_2(self):
        print('\ntest_RORB_2')
        self.psw.set_psw(psw=0o0177777)
        self.reg.set(1, 0b1111000000001111)
        instruction = 0o106001  # mode 0 R1
        assert self.sopr.is_single_operand(instruction)
        run, operand1, operand2, assembly, report = self.sopr.do_single_operand(instruction)
        assert assembly == "RORB R1"
        print (report)
        r1 = self.reg.get(1)
        assert r1 == 0b0111100010000111
        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "1001" # NZVC
