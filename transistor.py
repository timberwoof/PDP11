'''
This is a program to calculate the transistor bias resistors
for a basic Common Emitter amp stage, with series feedback, using Bipolar transistors.
It is up to you to assume the ground reference as positive or negative,
depending on the makeup of the transistor, (NPN or PNP). These are just
ballpark values, using first order calculations using rule of thumb
methods to get the values. The resistor values are approximations, it is
up to you to decide what values to use in the final design.
'''

import sys
import textwrap


def print_help():
    wrapper = textwrap.TextWrapper(width=50, initial_indent=' | ', subsequent_indent=' | ')
    for line in wrapper.wrap(__doc__.strip()):
        print(line)


class ExitApp(Exception):
    pass


def print_newlines(n):
    print('\n' * n, end='')


def get_input_as(question, type=float, prompt=' >> ', exit_text='e'):
    while True:
        value = input(question + prompt)
        if value.lower().strip() == exit_text:
            raise ExitApp()
        try:
            value = float(value)
        except ValueError:
            print(f"{value} is not a float")
            continue
        else:
            return value


def get_parameters():
    print_newlines(3)
    amp = dict.fromkeys(["VCC", "RC", "Av", "Beta"])
    print("Entering ( e ) exits out anytime")
    for param in amp:
        try:
            value = get_input_as(f'Please enter the parameter for {param}', float)
        except ExitApp:
            sys.exit(0)
        amp[param] = value
    return amp


def do_math1(VCC, RC, **args):
    '''
    This function takes only VCC and RC.
    Other keywords are not used. **args allows this.
    '''
    # some calculations
    return 'your result'


if __name__ == '__main__':
    print_help()
    parameters = get_parameters()
    print(parameters)

    do_math1(**parameters)  # Av and Beta is not used in this function
    # but you do also this
    do_math1(parameters['VCC'], parameters['RC'])
    # or
    vcc = parameters['VCC']
    rc = parameters['RC']
    do_math1(vcc, rc)