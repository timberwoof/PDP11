"""PDP11 Registers"""


class reg:
    def __init__(self):
        #print('initializing pdp11reg')
        self.bytemask = 0o377
        self.wordmask = 0o177777
        self.registers = [0, 0, 0, 0, 0, 0, 0, 0]  # R0 R1 R2 R3 R4 R5 R6 R7
        self.sp = 0o06
        self.pc = 0o07
        self.registermask = 0o07

    def get(self, register):
        """read a single register

        returns: register contents"""
        result = self.registers[register & self.registermask]
        #print(f'    get R{register}={oct(result)}')
        return result

    def set(self, register, value):
        """set a single register"""
        #print(f'    set R{register}<-{oct(value)}')
        self.registers[register & self.registermask] = value & self.wordmask

    def getpc(self):
        """get program counter

        returns: program counter"""
        return self.registers[self.pc]

    def incpc(self, whocalled=''):
        """increment progran counter by 2

        returns: new program counter"""
        self.registers[self.pc] = self.registers[self.pc] + 2
        #print(f'    incpc R7<-{oct(self.registers[self.pc])} {whocalled}')
        return self.registers[self.pc]

    def setpc(self, value, whocalled=''):
        """set program counter to arbitrary value"""
        waspc =  self.registers[self.pc]
        newpc = value & self.wordmask
        self.registers[self.pc] = newpc
        #print(f'    setpc R7<-{oct(newpc)} {whocalled}')

    def setpcoffset(self, offset, whocalled=''):
        """set program counter to an offset

        returns: new program counter"""
        waspc =  reg.getpc()
        self.registers[self.pc] = waspc + 2 * (offset & self.wordmask)
        newpc = self.registers[self.pc]
        #print(f'    setpcoffset R7<-{oct(newpc)} (was:{oct(waspc)}) {whocalled}')
        return newpc

    def getsp(self):
        """get stack pointer

        returns: stack pointer"""
        return self.registers[self.sp]

    def setsp(self, value, whocalled=''):
        """set stack pointer

        returns: new stack pointer"""
        wassp =  self.registers[self.pc]
        newsp = value & self.wordmask
        self.registers[self.pc] = newsp
        #print(f'{oct(wassp)} setpc {oct(newsp)}')
        return newsp

    def logRegisters(self):
        index = 0
        report = ''
        for register in self.registers:
            report = report + f'R{index}: {oct(register)}  '
            index = index + 1
        print (report)