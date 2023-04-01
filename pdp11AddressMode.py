"""pdp11AddressMode - parameter preparation"""

from pdp11psw import psw
from pdp11ram import ram
from pdp11reg import reg

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

        print(f'    addressing_mode_get {B} mode:{oct(addressmode)} reg:{oct(register)}')

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
            print('    register: Rn: register contains operand')
            operand = self.reg.get(register)
            print(f'    R{oct(register)} = operand:{oct(operand)}')
        elif addressmode == 1:
            print('    register deferred: @Rn or (Rn): register contains address of operand')
            operandaddress = self.reg.get(register)
            operand = ram_read(operandaddress)
            print(f'    {oct(operandaddress)} = operand:{oct(operand)}')
        elif addressmode == 2:
            print('    autoincrement: (Rn)+: register contains address of operand then incremented')
            operandaddress = self.reg.get(register)
            operand = ram_read(operandaddress)
            if register != 7:
                self.reg.set(register, self.reg.get(register) + increment)
                # increment 1 for B and 2 for W
            print(f'    R{register}={oct(operandaddress)} = operand:{oct(operand)}')
        elif addressmode == 3:  # autoincrement deferred
            print(
                '    autoincrement deferred: @(Rn)+: register contains address of address of operand, then incremented')
            operandaddress = self.reg.get(register)
            operand = ram_read(operandaddress)
            if register != 7:
                self.reg.set(register, self.reg.get(register) + 2)
                # increment always by 2
            print(f'    {oct(operandaddress)} = operand:{oct(operand)}')
        elif addressmode == 4:  # autodecrement direct
            print('    autodecrement: -(Rn): register is decremented, then contains address of operand')
            self.reg.set(register, self.reg.get(register) - increment)
            # decrement 1 for B and 2 for W
            operandaddress = self.reg.get(register)
            operand = ram_read(operandaddress)
            print(f'    R{register}={oct(operandaddress)} = operand:{oct(operand)}')
        elif addressmode == 5:  # autodecrement deferred
            print(
                '    autodecrement deferred: @-(Rn): register is decremented, then contains address of address of operand')
            self.reg.set(register, self.reg.get(register) - 2)
            # decrement always by 2
            operandaddress = self.reg.get(register)
            operand = ram_read(operandaddress)
            print(f'    R{register}={oct(operandaddress)} = operand:{oct(operand)}')
        elif addressmode == 6:
            print('    index: X(Rn): value X is added to Register to produce address of operand')
            operandaddress = self.reg.get(register) + ram_read(self.reg.get_pc() + 2)
            operand = ram_read(operandaddress)
            print(f'    R{register}={oct(operandaddress)} = operand:{oct(operand)}')
        elif addressmode == 7:  # index deferred
            print('    index deferred: @X(Rn): value X is added to Register then used as address of address of operand')
            operandaddress = self.reg.get(register)
            operandaddress = ram_read(operandaddress) + ram_read(self.reg.get_pc() + 2)
            operand = ram_read(operandaddress)
            print(f'    R{register}={oct(operandaddress)} = operand:{oct(operand)}')
        return operand


    def addressing_mode_set(self, B, mode_register, result):
        """copy the result into the place indicated by mode_register

        Parameters:
            B: 'B' or ''
            mode_register: SS or DD
            result: what to store there
        """
        print(f'    addressing_mode_set("{B}", {oct(mode_register)}, {oct(result)})')

        addressmode = (mode_register & 0o70) >> 3
        register = mode_register & 0o07
        print(f'    addressing_mode_set {B} mode:{oct(addressmode)} reg:{register} result:{oct(result)}')

        if B == 'B':
            ram_write = self.ram.write_byte
            increment = 1
        else:
            ram_write = self.ram.write_word
            increment = 2
        if register == 6 or register == 7:
            increment = 2

        if addressmode == 0:  # register direct
            # print('    register direct')
            self.reg.set(register, result)
        if addressmode == 1:  # register deferred
            # print('    register deferred')
            operandaddress = self.reg.get(register)
            ram_write(operandaddress, result)
        elif addressmode == 2:  # autoincrement direct
            # print('    autoincrement direct')
            operandaddress = self.reg.get(register)
            ram_write(operandaddress, result)
        elif addressmode == 3:  # autoincrement deferred
            # print('    autoincrement deferred')
            operandaddress = self.reg.get(register)
            ram_write(operandaddress, result)
            self.reg.set(register, self.reg.get(register) + 2)
        elif addressmode == 4:  # autodecrement direct
            # print('    autodecrement direct')
            operandaddress = self.reg.get(register)
            ram_write(operandaddress, result)
        elif addressmode == 5:  # autodecrement deferred
            # print('    autodecrement deferred')
            operandaddress = self.reg.get(register)
            ram_write(operandaddress, result)
            self.reg.inc_pc('ams6')
        elif addressmode == 6:  # index
            operandaddress = self.reg.get(register)
            # print(f'index R{register}={oct(operandaddress)} <- {oct(result)}')
            ram_write(operandaddress, result)
            self.reg.inc_pc('ams6')
        elif addressmode == 7:  # index deferred
            # print('    index deferred')
            operandaddress = self.reg.get(register)
            ram_write(operandaddress, result)
            self.reg.inc_pc('ams7')

