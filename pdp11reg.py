"""PDP11 Registers"""
registers = [0, 0, 0, 0, 0, 0, 0, 0]  # R0 R1 R2 R3 R4 R5 R6 R7


class reg:
    def __init__(self):
        print('initializing registers')

    def getpc(self):
        return registers[7]

    def setpc(self, v):
        waspc =  registers[0o7]
        newpc = v & 0o177777
        registers[0o7] = newpc
        print(f'{oct(waspc)} setpc {oct(newpc)}')

    def incpc(self):
        registers[0o7] = registers[0o7] + 2

    def get(self, r):
        return registers[r & 0o7]

    def set(self, r, v):
        registers[r & 0o7] = v & 0o377
