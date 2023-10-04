"""PDP11 M9301 Boot Rom"""
class M9301:
    """Emulates PDP11 M9301 boot ROM card"""
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

        # 7.3 Micrositch Settings. See p. 7-2 of
        # PDP11 M9301 bootstrap/terminator module maintenance and operator's manual
        m9301_start_ddress = ram.top_of_memory - 0o4777 # *** Only supports 16-bit address for now.
        # switch81_1 = True # low rom enable ON = True.
        # "False" is not implemented. This calss behaves as though this is ON.
        switch81_2 = True # power up reboot enable ON = True
        # If this is on (True) then processor will trap to a selectable address.
        # Switches 3-10 set the address.
        # If this is off (False) then  processor will trap to location 24 on startup.

        # Address switches. Configure this by setting the on/off variable to on or off.
        on = 0o000377
        off = 0o000000
        switch81_3 = 0o0400 & on # bus address bit 8
        switch81_4 = 0o0200 & off # bus address bit 7
        switch81_5 = 0o0100 & off # bus address bit 6
        switch81_6 = 0o0040 & on # bus address bit 5
        switch81_7 = 0o0020 & off # bus address bit 4
        switch81_8 = 0o0010 & off # bus address bit 3
        switch81_9 = 0o0004 & off # bus address bit 2
        switch81_10 = 0o0002 & off # bus address bit 1
        # include the switches you want to have '1' digits.
        # Where the DEC manual says to have a switch OFF, include it
        # Thus none of the switches results in CPU Diagnostics with Console Emulator:
        # PC = m9301_start_ddress
        # console boot switch causes M9301 to be activated
        # causes normal boot-up sequence
        # new PC address is logical OR of 0o173000 and selected microswitches
        # To set CPU diag. Boot RK11:
        # PC = m9301_start_ddress + switch81_3 + switch81_6
        if switch81_2:
            # Load boot rom image into RAM (165000 - 173776 length 0o6776
            # Manual says  773000 through 773776 length 0o776
            # That's an offset of about 0o600000
            boot.read_pdp11_assembly_file('source/M9301-YA.txt')
            PC = m9301_start_ddress + switch81_3 + switch81_4 + switch81_5 + switch81_6 + \
                 switch81_7 + switch81_8 + switch81_9 + switch81_10
            reg.set_pc(PC, "M9301")  # 0o165000
        else:
            reg.set_pc(0o24,"M9301 else")  # 0o165000

        print(f'initializing M9301 done. PC:{oct(reg.get_pc())}')

    # Pylint complains that this has too few public methods.
    # That's perfectly acceptable as this only does anything on startup.