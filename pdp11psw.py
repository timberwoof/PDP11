"""PDP11 PSW"""


class psw:
    """PDP11 PSW"""

    def __init__(self, ram):
        """initialize PDP11 PSW"""
        #print('initializing pdp11psw')
        # 104000-104377 EMT (trap & interrupt)
        # 104400-104777 TRAP (trap & interrupt)

        # 013400 0 001 011 100 000 000 BCS (branch)
        # 16SSDD 1 110 *** *** *** *** subtract src from dst (double)
        # 06SSDD 0 110 *** *** *** *** ADD add src to dst (double)

        # PSW bit meanings and masks
        # 15 14 current mode        0o140000
        # 13 12 previous mode       0o030000
        # 7 6 5 priority            0o000340
        # 4 T trap                  0o000020
        # 3 N result was negative   0o000010
        # 2 Z result was zero       0o000004
        # 1 V overflow              0o000002
        # 0 C result had carry      0o000001
        self.ram = ram

        self.PSW_address = ram.topofmemory - 3
        self.c_mode_mask = 0o140000
        self.p_mode_mask = 0o030000
        self.mode_mask = 0o170000
        self.priority_mask = 0o000340
        self.trap_mask = 0o000020
        self.N_mask = 0o000010  # Negative
        self.Z_mask = 0o000004  # Zero
        self.V_mask = 0o000002  # Overflow
        self.C_mask = 0o000001  # Carry

        self.byte_mask = 0o000377
        self.word_mask = 0o177777

    def PSW(self):
        """return PSW"""
        return self.ram.read_word(self.PSW_address)

    def set_PSW(self, mode=-1, priority=-1, trap=-1, N=-1, Z=-1, V=-1, C=-1, PSW=-1):
        """set any PSW bits"""
        PSW_now = self.PSW()
        if mode > -1:
            oldmode = PSW_now & self.mode_mask
            PSW_now = PSW_now & ~self.c_mode_mask | mode << 14 | oldmode >> 2
        if priority > -1:
            PSW_now = PSW_now & ~self.priority_mask | priority << 5
        if trap > -1:
            PSW_now = PSW_now & ~self.trap_mask | trap << 4
        if N > -1:
            PSW_now = PSW_now & ~self.N_mask | N << 3
        if Z > -1:
            PSW_now = PSW_now & ~self.Z_mask | Z << 2
        if V > -1:
            PSW_now = PSW_now & ~self.V_mask | V << 1
        if C > -1:
            PSW_now = PSW_now & ~self.C_mask | C
        if PSW > -1:
            PSW_now = PSW
        self.ram.write_word(self.PSW_address, PSW_now)

    def N(self):
        """negative status bit of PSW"""
        return self.PSW() & ~self.N_mask >> 3

    def Z(self):
        """zero status bit of PSW"""
        return self.PSW() & ~self.Z_mask >> 2

    def V(self):
        """overflow status bit of PSW"""
        return self.PSW() & ~self.V_mask >> 1

    def C(self):
        """carry status bit of PSW"""
        return self.PSW() & ~self.C_mask

    def addb(self, b1, b2):
        """add byte, limit to 8 bits, set PSW"""
        result = b1 + b2
        if result > result & self.byte_mask:
            self.set_PSW(V=1)
        if result == 0:
            self.set_PSW(Z=1)
        result = result & self.byte_mask
        return result

    def subb(self, b1, b2):
        """subtract bytes b1 - b2, limit to 8 bits, set PSW"""
        result = b1 - b2
        if result < 0:
            self.set_PSW(N=1)
        result = result & self.byte_mask
        return result

    def addw(self, b1, b2):
        """add words, limit to 16 bits, set PSW"""
        result = b1 + b2
        if result > result & self.word_mask:
            self.set_PSW(V=1)
        if result == 0:
            self.set_PSW(Z=1)
        result = result & self.word_mask
        return result

    def subw(self, b1, b2):
        """subtract words b1 - b2, limit to 16 bits, set PSW"""
        result = b1 - b2
        if result < 0:
            self.set_PSW(N=1)
        result = result & self.word_mask
        return result
