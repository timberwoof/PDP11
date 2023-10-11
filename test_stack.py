"""test_stack"""
from pdp11_hardware import Registers as reg
from pdp11_hardware import Ram
from pdp11_hardware import PSW
from pdp11_hardware import Stack
from pdp11_hardware import AddressModes as am
from pdp11_single_operand_ops import SingleOperandOps as sopr
from pdp11_double_operand_ops import DoubleOperandOps as dopr
from pdp11_other_ops import OtherOps as other
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
    other = other(reg, ram, psw, am, sw)

    def test_jsr_R5(self):
        # pdp11-40 4-58
        print ('test_jsr_R5')

        R7 = 7
        R6 = 6
        R5 = 5
        mode1 = 1
        mode2 = 2
        mode3 = 3
        mode6 = 6

        # 00 4R DD: JSR jump to subroutine
        # *** I do not know what paremeters are given to JSR
        # *** I do not know the address mode that is used
        # *** JSR is typically used
        # M9301_YA:
        # 165334 012701	TST7:	MOV	#JSRT, R1
        # 165344 004311		JSR	R3, @R1  ; mode 1
        # 165350 004361		JSR	R3, 4(R1) ; mode 6
        # 165352 000004
        # 165356 005723	JSRT:	TST	(R3)+ ; R1
        # 165362 021605		CMP	@SP, R5 ; 4(R1)
        # spcinv.mac:
        # JSR PC,ADDRESS

        # from pdp11-40 4-59
        # arbitrary values for test:
        PC = 0o01000
        SP = 0o02000
        SBR = 0o03000
        Data0 = 0o01234
        Data1 = 0o12345

        self.reg.set(R7, PC)
        self.reg.set(R6, SP)
        self.ram.write_word(SP, Data0)
        self.reg.set(R5, Data1)
        self.ram.write_word(PC+2, SBR)

        opcode = 0o04000 | (R5 << 6) | (mode1 << 3) | R7
        print (f'opcode:{oct(opcode)}')
        self.ram.write_word(PC, opcode)

        assert self.other.is_other_op(opcode)
        print ('is other opcode')

        reg7 = self.reg.get(R7)
        reg6 = self.reg.get(R6)
        reg5 = self.reg.get(R5)
        top = self.ram.read_word(reg6)
        self.reg.set(R7, PC+2)
        print(f'before R7:{oct(reg7)} R6:{oct(reg6)} R5:{oct(reg5)} top:{oct(top)} ')

        self.other.other_opcode(opcode)

        reg7 = self.reg.get(R7)
        reg6 = self.reg.get(R6)
        reg5 = self.reg.get(R5)
        top = self.ram.read_word(reg6)
        print(f'after R7:{oct(reg7)} R6:{oct(reg6)} R5:{oct(reg5)} top:{oct(top)} ')

        #assert actual == expected
        assert reg7 == SBR
        assert reg6 == SP - 2
        assert reg5 == PC + 2
        assert top == Data1

    def test_rts(self):
        print ('test_rts')

    def test_mark(self):
        print ('test_mark')

    def test_mtps(self):
        print ('test_mtps')