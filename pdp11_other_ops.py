"""pdp11other - other instructions"""

from pdp11_hardware import Stack

# masks for accessing words and bytes
MASK_BYTE = 0o000377
MASK_WORD = 0o177777
MASK_WORD_MSB = 0o100000
MASK_BYTE_MSB = 0o000200

class OtherOps:
    """Implements the remainder of PDP11 instructions"""
    def __init__(self, reg, ram, psw, am ):
        print('initializing otherOps')
        self.reg = reg
        self.ram = ram
        self.psw = psw
        self.am = am
        self.stack = Stack(reg, ram, psw)


    # ****************************************************
    # Other instructions
    # ****************************************************
    def JSR(self, instruction):
        """00 4R DD: JSR jump to subroutine 4-58

        |  pushstack(reg)
        |  reg <- PC+2
        |  PC <- (dst)
        """
        R = instruction & 0o000700 >> 6
        DD = instruction & 0o000077
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} JSR r{R} {oct(DD)}')
        tmp = DD
        self.stack.push(self.reg.get(R))
        self.reg.set(self.reg.get_pc())
        self.reg.set_pc(tmp, "JSR")

    def RTS(self, instruction):
        """00 20 0R: RTS return from subroutine 4-60
        
        | PC <- reg
        | reg <- (SP)^
        """
        R = instruction & 0o000007
        print(f'    {oct(self.reg.get_pc())} {oct(instruction)} RTS r{R}')
        self.reg.set_pc(self.reg.get(R), "RTS")
        self.reg.set(R, self.stack.pop())

    def MARK(self, instruction):
        """00 64 NN mark 46-1"""
        # *** unimplemented
        print(f'    MARK {oct(instruction)} unimplemented')

    def MFPI(self, instruction):
        """00 65 SS move from previous instruction space 4-77"""
        # *** unimplemented
        print(f'    MFPI {oct(instruction)} unimplemented')

    def MTPI(self, instruction):
        """00 66 DD move to previous instruction space 4-78"""
        # *** unimplemented
        print(f'    MTPI {oct(instruction)} unimplemented')

    def other_opcode(self, instruction):
        """dispatch a leftover opcode"""
        # parameter: opcode of form that doesn't fit the rest
        print(f'{oct(self.reg.get_pc())} {oct(instruction)} other_opcode')
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
            return False
        return True
