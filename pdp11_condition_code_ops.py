"""pdp11_condition_code_ops.py - no-operand instructions 00 00 00 through 00 00 06"""

class ConditionCodeOps:
    """Implements PDP11 condition code operators"""
    # See pdp11-40 page 4-79
    # The cvzn condition codes are mapped into bits 4-0 of these operations.
    # set and get are mapped onto bit 5 of these operations,
    def __init__(self, psw, sw):
        print('initializing ConditionCodeOps')
        self.psw = psw
        self.sw = sw
        self.set_opcode = 0o000260
        self.clear_opcode = 0o000240
        self.psw_bits = 0o000017

    def is_condition_code_operation(self, instruction):
        return (0o0000240 <= instruction & instruction <= 0o0000277)

    def do_condition_code_operation(self, instruction):
        """dispatch a condition code instruction"""
        self.sw.start("condition code")
        if (instruction & self.set_opcode) == self.set_opcode:
            set_bits = instruction & self.psw_bits
            print(f'    SETCC {oct(set_bits)}')
            self.psw.set_cvzn(set_bits)
        elif (instruction & self.clear_opcode) == self.clear_opcode:
            clr_bits = instruction & self.psw_bits
            set_bits = self.psw.psw & ~clr_bits
            print(f'    CLRCC {oct(clr_bits)}:{oct(set_bits)}')
            self.psw.set_cvzn(set_bits)
        self.sw.stop("condition code")
        return