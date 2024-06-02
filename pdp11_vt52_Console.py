"""PDP11 VT52 Emulator"""
import time
import logging
import PySimpleGUI as sg

# https://stackoverflow.com/questions/16938647/python-code-for-serial-data-to-print-on-window
CIRCLE = '⚫'
CIRCLE_OUTLINE = '⚪'

class VT52_Console:
    """DEC VT52 terminal emulator and Console"""
    def __init__(self, pdp11, sw):
        """vt52(pdp11, serial interface)"""
        logging.info('initializing vt52')
        logging.info(f'PySimpleGUI version:{sg.__version__}') # PySimpleGUI version:5.0.4
        self.pdp11 = pdp11
        self.dl11 = pdp11.dl11
        logging.info(f'vt52 dl11:{self.dl11}')
        self.lock = pdp11.lock
        logging.info(f'vt52 lock:{self.lock}')
        self.window_cycles = 0
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

    def pc_to_blinky_lights(self):
        """create a display of the pdp11's program counter"""
        pc_text = ''
        pc = self.pdp11.reg.get_pc()
        mask = 1
        bits = self.pdp11.ram.top_of_memory
        while bits > 0:
            if pc & mask == mask:
                pc_text = CIRCLE_OUTLINE + pc_text
            else:
                pc_text = CIRCLE + pc_text
            bits = bits >> 1
            mask = mask << 1
        return pc_text

    def make_window(self):
        """create the DL11 emulated terminal using PySimpleGUI"""
        logging.info('vt52 make_window begins')
        pc_display = oct(self.pdp11.reg.get_pc())
        layout = [[sg.Text(pc_display, key='pc_display')], #, sg.Text(pc_lights, key='pc_lights')
                  [sg.Text(CIRCLE, key='runLED'), sg.Button('Run'), sg.Button('Halt'), sg.Button('Exit')],
                  [sg.Multiline(size=(80, 24),
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
        self.dl11.ram.get_lock('VT52 RCSR')
        rcsr = self.dl11.read_RCSR()
        while (rcsr & self.dl11.RCSR_RCVR_DONE) != 0:
            logging.info('wait_for_rcsr_done_get_lock loop')
            self.dl11.ram.release_lock()
            time.sleep(0.1)
            self.dl11.ram.get_lock('VT52 RCSR')
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
        # The bug happens in immediately successive iterations of window_cycle.
        # There is only one call to dl11.write_XBUF.
        # dl11.write_XBUF reliably sets XCSR.
        # RAM is protected from simultaneous acecss by threads.
        # The bug happens when a CPU cycle is split.

        self.sw.start('VT52 window_cycle')
        window_run = True
        pc_display = self.window['pc_display']
        pc_display.update(oct(self.pdp11.reg.get_pc()))
        #pc_lights = self.window['pc_lights']
        #pc_lights.update(self.pc_to_blinky_lights())

        # If there's a character in the dl11 transmit buffer,
        # then send it to the display
        self.lock.acquire()
        #logging.debug(f'vt52 got lock {self.window_cycles}')
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
        #logging.debug(f'vt52 release lock {self.window_cycles}')

        event, values = self.window.read(timeout=0)
        # If the Enter key was hit
        # then send CR to the serial interface
        if event == 'keyboard_Enter':
            self.window['keyboard'].Update('')
            logging.info(f'{self.window_cycles} sending DL11 0o12 "CR"')
            logging.info(f'vt52 wait_for_rcsr_done_get_lock')
            self.wait_for_rcsr_done_get_lock()
            logging.info(f'vt52 got lock; dl11.write_RBUF')
            self.dl11.write_RBUF(0o15)
            logging.info(f'vt52 release lock {self.window_cycles}')
            self.lock.release()

        # If there's a keyboard event
        # then send the character to the serial interface
        kbd = values['keyboard']
        if kbd != '':
            self.window['keyboard'].Update('')
            o = ord(kbd[0:1])
            logging.info(f'{self.window_cycles} sending DL11 {o} {self.safe_character(o)}')
            logging.info(f'vt52 wait_for_rcsr_done_get_lock')
            self.wait_for_rcsr_done_get_lock()
            logging.info(f'vt52 got lock; dl11.write_RBUF')
            self.dl11.write_RBUF(o)
            logging.info(f'vt52 release lock')
            self.lock.release()

        if event in (sg.WIN_CLOSED, 'Quit'):  # if user closes window or clicks cancel
            #logging.debug('Quit')
            window_run = False
        elif event == "Run":
            #logging.debug('Run')
            self.pdp11.set_run(True)
            text = self.window['runLED']
            text.update(CIRCLE_OUTLINE)
        elif event == "Halt":
            #logging.debug('Halt')
            self.pdp11.set_run(False)
            text = self.window['runLED']
            text.update(CIRCLE)
        elif event == "Exit":
            #logging.debug('Exit')
            self.pdp11.set_run(False)
            window_run = False

        self.window_cycles = self.window_cycles + 1
        self.sw.stop('VT52 window_cycle')
        return window_run

    def close_window(self):
        """close the terminal window"""
        self.window.close()
