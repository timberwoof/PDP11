"""pdp11AddressMode - parameter preparation"""

from pdp11psw import psw
from pdp11Hardware import ram
from pdp11Hardware import reg

class am:
    def __init__(self, psw, ram, reg):
        print('initializing pdp11AddressMode')
        self.psw = psw
        self.ram = ram
        self.reg = reg

    def addressing_mode_get(self, B, mode_register):
        """copy the value from the location indicated by byte_register"""
        addressmode = (mode_register & 0o70) >> 3
        register = mode_register & 0o07

        print(f'    S addressing_mode_get {B} mode:{oct(addressmode)} reg:{oct(register)}')

        if B == 'B':
            ram_read = self.ram.read_byte
            increment = 1
            b = 'B'
        else:
            ram_read = self.ram.read_word
            increment = 2
            b = ''
        if register == 6 or register == 7:
            increment = 2

        if addressmode == 0:
            print(f'    S mode 0 Register: R{register}: register contains operand')
            operand = self.reg.get(register)
            print(f'    S mode 0 R{register} = operand:{oct(operand)}')
        elif addressmode == 1:
            print(f'    S mode 1 Register Deferred: (R{register}): register contains address of operand')
            address = self.reg.get(register)
            operand = ram_read(address)
            print(f'    S mode 1 @{oct(address)} = operand:{oct(operand)}')
        elif addressmode == 2:
            print(f'    S mode 2 Autoincrement: (R{register})+: register contains address of operand then incremented')
            address = self.reg.get(register)
            operand = ram_read(address)
            self.reg.set(register, self.reg.get(register) + increment)
            print(f'    S mode 2 R{register}={oct(address)} = operand:{oct(operand)}')
        elif addressmode == 3:  # autoincrement deferred
            print(f'    S mode 3 Autoincrement Deferred: @(R{register})+: register contains address of address of operand, then incremented')
            address = self.reg.get(register)
            self.reg.set(register, self.reg.get(register)+2)
            operand = ram_read(address)
            print(f'    S mode 3 @{oct(address)} = operand:{oct(operand)}')
        elif addressmode == 4:  # autodecrement direct
            print(f'    S mode 4 Autodecrement: -(R{register}): register is decremented, then contains address of operand')
            self.reg.set(register, self.reg.get(register) - increment)
            address = self.reg.get(register)
            operand = ram_read(address)
            print(f'    S mode 4 R{register}=@{oct(address)} = operand:{oct(operand)}')
        elif addressmode == 5:  # autodecrement deferred
            print(f'    S mode 5 Autodecrement Deferred: @-(R{register}): register is decremented, then contains address of address of operand')
            self.reg.set(register, self.reg.get(register)-2)
            pointer = self.reg.get(register)
            address = ram_read(pointer)
            operand = ram_read(address)
            print(f'    S mode 5 R{register}=@{oct(address)} = operand:{oct(operand)}')
        elif addressmode == 6:
            print(f'    S mode 6 Index: X(R{register}): value X is added to Register to produce address of operand')
            X = self.ram.read_word(self.reg.get_pc())
            address = self.reg.get(register) + X
            print(f'    S mode 6 X:{oct(X)} address:{oct(address)}')
            operand = ram_read(address)
            print(f'    S mode 6 R{register}=@{oct(address)} = operand:{oct(operand)}')
        elif addressmode == 7:  # index deferred
            print(f'    S mode 7 Index Deferred: @X(R{register}): value X is added to Register then used as address of address of operand')
            X = self.ram.read_word(self.reg.get_pc()+2)
            pointer = self.reg.get(register) + X
            address = ram_read(pointer)
            operand = ram_read(address)
            print(f'    S mode 7 R{register}=@{oct(address)} = operand:{oct(operand)}')

        if (addressmode == 6 or addressmode == 7) and register != 7:
            self.reg.set_pc(self.reg.get_pc()+2, "addressing_mode_get")

        return operand


    def addressing_mode_set(self, B, mode_register, result):
        """copy the result into the place indicated by mode_register

        Parameters:
            B: 'B' or ''
            mode_register: SS or DD
            result: what to store there
        """
        print(f'    D addressing_mode_set("{B}", {oct(mode_register)}, {oct(result)})')

        addressmode = (mode_register & 0o70) >> 3
        register = mode_register & 0o07
        print(f'    D addressing_mode_set {B} mode:{oct(addressmode)} reg:{register} result:{oct(result)}')

        if B == 'B':
            ram_read = self.ram.read_byte
            ram_write = self.ram.write_byte
            increment = 1
        else:
            ram_read = self.ram.read_word
            ram_write = self.ram.write_word
            increment = 2
        if register == 6 or register == 7:
            increment = 2

        if addressmode == 0:  # register direct
            print(f'    D mode 0 register: R{register}: register contains operand')
            self.reg.set(register, result)
            print(f'    D mode 0 R{register} = operand:{oct(result)}')
        if addressmode == 1:  # register deferred
            print(f'    D mode 1 register deferred: (R{register}): register contains address of operand')
            address = self.reg.get(register)
            ram_write(address, result)
            print(f'    D mode 1 @{oct(address)} = operand:{oct(result)}')
        elif addressmode == 2:  # autoincrement direct - R has address, then increment
            print(f'    D mode 2 autoincrement: (R{register})+: register contains address of operand then incremented')
            address = self.reg.get(register)
            self.reg.set(register, self.reg.get(register) + increment)
            ram_write(address, result)
            print(f'    D mode 2 R{register}={oct(address)} = operand:{oct(result)}')
        elif addressmode == 3:  # autoincrement deferred - R has handle, then increment
            print(f'    D mode 3 autoincrement deferred: @(R{register})+: register contains address of address of operand, then incremented')
            pointer = self.reg.get(register)
            self.reg.set(register, self.reg.get(register)+2)
            address = self.ram.read_word(pointer)
            ram_write(address, result)
            print(f'    D mode 3 @{oct(address)} = operand:{oct(result)}')
        elif addressmode == 4:  # autodecrement direct - decrement, then R has address
            print(f'    D mode 4 autodecrement: -(R{register}): register is decremented, then contains address of operand')
            self.reg.set(register, self.reg.get(register) - increment)
            address = self.reg.get(register)
            ram_write(address, result)
            print(f'    D mode 4 R{register}=@{oct(address)} = operand:{oct(result)}')
        elif addressmode == 5:  # autodecrement deferred - decrement, then R has handle
            print(f'    D mode 5 autodecrement deferred: @-(R{register}): register is decremented, then contains address of address of operand')
            self.reg.set(register, self.reg.get(register)-2)
            pointer = self.reg.get(register)
            address = self.ram.read_word(pointer)
            ram_write(address, result)
            print(f'    D mode 5 R{register}=@{oct(address)} = operand:{oct(result)}')
        elif addressmode == 6:  # index
            print(f'    D mode 6 index: X(R{register}): value X is added to Register to produce address of operand')
            nextword = self.ram.read_word(self.reg.get_pc())
            address = self.reg.get(register) + nextword
            print(f'    D mode 6 index R{register}={oct(address)} <- {oct(result)}')
            ram_write(address, result)
            print(f'    D mode 6 R{register}=@{oct(address)} = operand:{oct(result)}')
        elif addressmode == 7:  # index deferred
            print(f'    D mode 7 index deferred: @X(R{register}): value X is added to Register then used as address of address of operand')
            nextword = self.ram.read_word(self.reg.get_pc())
            address = self.reg.get(register) + nextword
            address = ram_read(address)
            ram_write(address, result)
            print(f'    D mode 7 R{register}=@{oct(address)} = operand:{oct(result)}')

        if (addressmode == 6 or addressmode == 7) and register != 7:
            self.reg.set_pc(self.reg.get_pc()+2, "addressing_mode_set")
