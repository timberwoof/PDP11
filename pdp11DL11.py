"""PDP11 DL11 communications console"""
import tkinter as tk
import PySimpleGUI as sg
from pdp11Hardware import ram

# https://stackoverflow.com/questions/16938647/python-code-for-serial-data-to-print-on-window
CIRCLE = '⚫'
CIRCLE_OUTLINE = '⚪'
PC_DISPLAY = ''

class dl11:
    def __init__(self, ram, base_address, terminal=False):
        """dlss(ram object, base address for this device)
        """
        print(f'initializing dl11({oct(base_address)})   {oct(ord("$"))}')
        self.ram = ram
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
        # no paper tape bits as for A and C.
        # no modem-control bits as for E
        self.RCSR_RCVR_ACT = 0o004000 # 11 RO - active (we're not multithreaded yet)
        self.RCSR_RCVR_DONE = 0o000200 # 7 RO
        #   set when character has been received,
        #   cleared when RBUF is read (addressed for read or write by CPU)
        self.RCSR_INT_ENB = 0o000100 # 6 - when set, enables interrupt (not implemented)
        self.RCSR = 0   # receive status register. Not active; no character yet
        self.RBUF = 0   # receive buffer

        # XCSR Transmitter Status Register bits
        # This is a DL11-B
        # No Break bit
        self.XCSR_XMIT_RDY = 0o000200 # 7 RO -
        #   set when transmitter can accept another character
        #   cleared by loading XBUF (write by CPU)
        self.XCSR_SMIT_INT_ENB = 0o000100 # 6 RW - when set, enables interrupt (not implemented)
        self.XCSR_MAINT = 0o000004 # 2 RW - maintenance loopback XBUF to RBUF
        self.XCSR = self.XCSR_XMIT_RDY   # transmit status register ready on init
        self.XBUF = 0   # transmit buffer
        print(f'initializing dl11 done')

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
        print(f'    dl11.write_RBUF({oct(byte)}):"{self.safeCharacter(byte)}"')
        self.RBUF = byte
        self.RCSR = self.RCSR | self.RCSR_RCVR_DONE

    def read_RBUF(self):
        """PDP11 calls this to read from receiver buffer. Read buffer and reset ready bit"""
        result = self.RBUF
        print(f'    dl11.read_RBUF() returns {oct(result)}:"{self.safeCharacter(result)}"')
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
        print(f'    dl11.write_XBUF({oct(byte)}):"{self.safeCharacter(byte)}"')
        self.XBUF = byte
        # self.XCSR_XMIT_RDY is cleared when XBUF is loaded
        self.XCSR = self.XCSR & ~self.XCSR_XMIT_RDY

        # check for Maintenance mode
        if self.XCSR & self.XCSR_MAINT:
            self.write_RBUF(byte)

    def read_XBUF(self):
        """DL11 calls this to read from transmitter buffer register."""
        result = self.XBUF
        print(f'    dl11.read_XBUF() returns {oct(result)}:"{self.safeCharacter(result)}"')
        # self.XCSR_XMIT_RDY is set when XBUF can accept another character
        self.XCSR = self.XCSR | self.XCSR_XMIT_RDY
        return result

    # *********************
    # PySimpleGUI Interface
    def makeWindow(self):
        """create the DL11 emulated terminal using PySimpleGUI"""
        print(f'dl11 makeWindow begins')
        layout = [[sg.Text(PC_DISPLAY, key='programCounter')],
                  [sg.Multiline(size=(80, 24), key='crt', write_only=True, reroute_cprint=True, font=('Courier', 18), text_color='green yellow', background_color='black')],
                  [sg.InputText('', size=(80, 1), focus=True, key='keyboard')],
                  [sg.Text(CIRCLE, key='runLED'), sg.Button('Run'), sg.Button('Halt'), sg.Button('Exit')]                  ]
        self.window = sg.Window('PDP-11 Console', layout, font=('Arial', 18), finalize=True)
        self.window['keyboard'].bind("<Return>", "_Enter")
        print('dl11 makeWindow done')

        # autoscroll=True,

    def get_pc_text(self, pdp11):
        """create a display of the program counter"""
        PCtext = ''
        PC = pdp11.reg.get_pc()
        mask = 1
        bits = self.ram.top_of_memory
        while bits > 0:
            if PC & mask == mask:
                PCtext = CIRCLE_OUTLINE + PCtext
            else:
                PCtext = CIRCLE + PCtext
            bits = bits >> 1
            mask = mask << 1
        return PCtext

    def terminalWindowCycle(self, cpuRun, pdp11):
        """Run one iteration of the PySimpleGUI terminal window loop"""
        windowRun = True

        programCounter = self.window['programCounter']
        programCounter.update(self.get_pc_text(pdp11))

        # maybe get character from dl11 transmit buffer
        if self.XCSR & self.XCSR_XMIT_RDY == 0 and self.XBUF != 0:
            newchar = self.read_XBUF()
            sg.cprint(chr(newchar), end='')

        # handle the window
        event, values = self.window.read(timeout=0)
        if event == sg.WIN_CLOSED or event == 'Quit': # if user closes window or clicks cancel
            windowRun = False
        elif event == "Run":
            cpuRun = True
            text = self.window['runLED']
            text.update(CIRCLE_OUTLINE)
        elif event == "Halt":
            cpuRun = False
            text = self.window['runLED']
            text.update(CIRCLE)
        elif event == "Exit":
            cpuRun = False
            windowRun = False
        elif event == 'keyboard_Enter':
            self.window['keyboard'].Update('')
            if self.RCSR & self.RCSR_RCVR_DONE == 0:
                self.write_RBUF(ord('\n'))
        kbd = values['keyboard']
        if kbd != '':
            self.window['keyboard'].Update('')
            if self.RCSR & self.RCSR_RCVR_DONE == 0:
                self.write_RBUF(ord(kbd[0:]))

        return windowRun, cpuRun

    def terminalCloseWindow(self):
        self.window.close()

    def safeCharacter(self, byte):
        if byte > 32:
            result = chr(byte)
        else:
            result = ""
        return result