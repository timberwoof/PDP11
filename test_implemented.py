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
        for i in range(0o1777):
            opcode = i << 6
            is_op = False
            opcodename = ""
            opcodetype = ""

            if pdp11.br.is_br_op(opcode):
                is_op = True
                try:
                    opcodename = pdp11.br.branch_instruction_names[opcode]
                    opcodetype = "BR"
                except KeyError:
                    opcodename = ""
            elif pdp11.cc_ops.is_cc_op(opcode):
                is_op = True
                opcodename = "CC"
                opcodetype = "CC"
            elif pdp11.noopr_ops.is_noopr_op(opcode):
                is_op = True
                try:
                    opcodename = pdp11.noopr_ops.no_operand_instruction_names[opcode]
                    opcodetype = "NOPR"
                except KeyError:
                    opcodename = ""
            elif pdp11.rss_ops.is_rss_op(opcode):
                is_op = True
                try:
                    opcodename = pdp11.rss_ops.double_operand_RSS_instruction_names[opcode & 0o077000]
                    opcodetype = "RSS"
                except KeyError:
                    opcodename = ""
            elif pdp11.ss_ops.is_ss_op(opcode):
                is_op = True
                try:
                    opcodename = pdp11.ss_ops.single_operand_instruction_names[opcode & 0o107700]
                    opcodetype = "SS"
                except KeyError:
                    opcodename = ""
            elif pdp11.ssdd_ops.is_ssdd_op(opcode):
                is_op = True
                try:
                    opcodename = pdp11.ssdd_ops.double_operand_SSDD_instruction_names[opcode & 0o070000]
                    opcodetype = "SSDD"
                except KeyError:
                    opcodename = ""
            elif pdp11.other_ops.do_other_op(opcode & 0o777700):
                is_op = True
                opcodename = "other"
                opcodetype = "other"

            if not is_op:
                not_ops.append(opcode)
                opcodename = "not"
                opcodetype = "not"


            print(f'{oct(opcode)},{bin(opcode)},{opcodetype},{opcodename}')

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
