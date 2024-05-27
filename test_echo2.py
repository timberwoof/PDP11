# test_echo.py
# load a small pdp11 program that echoes inputs back to outputs
from stopwatches import StopWatches
import random
import logging

from pdp11 import PDP11
from pdp11 import pdp11Run
from pdp11_boot import pdp11Boot

MASK_WORD = 0o177777
MASK_WORD_MSB = 0o100000
MASK_BYTE_MSB = 0o000200
MASK_LOW_BYTE = 0o000377
MASK_HIGH_BYTE = 0o177400

# *** This needs to be improved by spawning PDP11 off
# into anotehr tread that's running thos cdode.
# Then in the test thread, push a buynch of characters into
# the DL11 and read them out and verify correct statuses.
# This is to verify whether the same bug happens when
# sending characters into the CPU.
# This would use code very much like the VT52Console.

# http://www.retrocmp.com/how-tos/interfacing-to-a-pdp-1105/146-interfacing-with-a-pdp-1105-test-programs-and-qhello-worldq
echo = [0o012700, 0o177560,  # start: mov #kbs, r0
        0o105710,  # wait: tstb (r0)       ; character received?
        0o100376,  # bpl wait        ; no, loop
        0o016060, 0o000002, 0o000006,  # mov 2(r0),6(r0) ; transmit data
        0o000772]  # br wait         ; get next character
echo_address = 0o001000

class TestClass():

    def character_generator(self):
        characters = "qwertyuiopasdfghjklzxcvbnm"
        index = random.randrange(len(characters))
        return characters[index:index+1]

    def wait_for_rcsr_done_get_lock(self):
        """get lock, read RCSR. If it's done, keep the lock"""
        logging.debug('wait_for_rcsr_done_get_lock')
        self.pdp11.lock.acquire()
        rcsr = self.pdp11.dl11.read_RCSR()
        while (rcsr & self.pdp11.dl11.RCSR_RCVR_DONE) != 0:
            #logging.debug('wait_for_rcsr_done_get_lock loop')
            self.pdp11.lock.release()
            time.sleep(0.1)
            self.pdp11.lock.acquire()
            rcsr = self.pdp11.dl11.read_RCSR()
        logging.debug('got RCSR_DONE and lock')
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
        self.pdp11.lock.release()
        #logging.debug(f'vt52 release lock {self.window_cycles}')

        event, values = self.window.read(timeout=0)
        # If the Enter key was hit
        # then send CR to the serial interface
        if event == 'keyboard_Enter':
            self.window['keyboard'].Update('')
            #logging.debug(f'{self.window_cycles} sending DL11 0o12 "CR"')
            self.wait_for_rcsr_done_get_lock()
            self.dl11.write_RBUF(0o15)
            #logging.debug(f'vt52 released lock {self.window_cycles}')
            self.pdp11.lock.release()

        # If there's a keyboard event
        # then send the character to the serial interface
        kbd = values['keyboard']
        if kbd != '':
            self.window['keyboard'].Update('')
            o = ord(kbd[0:1])
            #logging.debug(f'{self.window_cycles} sending DL11 {o} {self.safe_character(o)}')
            self.wait_for_rcsr_done_get_lock()
            self.dl11.write_RBUF(o)
            #logging.debug(f'vt52 released lock {self.window_cycles}')
            self.pdp11.lock.release()

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

    def run_with_VT52_emulator(self):
        """run PDP11 with a PySimpleGUI terminal window."""
        logging.info('run_with_VT52_emulator: begin PDP11 emulator')
        logging.info(f'{self.pdp11.reg.registers_to_string()} NZVC:{self.pdp11.psw.get_nzvc()}')

        # Create and run the terminal window in PySimpleGUI
        logging.info('run_with_VT52_emulator make windows')
        vt52_window = self.pdp11.vt52.make_window()
        self.pdp11.set_run(False)
        was_cpu_run = True # We want the CPU to start
        console_run = True
        character_count = 0

        logging.info(f'run_with_VT52_emulator begins.')
        while console_run and character_count < 10:

            # window cycle
            console_run = self.pdp11.vt52.window_cycle()  # may set cu flag
            logging.info(f'console_run:{console_run}')

            # start the CPU
            # Check for whether we need to start or stop the CPU thread.
            # Start CPU here instead of in startup because console has to start and stop it.
            self.pdp11.runEvent.wait()  # wait for flag set
            self.pdp11.runEvent.clear()  # clear flag
            if (self.pdp11.run != was_cpu_run):  # if run changed
                if was_cpu_run:
                    self.pdp11.sw.stop("CPU")
                    logging.info('stop CPU thread')
                    self.pdp11.set_run(False)
                else:  # was_cpu_run == FALSE
                    logging.info('start CPU thread')
                    self.pdp11.set_run(True)
                    self.cpuThread = threading.Thread(target=self.cpuThread, args=(self.pdp11,), daemon=True)
                    self.cpuThread.start()
                    self.pdp11.sw.start("CPU")
                was_cpu_run = self.pdp11.run
            self.pdp11.runEvent.set()  # set the flag

            # inject a random haracter into the DL11
            character_count = character_count + 1
            character = self.character_generator()
            self.wait_for_rcsr_done_get_lock()
            self.pdp11.dl11.write_RBUF(ord(character))
            RCSR = self.pdp11.dl11.RCSR
            if (RCSR & self.pdp11.dl11.RCSR_RCVR_DONE) != self.pdp11.dl11.RCSR_RCVR_DONE:
                logging.error(f'XCSR {oct(RCSR)} was not set with {oct(self.pdp11.dl11.RCSR_RCVR_DONE)}')
            else:
                logging.info(f'XCSR {oct(RCSR)} was set with {oct(self.pdp11.dl11.RCSR_RCVR_DONE)}')

            logging.info(f'console_run:{console_run}  was_cpu_run:{was_cpu_run}')

        logging.info(f'run_with_VT52_emulator ends.')
        self.pdp11.am.address_mode_report()
        self.pdp11.sw.report()

    def test_character_generator(self):
        character_count = 0
        blort = ''
        while character_count < 10:
            blort = blort + self.character_generator()
            character_count = character_count + 1
        logging.info(blort)
        assert len(blort) == 10

    def test_echo(self):
        self.pdp11 = PDP11(True)
        logging.info('test_echo begins')
        boot = pdp11Boot(self.pdp11.reg, self.pdp11.ram)
        logging.info('test_echo load_machine_code()')
        boot.load_machine_code(echo, echo_address)
        self.pdp11.reg.set_pc(echo_address, "load_machine_code")
        self.pdp11.ram.dump(echo_address, echo_address+0o10)
        run = pdp11Run(self.pdp11)
        self.run_with_VT52_emulator()



    def close_window(self):
        """close the terminal window"""
        self.window.close()
