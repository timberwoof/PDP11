"""PDP11 VT52 Emulator"""
import PySimpleGUI as sg

class VT52:
    """DEC VT52 terminal emulator"""
    def __init__(self, dl11, sw, ui=False):
        """vt52(pdp11, serial interface)"""
        print('initializing vt52')
        self.dl11 = dl11
        # throttle window updates because they are very slow
        self.cycles_since_window = 0
        self.buffer = 0  # for holding LF after CR was sent
        self.window = 0
        self.sw = sw

    # ************************************
    # Cycle the VT52 with no GUI interface
    def cycle(self):
        '''One  cycle for VT52'''
        # This is an attenpt to make the VT52 automatcaly send LF after CR.
        # If there's a character in our buffer, send it to the DL11
        if self.buffer != 0:
            if self.dl11.RCSR & self.dl11.RCSR_RCVR_DONE == 0:
                self.dl11.write_RBUF(self.buffer)
                self.buffer = 0

        # if there's a character in the dl11 transmit buffer,
        # then eat it
        if self.dl11.XCSR & self.dl11.XCSR_XMIT_RDY == 0:
            newchar = self.dl11.read_XBUF()
            # Sure, DL11 can send me nulls; I just won't show them.
            if newchar != 0:
                print(f'dl11 read_XBUF:{chr(newchar)}')
                # *** this needs to print more intelligently
                # to the user console

        # There are no keyboard events yet.
        # *** when logging ios set up,
        # this will read from the user's console

        return


    # *********************
    # PySimpleGUI Interface
    # VT52 has a multiline and ain input_text
    # These take ~ 1000 uS to read each cycle

    def make_window(self):
        """create the DL11 emulated terminal using PySimpleGUI"""
        print('vt52 make_window begins')
        layout = [[sg.Multiline(size=(80, 24), key='crt', write_only=True,
                                reroute_cprint=True, font=('Courier', 18),
                                text_color='green yellow', background_color='black')],
                  [sg.InputText('', size=(80, 1), focus=True, key='keyboard')]
                  ]
        self.window = sg.Window('VT52', layout, font=('Arial', 18), finalize=True)
        self.window['keyboard'].bind("<Return>", "_Enter")
        print('vt52 make_window done')

        # autoscroll=True,

    def window_cycle(self):
        '''One PySimpleGUI window_cycle'''
        self.sw.start('VT52')
        # This is an attenpt to make the VT52 automatcaly send LF after CR.
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
                sg.cprint(chr(newchar), end='')

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
