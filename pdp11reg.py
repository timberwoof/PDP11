"""PDP11 Registers"""


class reg:
    def __init__(self):
        #print('initializing pdp11reg')
        self.bytemask = 0o377
        self.wordmask = 0o177777
        self.registermask = 0o07
        self.SP = 0o06  # R6 is rfequentluy referred to as the stack pointer
        self.PC = 0o07  # R7 is the program counter
        self.registers = [0, 0, 0, 0, 0, 0, 0, 0]  # R0 R1 R2 R3 R4 R5 R6 R7

    def get(self, register):
        """read a single register

        :param register:
        :return: register contents"""
        result = self.registers[register & self.registermask]
        #print(f'    get R{register}={oct(result)}')
        return result

    def set(self, register, value):
        """set a single register
        :param register:
        :param value:
        """
        #print(f'    set R{register}<-{oct(value)}')
        self.registers[register & self.registermask] = value & self.wordmask

    def get_pc(self):
        """get program counter

        :return: program counter"""
        return self.registers[self.PC]

    def inc_pc(self, whocalled=''):
        """increment progran counter by 2

        :return: new program counter"""
        self.registers[self.PC] = self.registers[self.PC] + 2
        #print(f'    inc_pc R7<-{oct(self.registers[self.PC])} {whocalled}')
        return self.registers[self.PC]

    def set_pc(self, value, whocalled=''):
        """set program counter to arbitrary value"""
        waspc =  self.registers[self.PC]
        newpc = value & self.wordmask
        self.registers[self.PC] = newpc
        #print(f'    setpc R7<-{oct(newpc)} {whocalled}')

    def set_pc_offset(self, offset, whocalled=''):
        """set program counter to 2x offset"""
        waspc = self.registers[self.PC]
        newpc = self.registers[self.PC] + 2 * (offset & self.bytemask)
        self.registers[self.PC] = newpc
        #print(f'    set_pc_offset R7<-{oct(newpc)} (was:{oct(waspc)}) {whocalled}')

    def get_sp(self):
        """get stack pointer

        :return: stack pointer"""
        return self.registers[self.SP]

    def set_sp(self, value, whocalled=''):
        """set stack pointer

        :return: new stack pointer"""
        wassp =  self.registers[self.PC]
        newsp = value & self.wordmask
        self.registers[self.PC] = newsp
        #print(f'{oct(wassp)} setpc {oct(newsp)}')
        return newsp

    def log_registers(self):
        """print all the registers in the log"""
        index = 0
        report = '    '
        for register in self.registers:
            report = report + f'R{index}: {oct(register)}  '
            index = index + 1
        print (report)