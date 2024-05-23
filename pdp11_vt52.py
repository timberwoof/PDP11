"""PDP11 VT52 Emulator"""
import time
import logging
import PySimpleGUI as sg

class VT52:
    """DEC VT52 terminal emulator"""
    def __init__(self, dl11, sw):
        """vt52(pdp11, serial interface)"""
        logging.info('initializing vt52')
        logging.info(f'PySimpleGUI version:{sg.__version__}') # PySimpleGUI version:5.0.4
        self.dl11 = dl11
        # throttle window updates because they are very slow
        self.cycles_since_window = 0
        self.buffer = 0  # for holding LF after CR was sent
        self.window = 0
        self.sw = sw

    # *********************
    # PySimpleGUI Interface
    # https://pypi.org/project/PySimpleGUI/
    # VT52 has a multiline and ain input_text
    # These take ~ 1000 uS to read each window_cycle

    def safe_character(self, byte):
        """return character if it is printable"""
        if byte > 31:
            result = chr(byte)
        else:
            low_ascii = ['NUL', 'SOH', 'STX', 'ETX', 'EOT', 'ENQ', 'ACK', 'BEL',
                         'BS', 'HT', 'LF', 'VF', 'FF', 'CR', 'SO', 'SI',
                         'DLE', 'DC1', 'DC2', 'DC3', 'DC4', 'NAK', 'SYN', 'ETB',
                         'CAN', 'EM', 'SUB', 'ESC', 'FS', 'GS', 'RS', 'US']
            result = low_ascii[byte]
        return result

    def make_window(self):
        """create the DL11 emulated terminal using PySimpleGUI"""
        logging.info('vt52 make_window begins')
        layout = [[sg.Multiline(size=(80, 24),
                                key='crt',
                                write_only=True,
                                reroute_cprint=True,
                                font=('Courier', 18),
                                text_color='green yellow',
                                background_color='black',
                                no_scrollbar=True)],
                  [sg.InputText('', size=(80, 1), focus=True, key='keyboard')]
                  ]
        self.window = sg.Window('VT52', layout, font=('Arial', 18), finalize=True)
        self.window['keyboard'].bind("<Return>", "_Enter")
        logging.info('vt52 make_window done')

        # autoscroll=True,

    def wait_for_rcsr_done_get_lock(self):
        """get lock, read RCSR. If it's done, keep the lock"""
        logging.info('wait_for_rcsr_done_get_lock')
        self.dl11.ram.get_lock()
        rcsr = self.dl11.read_RCSR()
        while (rcsr & self.dl11.RCSR_RCVR_DONE) != 0:
            logging.info('wait_for_rcsr_done_get_lock loop')
            self.dl11.ram.release_lock()
            time.sleep(0.1)
            self.dl11.ram.get_lock()
            rcsr = self.dl11.read_RCSR()
        logging.info('got RCSR_DONE and lock')
        # RCSR_RCVR_DONE == 0 and we have the python event lock

    def window_cycle(self):
        '''One PySimpleGUI window_cycle'''
        # parameters from PDP11
        # RCSR XCSR XBUF
        # outputs to PDP11: events
        # RBUF

        # multiple-character bug facts:
        # The bug happens in two successive iterations of window_cycle
        # We get only one call to dl11.write_XBUF.
        # dl11.write_XBUF reliably sets XCSR.
        # RAM is protected from simultaneous acecss by threads

        self.sw.start('VT52 window_cycle')

        # if there's a character in the dl11 transmit buffer,
        # then send it to the display
        self.dl11.ram.get_lock()
        if (self.dl11.read_XCSR() & self.dl11.XCSR_XMIT_RDY) == 0:
            newchar = self.dl11.read_XBUF()
            logging.info(
                f'{self.cycles_since_window} dl11 XBUF sent us ' +
                f'{oct(newchar)} {newchar} {self.safe_character(newchar)}')

            # Sure, DL11 can send us nulls; I just won't show them.
            if newchar != 0:
                # deal specially with <o15><o12> <13><11> CR LF
                # multiline rstrip=True therefore whitespace is stripped
                # call update or cprint with key
                if newchar != 13:
                    sg.cprint(chr(newchar), end='', sep='', autoscroll=True)
        self.dl11.ram.release_lock()

        event, values = self.window.read(timeout=0)

        # If the Enter key was hit
        # then send CR to the serial interface
        if event == 'keyboard_Enter':
            self.window['keyboard'].Update('')
            logging.info(f'{self.cycles_since_window} sending DL11 0o12 "CR"')
            self.wait_for_rcsr_done_get_lock()
            self.dl11.write_RBUF(0o15)
            self.dl11.ram.release_lock()

        # If there's a keyboard event
        # then send the character to the serial interface
        kbd = values['keyboard']
        if kbd != '':
            self.window['keyboard'].Update('')
            o = ord(kbd[0:1])
            logging.info(f'{self.cycles_since_window} sending DL11 {o} {self.safe_character(o)}')
            self.wait_for_rcsr_done_get_lock()
            self.dl11.write_RBUF(o)
            self.dl11.ram.release_lock()

        self.cycles_since_window = self.cycles_since_window + 1
        self.sw.stop('VT52 window_cycle')

    def close_window(self):
        """close the terminal window"""
        self.window.close()
