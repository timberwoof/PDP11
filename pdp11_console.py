"""PDP 11 Console"""
import PySimpleGUI as sg

# https://stackoverflow.com/questions/16938647/python-code-for-serial-data-to-print-on-window
CIRCLE = '⚫'
CIRCLE_OUTLINE = '⚪'
PC_DISPLAY = ''

class Console:
    """PDP11 Console"""
    def __init__(self, pdp11):
        """vt52(ram object, base address for this device)"""
        print(f'initializing console')
        self.pdp11 = pdp11

    def get_pc_text(self):
        """create a display of the program counter"""
        pc_text = ''
        pc = self.pdp11.reg.get_pc()
        mask = 1
        bits = self.ram.top_of_memory
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
    def make_window(self):
        """create the DL11 console using PySimpleGUI"""
        print('console make_window begins')
        layout = [[sg.Text(PC_DISPLAY, key='pc')],
                  [sg.Text(CIRCLE, key='runLED'), sg.Button('Run'), sg.Button('Halt'), sg.Button('Exit')]
                  ]
        self.window = sg.Window('PDP-11 Console', layout, font=('Arial', 18), finalize=True)
        print('console make_window done')

    def cycle(self, cpu_run):
        window_run = True
        event, values = self.window.read(timeout=0)

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

        return window_run, cpu_run

    def close_window(self):
        """close the terminal window"""
        self.window.close()
