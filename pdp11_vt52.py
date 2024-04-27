"""PDP11 VT52 Emulator"""
import logging
import PySimpleGUI as sg

class VT52:
    """DEC VT52 terminal emulator"""
    def __init__(self, dl11, sw, ui=False):
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
    # These take ~ 1000 uS to read each cycle

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

    def window_cycle(self):
        '''One PySimpleGUI window_cycle'''
        self.sw.start('VT52')
        # If there's a character in our buffer, send it to the DL11
        if self.buffer != 0:
            if self.dl11.RCSR & self.dl11.RCSR_RCVR_DONE == 0:
                self.dl11.write_RBUF(self.buffer)
                self.buffer = 0

        # if there's a character in the dl11 transmit buffer,
        # then send it to the display
        if self.dl11.XCSR & self.dl11.XCSR_XMIT_RDY == 0:
            newchar = self.dl11.read_XBUF()
            # Sure, DL11 can send me nulls; I just won't show them.
            if newchar != 0:
                logging.debug(f'dl11 XBUF sent us {oct(newchar)} {newchar} "{chr(newchar)}"')
                print(chr(newchar), end='')
                # deal specially with <o15><o12> <13><11> CR LF
                # multiline rstrip=True therefore whitespace is stripped
                # call update or cprint with key

                # try to filter out linefeeds 11. Nope. Still breaks wrong
                # try to filter out carriage return 13. Ddn't break wrong.
                if newchar != 13:
                    sg.cprint(chr(newchar), end='', sep='', autoscroll=True)

        # 1000 microseconds
        event, values = self.window.read(timeout=0)

        # If the Enter key was hit
        # then send CR LF to the serial interface
        if event == 'keyboard_Enter':
            self.window['keyboard'].Update('')
            if self.dl11.RCSR & self.dl11.RCSR_RCVR_DONE == 0:
                self.dl11.write_RBUF(0o15) # CR, not \n which is LF
                # put the LF into our buffer
                self.buffer = 0o12

        # If there's a keyboard event
        # then send the character to the serial interface
        kbd = values['keyboard']
        if kbd != '':
            self.window['keyboard'].Update('')
            if self.dl11.RCSR & self.dl11.RCSR_RCVR_DONE == 0:
                self.dl11.write_RBUF(ord(kbd[0:1]))

        self.sw.stop('VT52')
        return

    def close_window(self):
        """close the terminal window"""
        self.window.close()
