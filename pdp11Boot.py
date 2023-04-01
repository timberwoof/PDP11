"""PDP11 bootstrap utilities"""

from pdp11ram import ram
from pdp11reg import reg

class boot:
    def __init__(self, ram, reg):
        print('initializing pdp11Boot')
        self.ram = ram
        self.reg = reg

    # from pdp-11/40 book
    bootstrap_loader = [0o016701, # MOV 0o67:0o0 0o1:0o0
                        0o000240, # 0o000026
                        0o012702, # MOV 0o27:0o0 0o2:0o0
                        0o000240, # 0o000352
                        0o005211, # INC 0o0 0o0 incomplete
                        0o105711, # CLR 0o0 0o1
                        0o100376, # BPL 0o376
                        0o116162, # MOVB 0o61:0o377 0o62:0o377
                        0o000240, # 0o000002 RTI
                        0o000240, # BR 0o0
                        0o005267, # INC 0o770 0o5267
                        0o177756,
                        0o000765, # BR 0o365
                        0o177560, # 0o177560
                        0o000000] #
    # NOP 0o000240
    # 0o000400 BR 00 - what's at 00 now?
    bootaddress = 0o000744

    # http://www.retrocmp.com/how-tos/interfacing-to-a-pdp-1105/146-interfacing-with-a-pdp-1105-test-programs-and-qhello-worldq
    hello_world = [0o012702, # MOV 0o27 0o2
                   0o177566, # serial port+4
                   0o012701, # MOV 0o27 0o1
                   0o002032, # first character in table
                   0o112100, # MOVB 0o21 0o0
                   0o001405, # BEQ 0o5
                   0o110062, # MOVB 0o0 0o62
                   0o000002, #
                   0o105712, # TSTB 0o0 0o0
                   0o100376, # BPL 0o376
                   0o000771, # 0o000771, # BR 0o371 ; transmit next character
                   0o000000, # halt
                   0o000763, # br start
                   0o110,     0o145,     0o154,
                   0o154,     0o157,     0o054,
                   0o040,     0o167,     0o157,
                   0o162,     0o154,     0o144,
                   0o012,     0o000]
    hello_address = 0o2000

    def load_machine_code(self, code, base):
        """Copy the pdp-11 machine code found at code into the address in base

        :param code:
        :param base:
        :return:
        """
        address = base
        for instruction in code:
            # print()
            #print(f'bootaddress:{oct(address)}  instruction: {oct(instruction)}')
            self.ram.write_word(address, instruction)
            #print(f'{oct(address)}:{oct(ram.readword(address))}')
            address = address + 2
        self.reg.set_pc(base, "load_machine_code")

    def octal_to_decimal(self, octal_value):
        decimal_value = 0
        base = 1
        while (octal_value):
            last_digit = octal_value % 10
            octal_value = int(octal_value / 10)
            decimal_value += last_digit * base
            base = base * 8
        return decimal_value

    def read_PDP11_assembly_file(self, file):
        """read a DEC-formatted assembly file with machine code
        :param file: path to file
        :return: address specified in the file
        """
        print (f'read_PDP11_assembly_file "{file}"')
        base = 0
        text = open(file, 'r')
        for line in text:
            #if line.strip() != "":
            #    print (line.strip())
            parts = line.split()

            # if the line is empty, slip it
            if len(parts) == 0:
                continue
            part0 = parts[0]

            # if the line starts with ;, skip it
            if part0 == ';':
                continue

            # first item is the address
            if part0.isnumeric():
                address = self.octal_to_decimal(int(part0))
                # the first address is the base address
                if base == 0:
                    base = address

            # if it doesn't make sense, skip it
            else:
                continue

            # get the next value
            part1 = parts[1]
            if part1.isnumeric():
                value1 = self.octal_to_decimal(int(part1))
                # log what we got. octal, octal, decimal, decimal
                #print(part0, part1, address, value1)
                self.ram.write_word(address, value1)
        return base
