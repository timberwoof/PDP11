"""Terminal Emulator doesnt work yet."""
import logging
import PySimpleGUI as sg

class Terminal:
    """Terminal emulator"""
    def __init__(self, dl11, sw):
        logging.info('initializing terminal')
        self.dl11 = dl11
        # throttle window updates because they are very slow
        self.cycles_since_window = 0
        self.buffer = 0  # for holding LF after CR was sent
        self.window = 0
        self.sw = sw

    # ************************************
    # Cycle the terminal
    def cycle(self):
        '''One  window_cycle for terminal'''
        # This is an attenpt to make the terminal automatcaly send LF after CR.
        # If there's a character in our buffer, send it to the DL11
        if self.buffer != 0:
            if self.dl11.RCSR & self.dl11.RCSR_RCVR_DONE == 0:
                self.dl11.write_RBUF(self.buffer)
                self.buffer = 0

        # if there's a character in the dl11 transmit buffer,
        # then eat it
        if self.dl11.XCSR & self.dl11.XCSR_XMIT_RDY == 0:
            logging.info(f'dl11 read_XBUF:{chr(newchar)}')
            # Sure, DL11 can send me nulls; I just won't show them.
            if newchar != 0:
                logging.info(f'dl11 read_XBUF:{chr(newchar)}')
                print (newchar, end ="")

        # there's no way yet to read a character from the keybaord in a non blocking maner.
        # and this can't run from inside the PyCharm console, which is stupid
        #key = " " # bogus
        #if user_key():
        #    if self.dl11.RCSR & self.dl11.RCSR_RCVR_DONE == 0:
        #        self.dl11.write_RBUF(ord(kbd[0:1]))

        return
