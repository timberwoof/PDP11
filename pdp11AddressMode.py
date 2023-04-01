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

        #print(f'    S addressing_mode_get {B} mode:{oct(addressmode)} reg:{oct(register)}')

        if B == 'B':
            ram_read = self.ram.read_byte
            increment = 2
            b = 'B'
        else:
            ram_read = self.ram.read_word
            increment = 2
            b = ''
        if register == 6 or register == 7:
            increment = 2

        if addressmode == 0:
            print(f'    S mode {addressmode} register: R{register}: register contains operand')
            operand = self.reg.get(register)
            print(f'    R{register} = operand:{oct(operand)}')
        elif addressmode == 1:
            print(f'    S mode {addressmode} register deferred: (R{register}): register contains address of operand')
            operandaddress = self.reg.get(register)
            operand = ram_read(operandaddress)
            print(f'    @{oct(operandaddress)} = operand:{oct(operand)}')
        elif addressmode == 2:
            print(f'    S mode {addressmode} autoincrement: (R{register})+: register contains address of operand then incremented')
            operandaddress = self.reg.get(register)
            operand = ram_read(operandaddress)
            self.reg.set(register, self.reg.get(register) + increment)
            print(f'    R{register}={oct(operandaddress)} = operand:{oct(operand)}')
        elif addressmode == 3:  # autoincrement deferred
            print(f'    S mode {addressmode} autoincrement deferred: @(R{register})+: register contains address of address of operand, then incremented')
            operandaddress = self.reg.get(register)
            self.reg.set(register, self.reg.get(register) + increment)
            operand = ram_read(operandaddress)
            print(f'    @{oct(operandaddress)} = operand:{oct(operand)}')
        elif addressmode == 4:  # autodecrement direct
            print(f'    S mode {addressmode} autodecrement: -(R{register}): register is decremented, then contains address of operand')
            self.reg.set(register, self.reg.get(register) - increment)
            operandaddress = self.reg.get(register)
            operand = ram_read(operandaddress)
            print(f'    R{register}=@{oct(operandaddress)} = operand:{oct(operand)}')
        elif addressmode == 5:  # autodecrement deferred
            print(f'    S mode {addressmode} autodecrement deferred: @-(R{register}): register is decremented, then contains address of address of operand')
            self.reg.set(register, self.reg.get(register) - increment)
            operandhandle = self.reg.get(register)
            operandaddress = ram_read(operandhandle)
            operand = ram_read(operandaddress)
            print(f'    R{register}=@{oct(operandaddress)} = operand:{oct(operand)}')
        elif addressmode == 6:
            print(f'    S mode {addressmode} index: X(R{register}): value X is added to Register to produce address of operand')
            operandaddress = self.reg.get(register) + ram_read(self.reg.get_pc() + 2)
            operand = ram_read(operandaddress)
            print(f'    R{register}=@{oct(operandaddress)} = operand:{oct(operand)}')
        elif addressmode == 7:  # index deferred
            print(f'    S mode {addressmode} index deferred: @X(R{register}): value X is added to Register then used as address of address of operand')
            operandaddress = self.reg.get(register)
            operandaddress = ram_read(operandaddress) + ram_read(self.reg.get_pc() + 2)
            operand = ram_read(operandaddress)
            print(f'    R{register}=@{oct(operandaddress)} = operand:{oct(operand)}')
        return operand


    def addressing_mode_set(self, B, mode_register, result):
        """copy the result into the place indicated by mode_register

        Parameters:
            B: 'B' or ''
            mode_register: SS or DD
            result: what to store there
        """
        #print(f'    D addressing_mode_set("{B}", {oct(mode_register)}, {oct(result)})')

        addressmode = (mode_register & 0o70) >> 3
        register = mode_register & 0o07
        #print(f'    D addressing_mode_set {B} mode:{oct(addressmode)} reg:{register} result:{oct(result)}')

        if B == 'B':
            ram_write = self.ram.write_byte
            increment = 2
        else:
            ram_write = self.ram.write_word
            increment = 2
        if register == 6 or register == 7:
            increment = 2

        if addressmode == 0:  # register direct
            print(f'    D mode {addressmode} register: R{register}: register contains operand')
            self.reg.set(register, result)
        if addressmode == 1:  # register deferred
            print(f'    D mode {addressmode} register deferred: (R{register}): register contains address of operand')
            operandaddress = self.reg.get(register)
            ram_write(operandaddress, result)
        elif addressmode == 2:  # autoincrement direct - R has address, then increment
            print(f'    D mode {addressmode} autoincrement: (R{register})+: register contains address of operand then incremented')
            operandaddress = self.reg.get(register)
            self.reg.set(register, self.reg.get(register) + increment)
            ram_write(operandaddress, result)
        elif addressmode == 3:  # autoincrement deferred - R has handle, then increment
            print(f'    D mode {addressmode} autoincrement deferred: @(R{register})+: register contains address of address of operand, then incremented')
            operandhandle = self.reg.get(register)
            self.reg.set(register, self.reg.get(register) + increment)
            operandaddress = self.ram.read_word(operandhandle)
            ram_write(operandaddress, result)
        elif addressmode == 4:  # autodecrement direct - decrement, then R has address
            print(f'    D mode {addressmode} autodecrement: -(R{register}): register is decremented, then contains address of operand')
            self.reg.set(register, self.reg.get(register) - increment)
            operandaddress = self.reg.get(register)
            ram_write(operandaddress, result)
        elif addressmode == 5:  # autodecrement deferred - decrement, then R has handle
            print(f'    D mode {addressmode} autodecrement deferred: @-(R{register}): register is decremented, then contains address of address of operand')
            self.reg.set(register, self.reg.get(register) - increment)
            operandhandle = self.reg.get(register)
            operandaddress = self.ram.read_word(operandhandle)
            ram_write(operandaddress, result)
            self.reg.inc_pc('addressing_mode_set 5')
        elif addressmode == 6:  # index
            print(f'    D mode {addressmode} index: X(R{register}): value X is added to Register to produce address of operand')
            operandaddress = self.reg.get(register)
            # print(f'index R{register}={oct(operandaddress)} <- {oct(result)}')
            ram_write(operandaddress, result)
            self.reg.inc_pc('addressing_mode_set 6')
        elif addressmode == 7:  # index deferred
            print(f'    D mode {addressmode} index deferred: @X(R{register}): value X is added to Register then used as address of address of operand')
            operandaddress = self.reg.get(register)
            ram_write(operandaddress, result)
            self.reg.inc_pc('addressing_mode_set 7')

