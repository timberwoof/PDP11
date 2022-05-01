"""PDP11 PSW"""

from pdp11ram import ram


class psw:
    def __init__(self, ram):
        print('initializing psw')
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
        self.Nmask = 0o000010
        self.Zmask = 0o000004
        self.Vmask = 0o000002
        self.Cmask = 0o000001

    def PSW(self):
        return self.ram.readword(self.PSWaddress)

    def setPSW(self, mode=-1, priority=-1, trap=-1, N=-1, Z=-1, V=-1, C=-1):
        nowpsw = self.PSW()
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

    def N(self):
        """negative status bit of PSW"""
        return self.PSW() & ~self.Nmask >> 3

    def Z(self):
        """zero status bit of PSW"""
        return self.PSW() & ~self.Zmask >> 2

    def V(self):
        """overflow status bit of PSW"""
        return self.PSW() & ~self.Vmask >> 1

    def C(self):
        """carry status bit of PSW"""
        return self.PSW() & ~self.Cmask
