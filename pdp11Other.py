"""pdp11other - other instructions"""

from pdp11psw import psw
from pdp11ram import ram
from pdp11reg import reg
from pdp11AddressMode import am

# masks for accessing words and bytes
mask_byte = 0o000377
mask_word = 0o177777
mask_word_msb = 0o100000
mask_byte_msb = 0o000200

class other:
    def __init__(self, psw, ram, reg):
        print('initializing pdp11other')
        self.psw = psw
        self.ram = ram
        self.reg = reg
        self.am = am(psw, ram, reg)

    # ****************************************************
    # stack methods for use by instructions
    # ****************************************************
    def pushstack(self, value):
        """push the value onto the stack

        decrement stack pointer, write value to that address
        """
        stack = self.reg.get_sp() - 2
        self.reg.set_sp(stack)
        ram.self.write_word(stack, ram.self.value)

    # ****************************************************
    # Other instructions
    # ****************************************************
    def RTS(self, instruction):
        """00 20 0R RTS return from subroutine 00020R 4-60"""
        print(f'{oct(self.reg.get_pc()-2)} {oct(instruction)} RTS unimplemented')

    def JSR(self, instruction):
        """00 4R DD JSR jump to subroutine

        |  004RDD 4-58
        |  pushstack(reg)
        |  reg <- PC+2
        |  PC <- (dst)
        """
        print(f'{oct(self.reg.get_pc()-2)} {oct(instruction)} JSR')
        pushstack(ram.self.read_word(register))
        self.reg.set(register, self.reg.inc_pc('JSR'))
        self.reg.set_pc(dest, "JSR")

    def MARK(instruction):
        """00 64 NN mark 46-1"""
        print(f'{oct(self.reg.get_pc()-2)} {oct(instruction)} MARK unimplemented')

    def MFPI(instruction):
        """00 65 SS move from previous instruction space 4-77"""
        print(f'{oct(self.reg.get_pc()-2)} {oct(instruction)} MFPI unimplemented')

    def MTPI(instruction, dest, operand):
        """00 66 DD move to previous instruction space 4-78"""
        print(f'{oct(self.reg.get_pc()-2)} {oct(instruction)} MTPI unimplemented')


    def other_opcode(self, instruction):
        """dispatch a leftover opcode"""
        # parameter: opcode of form that doesn't fit the rest
        print(f'{oct(self.reg.get_pc()-2)} {oct(instruction)} other_opcode')
        result = True
        if instruction & 0o177000 == 0o002000:
            self.RTS(instruction)
        elif instruction & 0o177000 == 0o004000:
            self.JSR(instruction)
        elif instruction & 0o177700 == 0o006400:
            self.MARK(instruction)
        elif instruction & 0o177700 == 0o006500:
            self.MFPI(instruction)
        elif instruction & 0o177700 == 0o006600:
            self.MTPI(instruction)
        else:
            print(f'{oct(instruction)} is an unknown instruction')
            self.reg.set_pc(0o0, "other_opcode")
            result = False
        return result
