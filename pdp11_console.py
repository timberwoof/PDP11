"""PDP 11 Console: Blinky Lights for PDP11 emulator"""
import logging
import PySimpleGUI as sg

# https://stackoverflow.com/questions/16938647/python-code-for-serial-data-to-print-on-window
CIRCLE = '⚫'
CIRCLE_OUTLINE = '⚪'

class Console:
    """PDP11 Console: Blinky Lights for PDP11 emulator"""
    def __init__(self, pdp11, sw):
        """vt52(ram object, base address for this device)"""
        logging.info('initializing console')
        self.pdp11 = pdp11
        self.window = 0
        self.sw = sw

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

    # *********************
    # PySimpleGUI Interface
    # console has Text, Text, Text, Button, Button, Button
    # and takes 16000 microseconds to read

    def make_window(self):
        """create the DL11 console using PySimpleGUI"""
        logging.info('console make_window begins')
        pc_display = oct(self.pdp11.reg.get_pc())
        pc_lights = self.pc_to_blinky_lights()
        layout = [[sg.Text(pc_display, key='pc_display'), sg.Text(pc_lights, key='pc_lights')],
                  [sg.Text(CIRCLE, key='runLED'), sg.Button('Run'), sg.Button('Halt'), sg.Button('Exit')]
                  ]
        self.window = sg.Window('PDP-11 Console', layout, location=(50,50),
                                font=('Arial', 18), finalize=True)
        logging.info('console make_window done')

    def cycle(self, cpu_run):
        '''one console window update window_cycle'''
        self.sw.start('console')
        window_run = True

        pc_display = self.window['pc_display']
        pc_display.update(oct(self.pdp11.reg.get_pc()))

        pc_lights = self.window['pc_lights']
        pc_lights.update(self.pc_to_blinky_lights())

        # mean duration 16000 microseconds:
        self.sw.start('console read')
        event, values = self.window.read(timeout=0)
        self.sw.stop('console read')

        if event in (sg.WIN_CLOSED, 'Quit'):  # if user closes window or clicks cancel
            window_run = False
        elif event == "Run":
            cpu_run = True
            text = self.window['runLED']
            text.update(CIRCLE_OUTLINE)
        elif event == "Halt":
            cpu_run = False
            text = self.window['runLED']
            text.update(CIRCLE)
        elif event == "Exit":
            cpu_run = False
            window_run = False

        self.sw.stop('console')
        return window_run, cpu_run

    def close_window(self):
        """close the terminal window"""
        self.window.close()
