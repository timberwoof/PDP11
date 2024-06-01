"""PDP11 TEK4010 Emulator"""
import time
import logging
import PySimpleGUI as sg

# This shows me that I need to rework the architecture here
# Somehow the code for the terminals has to be separated out
# from the code for the DL11.
# wait_for_rcsr_done_get_lock must be in the DL11

# TEK4010 switches and buttons:
# Local/Line - local loop or connect to computer. Works like echo
#       implement as radio buttons
# Page - flashes green, clears display, and returns to Alpha mode
# Reset - returns alpha cursor to home

# modes
# 1 - alphanumeric 35 lines 74 columns
# 2 - graphic plot - commands from keyboard or computer draw stuff
# 3 - graphic input - cursor generates graphics coordinates
# 4 - print - sends image to printer. We will output a png.

# ctrl-shift-m enters graphic mode
# if in Local and Graphic input,
# then keys get converted to coordinates and are plotted

# https://stackoverflow.com/questions/16938647/python-code-for-serial-data-to-print-on-window
CIRCLE = '⚫'
CIRCLE_OUTLINE = '⚪'

class TEK4010_Console:
    """DEC TEK4010 terminal emulator and Console"""
    def __init__(self, pdp11, sw):
        """tek4010(pdp11, serial interface)"""
        logging.info('initializing tek4010')
        logging.info(f'PySimpleGUI version:{sg.__version__}') # PySimpleGUI version:5.0.4
        self.pdp11 = pdp11
        self.dl11 = pdp11.dl11
        logging.info(f'tek4010 dl11:{self.dl11}')
        self.lock = pdp11.lock
        logging.info(f'tek4010 lock:{self.lock}')
        self.window_cycles = 0
        self.buffer = 0  # for holding LF after CR was sent
        self.window = 0
        self.sw = sw
        self.runhalt = False
        self.linelocal = False

    # *********************
    # PySimpleGUI Interface
    # https://pypi.org/project/PySimpleGUI/
    # TEK4010 has a multiline and ain input_text
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
        logging.info('tek4010 make_window begins')
        pc_display = oct(self.pdp11.reg.get_pc())
        layout = [[sg.Text("PDP11:", key='tek_title'),
                   sg.Radio("Run", "runhalt", key='runhalt1'),
                   sg.Radio("Halt", "runhalt", key='runhalt0', default=True),
                   sg.Text(pc_display, key='pc_display'),
                   sg.Button('Exit'),
                   sg.Text("4010:", key='tek_title'),
                   sg.Radio("Line", "linelocal", key='linelocal1', default=True),
                   sg.Radio("Local", "linelocal", key='linelocal0'),
                   sg.Button('Page'),
                   sg.Button('Reset')
                   ],
                  [sg.Multiline(size=(74, 35),
                                key='alpha',
                                write_only=True,
                                reroute_cprint=True,
                                font=('Courier', 18),
                                text_color='green yellow',
                                background_color='black',
                                no_scrollbar=True)],
                  [sg.InputText('', size=(80, 1), focus=True, key='keyboard')]
                  ]
        self.window = sg.Window('TEK4010', layout, font=('Arial', 18), finalize=True)
        self.window['keyboard'].bind("<Return>", "_Enter")
        logging.info('tek4010 make_window done')

        # autoscroll=True,

    def wait_for_rcsr_done_get_lock(self):
        """get lock, read RCSR. If it's done, keep the lock"""
        #logging.debug('wait_for_rcsr_done_get_lock')
        self.lock.acquire()
        rcsr = self.dl11.read_RCSR()
        while (rcsr & self.dl11.RCSR_RCVR_DONE) != 0:
            #logging.debug('wait_for_rcsr_done_get_lock loop')
            self.lock.release()
            time.sleep(0.1)
            self.lock.acquire()
            rcsr = self.dl11.read_RCSR()
        #logging.debug('got RCSR_DONE and lock')
        # RCSR_RCVR_DONE == 0 and we have the python event lock

    def window_cycle(self):
        '''One PySimpleGUI window_cycle'''
        # parameters from PDP11
        # RCSR XCSR XBUF
        # outputs to PDP11: events
        # RBUF

        # multiple-character bug facts:
        # The bug happens in immediately successive iterations of window_cycle.
        # There is only one call to dl11.write_XBUF.
        # dl11.write_XBUF reliably sets XCSR.
        # RAM is protected from simultaneous acecss by threads.
        # The bug happens when a CPU cycle is split.

        self.sw.start('TEK4010 window_cycle')
        window_run = True
        pc_display = self.window['pc_display']
        pc_display.update(oct(self.pdp11.reg.get_pc()))

        # If there's a character in the dl11 transmit buffer,
        # then send it to the display
        self.lock.acquire()
        #logging.debug(f'tek4010 got lock {self.window_cycles}')
        if (self.dl11.read_XCSR() & self.dl11.XCSR_XMIT_RDY) == 0:
            XBUF = self.dl11.read_XBUF() # read_XBUF is supposed to set XCSR to XCSR_XMIT_RDY
            logging.info(
                f'cycle {self.window_cycles} {self.pdp11.CPU_cycles} dl11 XBUF sent us ' +
                f'{oct(XBUF)} {XBUF} {self.safe_character(XBUF)}')

            XCSR = self.dl11.read_XCSR()
            if (XCSR & self.dl11.XCSR_XMIT_RDY) != self.dl11.XCSR_XMIT_RDY:
                logging.error(f'XCSR {oct(XCSR)} was not set with {oct(self.dl11.XCSR_XMIT_RDY)}')

            # Sure, DL11 can send us nulls; I just won't show them.
            if XBUF != 0:
                # deal specially with <o15><o12> <13><11> CR LF
                # multiline rstrip=True therefore whitespace is stripped
                # call update or cprint with key
                if XBUF != 13:
                    sg.cprint(chr(XBUF), end='', sep='', autoscroll=True)
        self.lock.release()
        #logging.debug(f'tek4010 release lock {self.window_cycles}')

        event, values = self.window.read(timeout=0)
        # values:values:{'runhalt1': False, 'runhalt0': True, 'linelocal1': True, 'linelocal0': False, 'keyboard': ''}
        if self.runhalt != values['runhalt1']:
            self.runhalt = values['runhalt1']
            logging.info(f'set runhalt to {self.runhalt}')
            self.pdp11.set_run(self.runhalt)
        if self.linelocal !=  values['linelocal1']:
            self.linelocal =  values['linelocal1']
            logging.info(f'set linelocal to {self.linelocal}')

        # If the Enter key was hit
        # then send CR to the serial interface
        if event == 'keyboard_Enter':
            self.window['keyboard'].Update('')
            #logging.debug(f'{self.window_cycles} sending DL11 0o12 "CR"')
            self.wait_for_rcsr_done_get_lock()
            self.dl11.write_RBUF(0o15)
            #logging.debug(f'tek4010 released lock {self.window_cycles}')
            self.lock.release()

        # If there's a keyboard event
        # then send the character to the serial interface
        kbd = values['keyboard']
        if kbd != '':
            self.window['keyboard'].Update('')
            o = ord(kbd[0:1])
            #logging.debug(f'{self.window_cycles} sending DL11 {o} {self.safe_character(o)}')
            self.wait_for_rcsr_done_get_lock()
            self.dl11.write_RBUF(o)
            #logging.debug(f'tek4010 released lock {self.window_cycles}')
            self.lock.release()

        if event in (sg.WIN_CLOSED, 'Quit'):  # if user closes window or clicks cancel
            logging.info('Quit')
            window_run = False
        elif event == "Exit":
            logging.info('Exit')
            self.pdp11.set_run(False)
            window_run = False

        self.window_cycles = self.window_cycles + 1
        self.sw.stop('TEK4010 window_cycle')
        return window_run

    def close_window(self):
        """close the terminal window"""
        self.window.close()
