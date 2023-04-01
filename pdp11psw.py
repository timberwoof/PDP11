"""PDP11 Processor Status Word"""

from pdp11ram import ram

# masks for accessing words and bytes
mask_byte = 0o000377
mask_word = 0o177777
mask_byte_msb = 0o000200
mask_word_msb = 0o100000

class psw:
    """PDP11 PSW"""

    def __init__(self, ram):
        """initialize PDP11 PSW"""
        print('initializing pdp11psw')
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

    def set_PSW(self, mode=-1, priority=-1, trap=-1, N=-1, Z=-1, V=-1, C=-1, PSW=-1):
        """set processor status word by optional parameter

        :param mode:
        :param priority:
        :param trap:
        :param N:
        :param Z:
        :param V:
        :param C:
        :param PSW:
        :return:
        """
        print(f'set_PSW mode:{oct(mode)} Priority:{oct(priority)} {trap} NZVC: {N} {Z} {V} {C}  PSW:{oct(PSW)}  ')
        new_PSW = PSW
        PSW = self.ram.get_PSW()
        if mode > -1:
            oldmode = (PSW & self.mode_mask)
            PSW = (PSW & ~self.c_mode_mask) | (mode << 14) | (oldmode >> 2)
        if priority > -1:
            PSW = (PSW & ~self.priority_mask) | (priority << 5)
        if trap > -1:
            PSW = (PSW & ~self.trap_mask) | (trap << 4)
        if N > -1:
            PSW = (PSW & ~self.N_mask) | (N << 3)
        if Z > -1:
            print(f'PSW:{oct(PSW)}    self.Z_mask:{oct(self.Z_mask)}    ~self.Z_mask:{oct(~self.Z_mask)}   Z:{Z}')
            print(f'PSW & ~self.Z_mask:{oct(PSW & ~self.Z_mask)}    Z<<2:{oct(Z<<2)}')
            PSW = (PSW & ~self.Z_mask) | (Z << 2)
            print(f'new_PSW:{oct(PSW)}')
        if V > -1:
            PSW = (PSW & ~self.V_mask) | (V << 1)
        if C > -1:
            PSW = (PSW & ~self.C_mask) | C
        if new_PSW > -1:
            PSW = new_PSW
        self.ram.set_PSW(PSW)

    def set_condition_codes(self, value, B, pattern):
        """set condition codes based on value

        :param value: value to test
        :param B: "B" or "" for Byte or Word
        :param pattern: string matching DEC specification

        pattern looks like the Status Word Condition Codes in the DEC manual.
        Positionally NZVC for Negative, Zero, Overflor, Carry.
        * = conditionally set; - = not affected; 0 = cleared; 1 = set.
        Example: "**0-"
        """
        # set up some masks based on whether this is for Word or Byte
        if B == "B":
            n_mask = mask_byte_msb
            z_mask = mask_byte
            v_mask = mask_byte < 1 & ~mask_byte
            c_mask = mask_byte < 1 & ~mask_byte
        else:
            n_mask = mask_word_msb
            z_mask = mask_word
            v_mask = mask_word < 1 & ~mask_word
            c_mask = mask_word < 1 & ~mask_word  # *** I dion't know how to test for this

        # set unaffected values
        N = -1
        Z = -1
        V = -1
        C = -1

        codenames = "NZVC"

        # check each of the 4 characters
        for i in range(0,4):
            code = pattern[i]
            codename = codenames[i] # get the letter for convenience
            # check for explicit setting
            if code == "0" or code == "1":
                setting = int(code)
                if codename == "N":
                    N = setting
                elif codename == "Z":
                    Z = setting
                elif codename == "V":
                    V = setting
                elif codename == "C":
                    C = setting
            # check for conditional value
            elif code == "*":
                if codename == "N":
                    if (value & n_mask) > 0:
                        N = 1
                    else:
                        N = 0
                elif codename == "Z":
                    if (value & z_mask) == 0:
                        Z = 1
                    else:
                        Z = 0
                elif codename == "V":
                    if (value & v_mask) == v_mask:
                        V = 1
                    else:
                        V = 0
                elif codename == "C":
                    if (value & c_mask) == c_mask:  # *** I'm not sure about this
                        C = 1
                    else:
                        C = 0

        print(f'    set NZVC: {N} {Z} {V} {C}')
        self.set_PSW(N=N, Z=Z, V=V, C=C)
        print(f'    did set NZVC: {self.N()} {self.Z()} {self.V()} {self.C()}')

    def N(self):
        """negative status bit of PSW"""
        return (self.ram.get_PSW() & self.N_mask) >> 3

    def Z(self):
        """zero status bit of PSW"""
        return (self.ram.get_PSW() & self.Z_mask) >> 2

    def V(self):
        """overflow status bit of PSW"""
        return (self.ram.get_PSW() & self.V_mask) >> 1

    def C(self):
        """carry status bit of PSW"""
        return (self.ram.get_PSW() & self.C_mask)

    def addb(self, b1, b2):
        """add byte, limit to 8 bits, set PSW"""
        result = b1 + b2
        if result > result & self.byte_mask:
            self.ram.set_PSW(V=1)
        if result == 0:
            self.ram.set_PSW(Z=1)
        result = result & self.byte_mask
        return result

    def subb(self, b1, b2):
        """subtract bytes b1 - b2, limit to 8 bits, set PSW"""
        result = b1 - b2
        if result < 0:
            self.ram.set_PSW(N=1)
        result = result & self.byte_mask
        return result

    def addw(self, b1, b2):
        """add words, limit to 16 bits, set PSW"""
        result = b1 + b2
        if result > result & self.word_mask:
            self.ram.set_PSW(V=1)
        if result == 0:
            self.ram.set_PSW(Z=1)
        result = result & self.word_mask
        return result

    def subw(self, b1, b2):
        """subtract words b1 - b2, limit to 16 bits, set PSW"""
        result = b1 - b2
        if result < 0:
            self.ram.set_PSW(N=1)
        result = result & self.word_mask
        return result
