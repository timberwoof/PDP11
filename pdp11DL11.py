"""PDP11 DL11 communications console"""
import tkinter as tk
import PySimpleGUI as sg
from pdp11Hardware import ram

# https://stackoverflow.com/questions/16938647/python-code-for-serial-data-to-print-on-window
CIRCLE = '⚫'
CIRCLE_OUTLINE = '⚪'

class dl11:
    def __init__(self, ram, base_address, terminal=False):
        """dlss(ram object, base address for this device)
        """
        print(f'initializing dl11({oct(base_address)})')
        self.ram = ram
        self.RCSR_address = base_address
        self.RBUF_address = base_address + 2
        self.XCSR_address = base_address + 4
        self.XBUF_address = base_address + 6

        print(f'    dl11 RCSR:{oct(self.RCSR_address)}')
        print(f'    dl11 RBUF:{oct(self.RBUF_address)}')
        print(f'    dl11 XCSR:{oct(self.XCSR_address)}')
        print(f'    dl11 XBUF:{oct(self.XBUF_address)}')

        self.RCSR_ready_bit = 0o0200
        self.RCSR = self.RCSR_ready_bit   # receive
        self.RBUF = 0   # receive buffer
        self.XCSR_ready_bit = 0o0200
        self.XCSR = self.XCSR_ready_bit   # transmit status register ready on init
        self.XBUF = 0   # transmit buffer

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
        """write to receiver buffer register and set ready bit"""
        print(f'    dl11.write_RBUF({oct(byte)}):"{chr(byte)}"')
        self.RBUF = byte
        self.write_RCSR(self.RCSR_ready_bit)

    def read_RBUF(self):
        """read from receiver buffer register. Read once only and reset ready bit"""
        print(f'    dl11.read_RBUF() returns {oct(self.RBUF)}:"{chr(self.RBUF)}"')
        result = self.RBUF
        self.RBUF = 0
        self.RCSR = self.RCSR_ready_bit
        return result

    def RBUF_ready(self):
        if self.read_RCSR() & self.RCSR_ready_bit == self.RCSR_ready_bit:
            return True
        else:
            return False

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
        self.XCSR = byte

    def read_XCSR(self):
        """read from transitter status register"""
        print(f'    dl11.read_XCSR() returns {oct(self.XCSR)}')
        return self.XCSR

    def XBUF_ready(self):
        if self.XCSR & self.XCSR_ready_bit == 0 and self.XBUF != 0:
            return True
        else:
            return False

    # XBUF transmit data buffer (wo)
    # 7-0 transmitted data buffer
    def write_XBUF(self, byte):
        """write to transitter buffer register.
        Generally called by the CPU"""
        print(f'    dl11.write_XBUF({oct(byte)})')#:"{chr(byte)}"')
        self.XBUF = byte
        # self.XCSR_ready_bit is cleared when XBUF is loaded
        self.XCSR = self.XCSR & ~self.XCSR_ready_bit

    def read_XBUF(self):
        """read from transmitter buffer register.
        Generally called by some outside process"""
        result = self.XBUF
        print(f'    dl11.read_XBUF() returns {oct(result)}')#:"{chr(self.XBUF)}"')
        #self.XBUF = 0 # there's no reason it can't be read twice
        # self.XCSR_ready_bit is set when XBUF can accept another character
        self.XCSR = self.XCSR | self.XCSR_ready_bit
        return result

    def register_with_ram(self):
        print(f'dl11 register_with_ram')
        self.ram.register_io_writer(self.RCSR_address, self.write_RCSR)
        self.ram.register_io_writer(self.RBUF_address, self.write_RBUF)
        self.ram.register_io_writer(self.XCSR_address, self.write_XCSR)
        self.ram.register_io_writer(self.XBUF_address, self.write_XBUF)

        self.ram.register_io_reader(self.RCSR_address, self.read_RCSR)
        self.ram.register_io_reader(self.RBUF_address, self.read_RBUF)
        self.ram.register_io_reader(self.XCSR_address, self.read_XCSR)
        self.ram.register_io_reader(self.XBUF_address, self.read_XBUF)

    # *********************
    # PySimpleGUI Interface
    def makeWindow(self):
        """create the DL11 emulated terminal using PySimpleGUI"""
        print(f'dl11 makeWindow begins\n')
        layout = [[sg.Multiline(size=(80, 24), key='crt', write_only=True, reroute_cprint=True, font=('Courier', 18), text_color='green yellow', background_color='black')],
                  [sg.InputText('', size=(80, 1), focus=True, key='keyboard')],
                  [sg.Text(CIRCLE, text_color='green', key='runLED'), sg.Button('Run'), sg.Button('Halt'), sg.Button('Exit')]]
        self.window = sg.Window('PDP-11 Console', layout, font=('Arial', 18), finalize=True)
        self.window['keyboard'].bind("<Return>", "_Enter")
        print('dl11 makeWindow done')

        # autoscroll=True,

    def terminalWindowCycle(self, cpuRun):
        """Run one iteration of the PySimpleGUI terminal window loop"""
        windowRun = True

        # maybe get character from dl11 transmit buffer
        if self.XBUF_ready():
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
            if self.RBUF_ready():
                self.write_RBUF(ord('\n'))
        kbd = values['keyboard']
        if kbd != '':
            self.window['keyboard'].Update('')
            if self.RBUF_ready():
                self.write_RBUF(ord(kbd[0:]))

        return windowRun, cpuRun

    def terminalCloseWindow(self):
        self.window.close()

