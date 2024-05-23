"""PDP11 VT52 Emulator"""
import logging
import PySimpleGUI as sg
import pdp11_util as u

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
    # These take ~ 1000 uS to read each window_cycle

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

    def wait_for_RCSR_DONE_get_lock(self):
        """get lock, read RCSR. If it's done, keep the lock"""
        logging.info('wait_for_RCSR_DONE_get_lock')
        self.dl11.ram.get_lock()
        rcsr = self.dl11.read_RCSR()
        while rcsr & self.dl11.RCSR_RCVR_DONE != 0:
            logging.info('wait_for_RCSR_DONE_get_lock loop')
            self.dl11.ram.release_lock()
            sleep(0.1)
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
        self.sw.start('VT52')
        # If there's a character in our buffer, send it to the DL11
        if self.buffer != 0:
            wait_for_RCSR_DONE_get_lock()
            self.dl11.write_RBUF(self.buffer)
            self.dl11.ram.release_lock()
            self.buffer = 0

        # if there's a character in the dl11 transmit buffer,
        # then send it to the display
        #logging.info('dl11.get_lock for XCSR') # not hanging here.
        self.dl11.ram.get_lock()
        if self.dl11.read_XCSR() & self.dl11.XCSR_XMIT_RDY == 0:
            logging.info(f'{self.cycles_since_window} call dl11.read_XBUF')
            newchar = self.dl11.read_XBUF()
            # Sure, DL11 can send me nulls; I just won't show them.
            logging.info(
                f'{self.cycles_since_window} dl11 XBUF sent us {oct(newchar)} {newchar}') # "{u.safe_character(newchar)}"')
            if newchar != 0:
                # deal specially with <o15><o12> <13><11> CR LF
                # multiline rstrip=True therefore whitespace is stripped
                # call update or cprint with key
                if newchar != 13:
                    sg.cprint(chr(newchar), end='', sep='', autoscroll=True)
        self.dl11.ram.release_lock()

        # 1000 microseconds
        event, values = self.window.read(timeout=0)

        # If the Enter key was hit
        # then send CR to the serial interface
        if event == 'keyboard_Enter':
            self.window['keyboard'].Update('')
            logging.info(f'{self.cycles_since_window} sending DL11 0o12 "CR"')
            wait_for_RCSR_DONE_get_lock()
            self.dl11.write_RBUF(0o15)
            self.dl11.ram.release_lock()

        # If there's a keyboard event
        # then send the character to the serial interface
        kbd = values['keyboard']
        if kbd != '':
            self.window['keyboard'].Update('')
            o = ord(kbd[0:1])
            logging.info(f'{self.cycles_since_window} sending DL11 {o} "{u.safe_character(o)}"')
            wait_for_RCSR_DONE_get_lock()
            self.dl11.write_RBUF(o)
            self.dl11.ram.release_lock()

        self.cycles_since_window = self.cycles_since_window + 1
        self.sw.stop('VT52')
        return

    def close_window(self):
        """close the terminal window"""
        self.window.close()
