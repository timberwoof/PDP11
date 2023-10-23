# test_implemented.py
# generate all the opcodes and see which ones are not recognized.

from pdp11 import PDP11
from pdp11 import pdp11Run
from pdp11_boot import pdp11Boot

class TestClass():

    def test_opcodes(self):
        print ('testing opcodes')
        pdp11 = PDP11()
        not_ops = []
        for opcode in range(256):
            print(f'testing opcode {opcode}')
            is_op = False

            if pdp11.cc_ops.is_cc_op(opcode):
                is_op = True
            elif pdp11.br.is_br_op(opcode):
                is_op = True
            elif pdp11.noopr_ops.is_noopr_op(opcode):
                is_op = True
            elif pdp11.ss_ops.is_ss_op(opcode):
                is_op = True
            elif pdp11.rss_ops.is_rss_op(opcode):
                is_op = True
            elif pdp11.ssdd_ops.is_ssdd_op(opcode):
                is_op = True
            elif pdp11.other_ops.other_opcode(opcode):
                is_op = True

            if not is_op:
                not_ops.append(opcode)

        print ('found these not-opcodes:')
        print (not_ops)
        previous_opcode = -1
        range_begin = 0
        in_a_range = False
        for opcode in not_ops:
            if in_a_range:
                if opcode == previous_opcode + 1:
                    in_a_range = True
                    previous_opcode = opcode
                else:
                    print(f'{oct(range_begin)}–{oct(previous_opcode)}')
                    in_a_range = False
                    previous_opcode = opcode
            else:
                if opcode == previous_opcode + 1:
                    in_a_range = True
                    range_begin = previous_opcode
                    previous_opcode = opcode
                else:
                    in_a_range = False
                    previous_opcode = opcode

        if in_a_range:
            print(f'{oct(range_begin)}–{oct(previous_opcode)}')
