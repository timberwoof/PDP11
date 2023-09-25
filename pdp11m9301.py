"""PDP11 M9301 Boot Rom"""
from pdp11Hardware import ram

class m9301:
    def __init__(self, reg, ram, boot):
        print('initializing M9301')
        # the boot rom file contains
        # ; Entry point -- Console emulator w/ CPU Diagnostics
        # ;  DIP switches xx11111111  (173000)
        #
        # 173000 000574		BR	GODIAG
        #
        # ; Entry point -- Diagnostics, then emulate power-fail restart trap through 24
        # ;  DIP switches xx11111110  (173002)
        #
        # 173002 000573		BR	GODIAG

        m9301StartAddress = 0o173000
        switch81_1 = True # low rom enable ON = True. Not used here.
        switch81_2 = True # power up reboot enable ON = True
        # if this is off then  processor will trap to location 24 on startup.
        # if this is on then processor will trap to a selectable address.
        switch81_3 = 0o0400
        switch81_4 = 0o0200
        switch81_5 = 0o0100
        switch81_6 = 0o0040
        switch81_7 = 0o0020
        switch81_8 = 0o0010
        switch81_9 = 0o0004
        switch81_10 = 0o0002
        # include the switches you want to have '1' digits.
        # Where the DEC manual says to have a switch OFF, include it
        # Thus none of the switches results in CPU Diagnostics with Console Emulator:
        # PC = m9301StartAddress
        # console boot switch causes M9301 to be activated
        # causes normal boot-up sequence
        # new PC address is logical OR of 0o173000 and selected microswitches
        # To set CPU diag. Boot RK11:
        # PC = m9301StartAddress + switch81_3 + switch81_6
        if switch81_2:
            # Load boot rom image into RAM (165000 - 173776 length 0o6776
            # Manual says  773000 through 773776 length 0o776
            # That's an offset of about 0o600000
            boot.read_PDP11_assembly_file('source/M9301-YA.txt')
            PC = m9301StartAddress + switch81_3 + switch81_6
            reg.set_pc(PC, "M9301")  # 0o165000
        else:
            reg.set_pc(0o24,"M9301 else")  # 0o165000

        print(f'initializing M9301 done. PC:{oct(reg.get_pc())}')
