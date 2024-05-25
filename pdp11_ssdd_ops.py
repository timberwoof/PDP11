"""pdp11_rss_ops.py double operand instructions"""
import logging
import pdp11_util as u
MASK_WORD = 0o177777
MASK_WORD_MSB = 0o100000
MASK_BYTE_MSB = 0o000200
MASK_LOW_BYTE = 0o000377
MASK_HIGH_BYTE = 0o177400

class ssdd_ops:
    """Implements PDP11 double-operand ssdd instructions"""
    def __init__(self, reg, ram, psw, am, sw):
        logging.debug('initializing DoubleOperandOps')
        self.reg = reg
        self.ram = ram
        self.psw = psw
        self.am = am
        self.sw = sw

        self.double_operand_SSDD_instructions = {}
        # SSDD instructions with B variants the usual way
        self.double_operand_SSDD_instructions[0o010000] = self.MOV
        self.double_operand_SSDD_instructions[0o020000] = self.CMP
        self.double_operand_SSDD_instructions[0o030000] = self.BIT
        self.double_operand_SSDD_instructions[0o040000] = self.BIC
        self.double_operand_SSDD_instructions[0o050000] = self.BIS

        # SSDD instructions that break the rule
        self.double_operand_SSDD_instructions[0o060000] = self.ADDSUB

        self.double_operand_SSDD_instruction_names = {}
        self.double_operand_SSDD_instruction_names[0o010000] = "MOV"
        self.double_operand_SSDD_instruction_names[0o020000] = "CMP"
        self.double_operand_SSDD_instruction_names[0o030000] = "BIT"
        self.double_operand_SSDD_instruction_names[0o040000] = "BIC"
        self.double_operand_SSDD_instruction_names[0o050000] = "BIS"
        self.double_operand_SSDD_instruction_names[0o060000] = "ADD"
        self.double_operand_SSDD_instruction_names[0o110000] = "MOVB"
        self.double_operand_SSDD_instruction_names[0o120000] = "CMPB"
        self.double_operand_SSDD_instruction_names[0o130000] = "BITB"
        self.double_operand_SSDD_instruction_names[0o140000] = "BICB"
        self.double_operand_SSDD_instruction_names[0o150000] = "BISB"
        self.double_operand_SSDD_instruction_names[0o160000] = "SUB"

    # ****************************************************
    # Double-Operand SSDD instructions
    # 01 SS DD through 06 SS DD
    # 11 SS DD through 16 SS DD
    # ****************************************************

    def sign(self, a):
        if abs(a) & MASK_WORD_MSB == MASK_WORD_MSB:
            return -1
        else:
            return 1

    def byte_mask(self, BW, value, target):
        """mask source and result like PDP11 does
        @param BW:
        @param value: new value to stuff into the return value
        @param target: resgiter where it's going
        @return: result with maybe old high byte
        """
        if BW == 'B':
            # Only make the operation affect the low byte
            # The target high byte remains unnafected
            return_value = (value & MASK_LOW_BYTE) | (target & MASK_HIGH_BYTE)
            logging.debug(f'                                  ; byte_mask(value:{bin(value)}, target:{bin(target)}) returns {bin(return_value)}')
        else:
            return_value = value
        return return_value

    def MOV(self, BW, source, dest):
        """01 SS DD move 4-23

        (dst) < (src)"""
        #result = source
        logging.debug(f'                                  ; MOV {bin(source)},{bin(dest)}')
        result = self.byte_mask(BW, source, dest)
        self.psw.set_n(BW, source)
        self.psw.set_z(BW, source)
        self.psw.set_psw(v=0)
        return result, ''

    def CMP(self, BW, source, dest):
        """compare 4-24
        (src)-(dst)"""
        # subtract dest from source
        # set the condition code based on that result
        # but don't change the destination
        #result = source - dest
        result = self.byte_mask(BW, source - dest, dest)
        logging.debug(f'    ; CMP{BW} source:{source} dest:{dest} result:{result}')
        self.psw.set_n(BW, result)
        self.psw.set_z(BW, result)
        self.psw.set_v(BW, result)
        return dest, ''

    def BIT(self, BW, source, dest):
        """bit test 4-28

        (src) ^ (dst)"""
        #
        # Performs logical "and" comparison of the source and destination
        # and modifies condition codes accordingly.
        # Neither the source nor destination operands are affected.
        result = self.byte_mask(BW, source, source & dest)

        logging.debug(f'    BIT source:{source} dest:{dest} result:{result}')
        self.psw.set_n(BW, result)
        self.psw.set_z(BW, result)
        self.psw.set_psw(v=0)
        return result, ''

    def BIC(self, BW, source, dest):
        """bit clear 4-29

        (dst) < ~(src)&(dst)"""
        wsource = ~(source | 0o400000) & MASK_WORD
        result = self.byte_mask(BW, wsource & dest, dest)
        # for byte operations,
        # low-order byte is affected
        # high-order byte is unchanged
        self.psw.set_n(BW, result)
        self.psw.set_z(BW, result)
        self.psw.set_psw(v=0)
        return result, '' #f'    ; BIC{BW}({bin(source)},{bin(dest)}) result: {bin(result)}'

    def BIS(self, BW, source, dest):
        """bit set 4-30
        (dst) < (src) get_v (dst)"""
        result = self.byte_mask(BW, source | dest, dest)
        logging.debug(f'    BIS {oct(source)} {oct(dest)} -> {oct(result)}')
        self.psw.set_n(BW, result)
        self.psw.set_z(BW, result)
        self.psw.set_psw(v=0)
        return result, ''

    def ADDSUB(self, BW, source, dest):
        """06 SS DD: ADD 4-25 (dst) < (src) + (dst)
        | 16 SS DD: SUB 4-26 (dst) < (dst) + ~(src) + 1
        The ADD and SUB instructions use word addressing,
        and have no byte-oriented variations.
        """
        # N set if result < 0, else cleared
        # Z set if result = 0, else cleared
        # for ADD DEC says "set if there was arithmetic overflow as a result of the operation;
        # that is both operands were of the same sign
        # and the result was of the opposite sign;
        # cleared otherwise"
        # for SUB DEC says "set if there was arithmetic overflow as a result of the operation,
        # that is if operands were of opposite signs
        # and the sign of the source was the same as the sign of the result;
        # cleared otherwise"
        # But this is wrong. It doesn't account for 0 operand
        # C: set if there was a carry from the most significant bit of the result; cleared otherwise

        logging.info(f'source:{oct(source)} dest:{oct(dest)}')
        py_source = u.pythonifyPDP11Word(source)
        py_dest = u.pythonifyPDP11Word(dest)
        sS = self.sign(source)
        sD = self.sign(dest)
        v = 0
        c = 0

        # SUB is the "byte" version of ADD
        if BW == 'W': # ADD
            py_result = py_source + py_dest
            pdp11_result = u.PDP11WordifyPythonInteger(py_result)
            logging.info(f'py_source:{py_source} + py_dest:{py_dest} = pdp11_result:{oct(pdp11_result)}')
            sR = self.sign(pdp11_result)
            logging.info(f'sS:{sS} sD:{sD} sR:{sR}')
            if source != 0 and dest != 0 and sS == sD:
                if sS != sR:
                    v = 1
                    c = 1
            if ((source | dest) & MASK_WORD_MSB == MASK_WORD_MSB) and (pdp11_result & MASK_WORD_MSB == 0):
                logging.info('carry')
                c = 1
        else: # SUB DST - SRC
            py_result = py_dest - py_source
            pdp11_result = u.PDP11WordifyPythonInteger(py_result)
            logging.info(f'py_dest:{py_dest} - py_source:{py_source} = py_result:{py_result} pdp11_result:{oct(pdp11_result)}')
            sR = self.sign(pdp11_result)
            logging.info(f'sS:{sS} sD:{sD} sR:{sR}')
            if source != 0 and dest != 0 and sS != sD:
                if sS == sR:
                    v = 1
                    c = 1

        self.psw.set_n('W', pdp11_result)
        self.psw.set_z('W', pdp11_result)
        self.psw.set_psw(v=v, c=c)

        return pdp11_result, ''

    def is_ssdd_op(self, instruction):
        """Using instruction bit pattern, determine whether it's a souble operand instruction"""
        # bits 14 - 12 in [1, 2, 3, 4, 5, 6]
        logging.debug(f'is_ssdd_op {oct(instruction)}&0o070000={instruction & 0o070000}')
        bits14_12 = instruction & 0o070000 in [0o010000, 0o020000, 0o030000, 0o040000, 0o050000, 0o060000]
        return bits14_12

    def do_ssdd_op(self, instruction):
        """dispatch a double-operand opcode.
        parameter: opcode of form * +++ *** *** *** ***
        where +++ = not 000 and not 111 and not 110 """
        # double operands
        # 15-12 opcode
        # 11-6 src
        # 5-0 dst

        #        * +++ *** *** *** *** double operands
        # •1SSDD * 001 *** *** *** *** MOV move source to destination (double)
        # •2SSDD * 010 *** *** *** *** CMP compare src to dst (double)
        # •3SSDD * 011 *** *** *** *** BIT bit test (double)
        # •4SSDD * 100 *** *** *** *** BIC bit clear (double)
        # •5SSDD * 101 *** *** *** *** BIS bit set (double)

        self.sw.start("ssdd")
        self.reg.PC_increment = 0
        if (instruction & 0o100000) >> 15 == 1:
            bw = 'B'
        else:
            bw = 'W'
        opcode = instruction & 0o070000
        name_opcode = instruction & 0o170000

        source = (instruction & 0o007700) >> 6
        dest = instruction & 0o000077
        logging.debug(f'    source_value  = addressing_mode_get')
        source_value, source_register, source_address, operand1, assembly1, source_addressmode = self.am.addressing_mode_get(bw, source)
        logging.debug(f'    dest_value = addressing_mode_get')
        dest_value, dest_register, dest_address, operand2, assembly2, dest_addressmode = self.am.addressing_mode_get(bw, dest)
        logging.debug(f'    S:{oct(source_value)} R:{oct(source_register)} @:{oct(source_address)}  D:{oct(dest_value)} R:{oct(dest_register)} @:{oct(dest_address)}')

        run = True
        logging.debug(f'    result = double_operand_SSDD_instructions')
        try:
            result, report = self.double_operand_SSDD_instructions[opcode](bw, source_value, dest_value)
            assembly = f'{self.double_operand_SSDD_instruction_names[name_opcode]} {assembly1},{assembly2}'
            logging.debug(f'    result:{oct(result)}   NVZC:{self.psw.get_nzvc()}  PC:{oct(self.reg.get_pc())}')
        except KeyError:
            assembly = 'Error: double operand opcode not found'
            result = False

        logging.debug(f'    addressing_mode_set')
        self.am.addressing_mode_set(bw, dest_addressmode, result, dest_register, dest_address)
        self.sw.stop("ssdd")

        return run, operand1, operand2, assembly, report
