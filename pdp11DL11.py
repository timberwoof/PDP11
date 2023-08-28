"""PDP11 DL11 communications console"""
import tkinter as tk
import PySimpleGUI as sg

from pdp11Hardware import ram

# https://stackoverflow.com/questions/16938647/python-code-for-serial-data-to-print-on-window

class dl11:
    def __init__(self, ram, base_address):
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

        self.RCSR = 0   # receive
        self.RBUF = 0   # receive buffer
        self.XCSR = 0o0200   # transmit status register always ready
        self.XBUF = 0   # transmit buffer
        self.bigbuf = ''

        #self.layout = [[sg.Multiline(size=(80, 24), autoscroll=True, key='crt')],
        #               [sg.InputText(size=(80, 1), key='keyboard')]]
        #self.window = sg.Window('PDP-11 Console', self.layout, font=('Arial', 18))
        #event, values = self.window.read()

    # Receiver Status Register
    # 7: set when character has been received (ro)
    # 6: receiver interrupt enable (rw)
    # 0: reader enable (wo)
    def write_RCSR(self, byte):
        """write to receiver status register"""
        print(f'    dl11.write_RCSR({oct(byte)})')
        self.RCSR = byte

    def read_RCSR(self):
        """read from receiver status register"""
        print(f'    dl11.read_RCSR() returns {oct(self.RCSR)}')
        return self.RCSR

    # reciever data buffer (ro)
    # 15: error
    # 14: overrun
    # 13: framing error
    # 12: receive parity error
    # 7-0 received data
    def write_RBUF(self, byte):
        """write to receiver buffer register"""
        print(f'    dl11.write_RBUF({oct(byte)}):{chr(byte)}')
        self.RBUF = byte

    def read_RBUF(self):
        """read from receiver buffer register"""
        print(f'    dl11.read_RBUF() returns {oct(self.RBUF)}:{chr(self.RBUF)}')
        return self.RBUF

    # transmit status register (rw)
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

    # transmit data buffer (wo)
    # 7-0 transmitted data buffer
    def write_XBUF(self, byte):
        """write to transitter buffer register"""
        print(f'    dl11.write_XBUF({oct(byte)}):{chr(byte)}')
        self.XBUF = byte
        self.bigbuf = self.bigbuf + chr(byte)
        #self.window['crt'].update(values[chr(byte)], append=True)

    def read_XBUF(self):
        """read from transitter buffer register"""
        print(f'    dl11.read_XBUF() returns {oct(self.XBUF)}:{chr(self.XBUF)}')
        return self.XBUF



    def register_with_ram(self):
        print(f'    dl11.register_with_ram')
        self.ram.register_io_writer(self.RCSR_address, self.write_RCSR)
        self.ram.register_io_writer(self.RBUF_address, self.write_RBUF)
        self.ram.register_io_writer(self.XCSR_address, self.write_XCSR)
        self.ram.register_io_writer(self.XBUF_address, self.write_XBUF)

        self.ram.register_io_reader(self.RCSR_address, self.read_RCSR)
        self.ram.register_io_reader(self.RBUF_address, self.read_RBUF)
        self.ram.register_io_reader(self.XCSR_address, self.read_XCSR)
        self.ram.register_io_reader(self.XBUF_address, self.read_XBUF)

    def dumpBuffer(self):
        print(f'    dl11 buffer: {self.bigbuf}')