"""PDP11 Registers"""


class reg:
    def __init__(self):
        print('initializing pdp11reg')
        self.bytemask = 0o377
        self.wordmask = 0o177777
        self.registers = [0, 0, 0, 0, 0, 0, 0, 0]  # R0 R1 R2 R3 R4 R5 R6 R7
        self.pc = 0o07
        self.registermask = 0o07

    def getpc(self):
        """get program counter"""
        return self.registers[self.pc]

    def setpc(self, v):
        """update program counter"""
        waspc =  self.registers[self.pc]
        newpc = v & self.wordmask
        self.registers[self.pc] = newpc
        print(f'{oct(waspc)} setpc {oct(newpc)}')

    def incpc(self):
        """increment progran counter by 2"""
        self.registers[self.pc] = self.registers[self.pc] + 2

    def get(self, r):
        """read a single register"""
        return self.registers[r & self.registermask]

    def set(self, r, v):
        """set a single register"""
        self.registers[r & self.registermask] = v & self.wordmask
