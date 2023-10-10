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

    def test_jsr(self):
        # pdp11-40 4-58
        print ('test_jsr')

        PC = 0o01000
        SP = 0o02000
        SBR = 0o03000
        N0 = 0o01234
        N1 = 0o12345

        self.reg.set(7, PC)
        self.reg.set(6, SP)
        self.reg.set(5, N1)
        self.ram.write_word(SP, N0)
        self.ram.write_word(PC+2, SBR)

        R7 = self.reg.get(7)
        R6 = self.reg.get(6)
        R5 = self.reg.get(5)
        top = self.ram.read_word(R6)
        print(f'R7:{oct(R7)} R6:{oct(R6)} R5:{oct(R5)} top:{oct(top)} ')

        # 00 4R DD: JSR jump to subroutine
        # in other_ops but shound be in single-operand instructions
        opcode = 0o04000 | (5 << 6) | (3 << 3) | 7  # 0o004537
        print (f'opcode:{oct(opcode)}')
        self.ram.write_word(PC, opcode)

        assert self.other.is_other_op(opcode)
        print ('is other opcode')

        self.other.other_opcode(opcode)

        R7 = self.reg.get(7)
        R6 = self.reg.get(6)
        R5 = self.reg.get(5)
        top = self.ram.read_word(R6)
        print(f'R7:{oct(R7)} R6:{oct(R6)} R5:{oct(R5)} top:{oct(top)} ')

        assert R7 == SBR
        assert R6 == SP - 2
        assert R5 == PC + 2
        assert top == N1

        # Needs to add mode and second register
        # It's a lot like JMP except it needs an R and a DD

    def test_rts(self):
        print ('test_rts')

    def test_mark(self):
        print ('test_mark')

    def test_mtps(self):
        print ('test_mtps')