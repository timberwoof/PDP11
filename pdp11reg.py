"""PDP11 Registers"""


class reg:
    def __init__(self):
        #print('initializing pdp11reg')
        self.bytemask = 0o377
        self.wordmask = 0o177777
        self.registers = [0, 0, 0, 0, 0, 0, 0, 0]  # R0 R1 R2 R3 R4 R5 R6 R7
        self.pc = 0o07
        self.registermask = 0o07

    def get(self, register):
        """read a single register

        returns: register contents"""
        return self.registers[register & self.registermask]

    def set(self, register, value):
        """set a single register"""
        self.registers[register & self.registermask] = value & self.wordmask

    def getpc(self):
        """get program counter

        returns: program counter"""
        return self.registers[self.pc]

    def incpc(self):
        """increment progran counter by 2

        returns: new program counter"""
        self.registers[self.pc] = self.registers[self.pc] + 2
        return self.registers[self.pc]

    def setpc(self, value):
        """set program counter to arbitrary value"""
        waspc =  self.registers[self.pc]
        newpc = value & self.wordmask
        self.registers[self.pc] = newpc
        #print(f'{oct(waspc)} setpc {oct(newpc)}')

    def setpcoffset(self, offset):
        """set program counter to an offset

        returns: new program counter"""
        waspc =  reg.getpc()
        self.registers[self.pc] = waspc + 2 * (offset & self.wordmask)
        newpc = self.registers[self.pc]
        #print(f'{oct(waspc)} setpc {oct(newpc)}')
        return newpc

    def getsp(self):
        """get stack pointer

        returns: stack pointer"""
        return self.registers[self.sp]

    def setsp(self, value):
        """set stack pointer

        returns: new stack pointer"""
        wassp =  self.registers[self.pc]
        newsp = value & self.wordmask
        self.registers[self.pc] = newsp
        #print(f'{oct(wassp)} setpc {oct(newsp)}')
        return newsp