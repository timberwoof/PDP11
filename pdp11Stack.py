"""pdp11stac"""

from pdp11psw import psw
from pdp11ram import ram
from pdp11reg import reg

class stack:
    def __init__(self, psw, ram, reg):
        print('initializing pdp11Stack')
        self.psw = psw
        self.ram = ram
        self.reg = reg

        # ****************************************************
        # stack methods for use by instructions
        # ****************************************************
        def push(self, value):
            """push the value onto the stack

            decrement stack pointer, write value to that address
            """
            stack = self.reg.get_sp() - 2
            self.reg.set_sp(stack)
            self.ram.write_word(stack, self.ram.value)

        def pop(self):
            """pop value off the stack

            get value from stack pointer, increment stack pointer"""
            stack = self.reg.get_sp()
            result = self.ram.read_word(stack)
            self.reg.set_sp(stack + 2)
            return result

