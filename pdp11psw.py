"""PDP11 PSW"""


class Psw:
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

        self.PSWaddress = ram.topofmemory - 3
        self.cmodemask = 0o140000
        self.pmoremask = 0o030000
        self.modemask = 0o170000
        self.prioritymask = 0o000340
        self.trapmask = 0o000020
        self.Nmask = 0o000010  # Negative
        self.Zmask = 0o000004  # Zero
        self.Vmask = 0o000002  # Overflow
        self.Cmask = 0o000001  # Carry

        self.bytemask = 0o377
        self.wordmask = 0o177777

    def psw(self):
        """return PSW"""
        return self.ram.readword(self.PSWaddress)

    def setpsw(self, mode=-1, priority=-1, trap=-1, N=-1, Z=-1, V=-1, C=-1):
        """set any PSW bits"""
        nowpsw = self.psw()
        if mode > -1:
            oldmode = nowpsw & self.modemask
            nowpsw = nowpsw & ~self.cmodemask | mode << 14 | oldmode >> 2
        if priority > -1:
            nowpsw = nowpsw & ~self.prioritymask | priority << 5
        if trap > -1:
            nowpsw = nowpsw & ~self.trapmask | trap << 4
        if N > -1:
            nowpsw = nowpsw & ~self.Nmask | N << 3
        if Z > -1:
            nowpsw = nowpsw & ~self.Zmask | Z << 2
        if V > -1:
            nowpsw = nowpsw & ~self.Vmask | V << 1
        if C > -1:
            nowpsw = nowpsw & ~self.Cmask | C
        self.ram.writeword(self.PSWaddress, nowpsw)

    def n(self):
        """negative status bit of PSW"""
        return self.psw() & ~self.Nmask >> 3

    def z(self):
        """zero status bit of PSW"""
        return self.psw() & ~self.Zmask >> 2

    def v(self):
        """overflow status bit of PSW"""
        return self.psw() & ~self.Vmask >> 1

    def c(self):
        """carry status bit of PSW"""
        return self.psw() & ~self.Cmask

    def addb(self, b1, b2):
        """add byte, limit to 8 bits, set PSW"""
        result = b1 + b2
        if result > result & self.bytemask:
            self.setpsw(V=1)
        if result == 0:
            self.setpsw(Z=1)
        result = result & self.bytemask
        return result

    def subb(self, b1, b2):
        """subtract bytes b1 - b2, limit to 8 bits, set PSW"""
        result = b1 - b2
        if result < 0:
            self.setpsw(N=1)
        result = result & self.bytemask
        return result

    def addw(self, b1, b2):
        """add words, limit to 16 bits, set PSW"""
        result = b1 + b2
        if result > result & self.wordmask:
            self.setpsw(V=1)
        if result == 0:
            self.setpsw(Z=1)
        result = result & self.wordmask
        return result

    def subw(self, b1, b2):
        """subtract words b1 - b2, limit to 16 bits, set PSW"""
        result = b1 - b2
        if result < 0:
            self.setpsw(N=1)
        result = result & self.wordmask
        return result
