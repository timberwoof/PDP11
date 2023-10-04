"""PDP11 DL11 communications console"""
import PySimpleGUI as sg

# https://stackoverflow.com/questions/16938647/python-code-for-serial-data-to-print-on-window
CIRCLE = '⚫'
CIRCLE_OUTLINE = '⚪'
PC_DISPLAY = ''

class DL11:
    """DEC DL11 serial interface and terminal emulator"""
    def __init__(self, ram, base_address, sw):
        """dlss(ram object, base address for this device)
        """
        print(f'initializing dl11({oct(base_address)})   {oct(ord("$"))}')
        self.ram = ram
        self.sw = sw
        self.RCSR_address = base_address
        self.RBUF_address = base_address + 2
        self.XCSR_address = base_address + 4
        self.XBUF_address = base_address + 6

        self.ram.register_io_writer(self.RCSR_address, self.write_RCSR)
        self.ram.register_io_writer(self.RBUF_address, self.write_RBUF)
        self.ram.register_io_writer(self.XCSR_address, self.write_XCSR)
        self.ram.register_io_writer(self.XBUF_address, self.write_XBUF)

        self.ram.register_io_reader(self.RCSR_address, self.read_RCSR)
        self.ram.register_io_reader(self.RBUF_address, self.read_RBUF)
        self.ram.register_io_reader(self.XCSR_address, self.read_XCSR)
        self.ram.register_io_reader(self.XBUF_address, self.read_XBUF)

        # RCSR Receiver Status Register bits
        # This is a DL11-B
        # no paper tape bits as for A and get_c.
        # no modem-control bits as for E
        self.RCSR_RCVR_ACT = 0o004000  # 11 RO - active (we're not multithreaded yet)
        self.RCSR_RCVR_DONE = 0o000200  # 7 RO
        #   set when character has been received,
        #   cleared when RBUF is read (addressed for read or write by CPU)
        self.RCSR_INT_ENB = 0o000100  # 6 - when set, enables interrupt (not implemented)
        self.RCSR = 0   # receive status register. Not active; no character yet
        self.RBUF = 0   # receive buffer

        # XCSR Transmitter Status Register bits
        # This is a DL11-B
        # No Break bit
        self.XCSR_XMIT_RDY = 0o000200  # 7 RO -
        #   set when transmitter can accept another character
        #   cleared by loading XBUF (write by CPU)
        self.XCSR_SMIT_INT_ENB = 0o000100  # 6 RW - when set, enables interrupt (not implemented)
        self.XCSR_MAINT = 0o000004  # 2 RW - maintenance loopback XBUF to RBUF
        self.XCSR = self.XCSR_XMIT_RDY   # transmit status register ready on init
        self.XBUF = 0   # transmit buffer

        # throttle window updates because they are very slow
        self.cycles_since_window = 0
        print('initializing dl11 done')

    # DL11 Internal Interface to PDP-11 Emulator

    # Receiver receives characters from a terminal.
    # RCSR Receiver Status Register
    # 7: set when character has been received (ro)
    # 6: receiver interrupt enable (rw)
    # 0: reader enable (wo) clears 7
    def write_RCSR(self, byte):
        """write to receiver status register"""
        print(f'    dl11.write_RCSR({oct(byte)})')
        self.RCSR = byte

    def read_RCSR(self):
        """read from receiver status register"""
        print(f'    dl11.read_RCSR() returns {oct(self.RCSR)}')
        return self.RCSR

    # RBUF reciever data buffer (ro)
    # 15: error
    # 14: overrun
    # 13: framing error
    # 12: receive parity error
    # 7-0 received data
    def write_RBUF(self, byte):
        """DL11 calls this to write to receiver buffer and set ready bit"""
        print(f'    dl11.write_RBUF({oct(byte)}):"{self.safe_character(byte)}"')
        self.RBUF = byte
        self.RCSR = self.RCSR | self.RCSR_RCVR_DONE

    def read_RBUF(self):
        """PDP11 calls this to read from receiver buffer. Read buffer and reset ready bit"""
        result = self.RBUF
        print(f'    dl11.read_RBUF() returns {oct(result)}:"{self.safe_character(result)}"')
        self.RCSR = self.RCSR & ~self.RCSR_RCVR_DONE
        return result

    # Transmitter enables CPU to send characters to a terminal.
    # XCSR transmit status register (rw)
    # 7: transmitter ready (ro).
    #   Cleared when XBUF is loaded.
    #   Set when XBUF can accept another character.
    # 6: transmit interrupt enable (rw)
    # 2: maintenance. when set sends serial output to serial input (rw)
    # 0: break. when set sends continuous space (rw)
    def write_XCSR(self, byte):
        """write to transmitter status register"""
        print(f'    dl11.write_XCSR({oct(byte)})')
        # make the RW and RO bits play nice
        # only two are implemented so far
        self.XCSR = byte

    def read_XCSR(self):
        """read from transitter status register"""
        print(f'    dl11.read_XCSR() returns {oct(self.XCSR)}')
        return self.XCSR

    # XBUF transmit data buffer (wo)
    # 7-0 transmitted data buffer
    def write_XBUF(self, byte):
        """PDP11 calls this to write to transmitter buffer register."""
        print(f'    dl11.write_XBUF({oct(byte)}):"{self.safe_character(byte)}"')
        self.XBUF = byte
        # self.XCSR_XMIT_RDY is cleared when XBUF is loaded
        self.XCSR = self.XCSR & ~self.XCSR_XMIT_RDY

        # check for Maintenance mode
        if self.XCSR & self.XCSR_MAINT:
            self.write_RBUF(byte)

    def read_XBUF(self):
        """DL11 calls this to read from transmitter buffer register."""
        result = self.XBUF
        print(f'    dl11.read_XBUF() returns {oct(result)}:"{self.safe_character(result)}"')
        # self.XCSR_XMIT_RDY is set when XBUF can accept another character
        self.XCSR = self.XCSR | self.XCSR_XMIT_RDY
        return result

    def safe_character(self, byte):
        """return character if it is printable"""
        if byte > 32:
            result = chr(byte)
        else:
            result = ""
        return result

    # *********************
    # PySimpleGUI Interface
    # *** This should be a different class from teh DL11.
    # *** It ought to be possible to run the emulator as a command-line program.
    # *** In that case, the DL11 would just talk to the command line's emulator.
    # *** That means the PySimpleGUI and Terminal ways should be different classes that talk to dl11.
    def make_window(self):
        """create the DL11 emulated terminal using PySimpleGUI"""
        print('dl11 make_window begins')
        layout = [[sg.Text(PC_DISPLAY, key='pc')],
                  [sg.Multiline(size=(80, 24), key='crt', write_only=True, reroute_cprint=True, font=('Courier', 18), text_color='green yellow', background_color='black')],
                  [sg.InputText('', size=(80, 1), focus=True, key='keyboard')],
                  [sg.Text(CIRCLE, key='runLED'), sg.Button('Run'), sg.Button('Halt'), sg.Button('Exit')]                  ]
        self.window = sg.Window('PDP-11 Console', layout, font=('Arial', 18), finalize=True)
        self.window['keyboard'].bind("<Return>", "_Enter")
        print('dl11 make_window done')

        # autoscroll=True,

    def get_pc_text(self, pdp11):
        """create a display of the program counter"""
        pc_text = ''
        pc = pdp11.reg.get_pc()
        mask = 1
        bits = self.ram.top_of_memory
        while bits > 0:
            if pc & mask == mask:
                pc_text = CIRCLE_OUTLINE + pc_text
            else:
                pc_text = CIRCLE + pc_text
            bits = bits >> 1
            mask = mask << 1
        return pc_text

    def terminal_window_cycle(self, cpu_run, pdp11):
        """Run one iteration of the PySimpleGUI terminal window loop"""
        self.sw.start('DL11 cycle')
        self.cycles_since_window = self.cycles_since_window + 1
        window_run = True

        pc = self.window['pc']
        pc.update(self.get_pc_text(pdp11))

        # maybe get character from dl11 transmit buffer
        if self.XCSR & self.XCSR_XMIT_RDY == 0 and self.XBUF != 0:
            newchar = self.read_XBUF()
            sg.cprint(chr(newchar), end='')

        # Maybe read the window
        if self.cycles_since_window > 100:
            self.cycles_since_window = 0

            # We should only do this when there's a keyboard event
            # This takes on average 13 milliseocnds
            self.sw.start('DL11 window read')
            event, values = self.window.read(timeout=0)
            self.sw.stop('DL11 window read')

            # handle the window events
            if event in (sg.WIN_CLOSED, 'Quit'):  # if user closes window or clicks cancel
                window_run = False
            elif event == "Run":
                cpu_run = True
                text = self.window['runLED']
                text.update(CIRCLE_OUTLINE)
            elif event == "Halt":
                cpu_run = False
                text = self.window['runLED']
                text.update(CIRCLE)
            elif event == "Exit":
                cpu_run = False
                window_run = False
            elif event == 'keyboard_Enter':
                self.window['keyboard'].Update('')
                if self.RCSR & self.RCSR_RCVR_DONE == 0:
                    self.write_RBUF(ord('\n'))
            kbd = values['keyboard']
            if kbd != '':
                self.window['keyboard'].Update('')
                if self.RCSR & self.RCSR_RCVR_DONE == 0:
                    self.write_RBUF(ord(kbd[0:1]))

        self.sw.stop('DL11 cycle')
        return window_run, cpu_run

    def close_terminal_window(self):
        """close the terminal window"""
        self.window.close()