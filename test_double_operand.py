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

    def test_byte_mask_w(self):
        print('\ntest_byte_mask_w')
        BW = 'W'
        value = 0b1010101010101010
        target = 0b0101010101010101
        return_value = self.dopr.byte_mask(BW, value, target)
        assert return_value == 0b1010101010101010

    def test_byte_mask_b1(self):
        print('\ntest_byte_mask_b1')
        BW = 'B'
        value = 0b1111111100000000
        target = 0b0000000011111111
        return_value = self.dopr.byte_mask(BW, value, target)
        assert return_value == 0

    def test_byte_mask_b2(self):
        print('\ntest_byte_mask_b2')
        BW = 'B'
        value = 0b0000000011111111
        target = 0b1111111100000000
        return_value = self.dopr.byte_mask(BW, value, target)
        assert return_value == 0b1111111111111111

    def test_byte_mask_b3(self):
        print('\ntest_byte_mask_b3')
        BW = 'B'
        value = 0b1010101010101010
        target = 0b0101010101010101
        return_value = self.dopr.byte_mask(BW, value, target)
        assert return_value == 0b0101010110101010

    def test_byte_mask_b4(self):
        print('\ntest_byte_mask_b4')
        BW = 'B'
        value = 0b0000000000000000
        target = 0b0101010101010101
        return_value = self.dopr.byte_mask(BW, value, target)
        assert return_value == 0b0101010100000000

    def test_BIC(self):
        print('\ntest_BIC')
        self.psw.set_psw(psw=0)
        self.reg.set(1, 0b1010101010101010)
        self.reg.set(2, 0b1111111111111111)

        instruction = self.op(opcode=0o040000, modeS=0, regS=1, modeD=0, regD=2)   # mode 0 R1
        assert self.dopr.is_double_operand_SSDD(instruction)
        run, operand1, operand2, assembly = self.dopr.do_double_operand_SSDD(instruction)
        assert assembly == 'BIC R1,R2'

        r2 = self.reg.get(2)
        assert r2 == 0b0101010101010101

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    def test_BICB(self):
        print('\ntest_BICB')
        self.psw.set_psw(psw=0)
        # evil test shows that The high byte is unaffected.
        self.reg.set(1, 0b1010101010101010)
        self.reg.set(2, 0b1111111111111111)


        instruction = self.op(opcode=0o140000, modeS=0, regS=1, modeD=0, regD=2)   # mode 0 R1
        assert self.dopr.is_double_operand_SSDD(instruction)
        run, operand1, operand2, assembly = self.dopr.do_double_operand_SSDD(instruction)
        assert assembly == 'BICB R1,R2'

        r2 = self.reg.get(2)
        assert r2 == 0b1111111101010101

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    def test_BIC_2(self):
        print('\ntest_BIC_2')
        # PDP-11/40 p. 4-21
        self.psw.set_psw(psw=0o777777)
        # evil test puts word data into a byte test and expects byte result
        self.reg.set(3, 0o001234)
        self.reg.set(4, 0o001111)

        instruction = self.op(opcode=0o040000, modeS=0, regS=3, modeD=0, regD=4)
        assert self.dopr.is_double_operand_SSDD(instruction)
        run, operand1, operand2, assembly = self.dopr.do_double_operand_SSDD(instruction)
        assert assembly == "BIC R3,R4"

        assert self.reg.get(3) == 0o001234
        assert self.reg.get(4) == 0o000101

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0001"

    def test_BICB_2(self):
        print('\ntest_BICB_2')
        # PDP-11/40 p. 4-21
        self.psw.set_psw(psw=0)
        # evil test puts word data into a byte test and expects byte result
        self.reg.set(3, 0o001234)
        self.reg.set(4, 0o001111)

        instruction = self.op(opcode=0o140000, modeS=0, regS=3, modeD=0, regD=4)
        assert self.dopr.is_double_operand_SSDD(instruction)
        run, operand1, operand2, assembly = self.dopr.do_double_operand_SSDD(instruction)
        assert assembly == "BICB R3,R4"

        assert self.reg.get(3) == 0o001234
        assert self.reg.get(4) == 0o001101

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    def test_MOV_0(self):
        print('\ntest_MOV_0')
        self.psw.set_psw(psw=0o777777)
        self.reg.set(3,0o123456)
        self.reg.set(4,0o000000)
        instruction = self.op(opcode=0o010000, modeS=0, regS=3, modeD=0, regD=4)   # mode 0 R1
        assert self.dopr.is_double_operand_SSDD(instruction)
        run, operand1, operand2, assembly = self.dopr.do_double_operand_SSDD(instruction)
        assert assembly == "MOV R3,R4"

        r3 = self.reg.get(3)
        assert r3 == 0o123456

        r4 = self.reg.get(4)
        assert r4 == 0o123456

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "1001"

    def test_MOVB_01(self):
        print('\ntest_MOVB_01')
        self.psw.set_psw(psw=0o777777)
        self.reg.set(3,0b1010011100101110)
        self.reg.set(4,0b0000000000000000)
        instruction = self.op(opcode=0o110000, modeS=0, regS=3, modeD=0, regD=4)   # mode 0 R1
        assert self.dopr.is_double_operand_SSDD(instruction)
        run, operand1, operand2, assembly = self.dopr.do_double_operand_SSDD(instruction)
        assert assembly == "MOVB R3,R4"

        r3 = self.reg.get(3)
        assert r3 == 0b1010011100101110

        r4 = self.reg.get(4)
        assert r4 == 0b0000000000101110

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0001"

    def test_MOVB_02(self):
        print('\ntest_MOVB_02')
        self.psw.set_psw(psw=0o777777)
        self.reg.set(3,0b1010011110101110)
        self.reg.set(4,0b0000000000000000)
        instruction = self.op(opcode=0o110000, modeS=0, regS=3, modeD=0, regD=4)   # mode 0 R1
        assert self.dopr.is_double_operand_SSDD(instruction)
        run, operand1, operand2, assembly = self.dopr.do_double_operand_SSDD(instruction)
        assert assembly == "MOVB R3,R4"

        r3 = self.reg.get(3)
        assert r3 == 0b1010011110101110

        r4 = self.reg.get(4)
        assert r4 == 0b0000000010101110

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "1001"

    def test_MOVB_03(self):
        print('\ntest_MOVB_03')
        self.psw.set_psw(psw=0o777777)
        self.reg.set(3,0b0000000010101110)
        self.reg.set(4,0b1010011100000000)
        instruction = self.op(opcode=0o110000, modeS=0, regS=3, modeD=0, regD=4)   # mode 0 R1
        assert self.dopr.is_double_operand_SSDD(instruction)
        run, operand1, operand2, assembly = self.dopr.do_double_operand_SSDD(instruction)
        assert assembly == "MOVB R3,R4"

        r3 = self.reg.get(3)
        assert r3 == 0b0000000010101110

        r4 = self.reg.get(4)
        assert r4 == 0b1010011110101110

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "1001"

    def test_MOVB_04(self):
        print('\ntest_MOVB_04')
        # 1165250 112512 MOVB (R5)+,@R2 from M9301-YA
        # MOVB (R5)+,@R2
        self.psw.set_psw(psw=0o777777)
        self.reg.set(2,0o000500)
        self.ram.write_word(0o000500, 0)
        assert self.ram.read_word(0o000500) == 0

        self.reg.set(5,0o165320)
        self.ram.write_word(0o165320, 0o177777)
        assert self.ram.read_word(self.reg.get(5)) == 0o177777

        instruction = 0o112512
        self.reg.set_pc(0o1165252)
        assert self.dopr.is_double_operand_SSDD(instruction)
        run, operand1, operand2, assembly = self.dopr.do_double_operand_SSDD(instruction)
        assert assembly == "MOVB (R5)+,@R2"
        assert self.reg.get(5) == 0o165321
        atr2  = self.ram.read_byte(self.reg.get(2))
        print(f'@R2={oct(atr2)} {bin(atr2)}')
        assert atr2 == 0o377
