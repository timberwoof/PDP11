"""pdp11_single_operand_ops.py single oprand instructions"""

MASK_WORD = 0o177777
MASK_WORD_MSB = 0o100000
MASK_BYTE_MSB = 0o000200
MASK_LOW_BYTE = 0o000377
MASK_HIGH_BYTE = 0o177400

class SingleOperandOps:
    """Implements PDP11 single-operand instructions"""
    def __init__(self, reg, ram, psw, am, sw):
        print('initializing SingleOperandOps')
        self.reg = reg
        self.ram = ram
        self.psw = psw
        self.am = am
        self.sw = sw

        # ****************************************************
        # Single-Operand instructions -
        # 00 50 DD - 00 77 DD
        # 10 50 DD - 10 77 DD
        # ****************************************************
        self.single_operand_instructions = {}
        self.single_operand_instructions[0o000100] = self.JMP
        self.single_operand_instructions[0o000300] = self.SWAB

        self.single_operand_instructions[0o005000] = self.CLR
        self.single_operand_instructions[0o005100] = self.COM
        self.single_operand_instructions[0o005200] = self.INC
        self.single_operand_instructions[0o005300] = self.DEC
        self.single_operand_instructions[0o005400] = self.NEG
        self.single_operand_instructions[0o005500] = self.ADC
        self.single_operand_instructions[0o005600] = self.SBC
        self.single_operand_instructions[0o005700] = self.TST
        self.single_operand_instructions[0o006000] = self.ROR
        self.single_operand_instructions[0o006100] = self.ROL
        self.single_operand_instructions[0o006200] = self.ASR
        self.single_operand_instructions[0o006300] = self.ASL
        self.single_operand_instructions[0o006400] = self.MARK
        self.single_operand_instructions[0o006500] = self.MFPI
        self.single_operand_instructions[0o006600] = self.MTPI
        self.single_operand_instructions[0o006700] = self.SXT

        self.single_operand_instructions[0o105000] = self.CLR  # CLRB
        self.single_operand_instructions[0o105100] = self.COM  # COMB
        self.single_operand_instructions[0o105200] = self.INC  # INCB
        self.single_operand_instructions[0o105300] = self.DEC  # DECB
        self.single_operand_instructions[0o105400] = self.NEG  # NEGB
        self.single_operand_instructions[0o105500] = self.ADC  # ADCB
        self.single_operand_instructions[0o105600] = self.SBC  # SBCB
        self.single_operand_instructions[0o105700] = self.TST  # TSTB
        self.single_operand_instructions[0o106000] = self.ROR  # RORB
        self.single_operand_instructions[0o106100] = self.ROL  # ROLB
        self.single_operand_instructions[0o106200] = self.ASR  # ASRB
        self.single_operand_instructions[0o106300] = self.ASL  # ASLB
        self.single_operand_instructions[0o106400] = self.MTPS
        self.single_operand_instructions[0o106500] = self.MFPD
        self.single_operand_instructions[0o106600] = self.MTPD
        self.single_operand_instructions[0o106700] = self.MFPS

        self.single_operand_instruction_names = {}
        self.single_operand_instruction_names[0o000100] = "JMP"
        self.single_operand_instruction_names[0o000300] = "SWAB"

        self.single_operand_instruction_names[0o005000] = "CLR"
        self.single_operand_instruction_names[0o005100] = "COM"
        self.single_operand_instruction_names[0o005200] = "INC"
        self.single_operand_instruction_names[0o005300] = "DEC"
        self.single_operand_instruction_names[0o005400] = "NEG"
        self.single_operand_instruction_names[0o005500] = "ADC"
        self.single_operand_instruction_names[0o005600] = "SBC"
        self.single_operand_instruction_names[0o005700] = "TST"
        self.single_operand_instruction_names[0o006000] = "ROR"
        self.single_operand_instruction_names[0o006100] = "ROL"
        self.single_operand_instruction_names[0o006200] = "ASR"
        self.single_operand_instruction_names[0o006300] = "ASL"
        self.single_operand_instruction_names[0o006400] = "MARK"
        self.single_operand_instruction_names[0o006500] = "MFPI"
        self.single_operand_instruction_names[0o006600] = "MTPI"
        self.single_operand_instruction_names[0o006700] = "SXT"

        self.single_operand_instruction_names[0o105000] = "CLRB"
        self.single_operand_instruction_names[0o105100] = "COMB"
        self.single_operand_instruction_names[0o105200] = "INCB"
        self.single_operand_instruction_names[0o105300] = "DECB"
        self.single_operand_instruction_names[0o105400] = "NEGB"
        self.single_operand_instruction_names[0o105500] = "ADCB"
        self.single_operand_instruction_names[0o105600] = "SBCB"
        self.single_operand_instruction_names[0o105700] = "TSTB"
        self.single_operand_instruction_names[0o106000] = "RORB"
        self.single_operand_instruction_names[0o106100] = "ROLB"
        self.single_operand_instruction_names[0o106200] = "ASRB"
        self.single_operand_instruction_names[0o106300] = "ASLB"
        self.single_operand_instruction_names[0o106400] = "MTPS"
        self.single_operand_instruction_names[0o106500] = "MFPD"
        self.single_operand_instruction_names[0o106600] = "MTPD"
        self.single_operand_instruction_names[0o106700] = "MFPS"

        self.single_operand_instruction_texts = {}
        self.single_operand_instruction_texts[0o000100] = "jump"
        self.single_operand_instruction_texts[0o000300] = "swap bytes"

        self.single_operand_instruction_texts[0o005000] = "clear destination"
        self.single_operand_instruction_texts[0o005100] = "complement"
        self.single_operand_instruction_texts[0o005200] = "increment"
        self.single_operand_instruction_texts[0o005300] = "decrement"
        self.single_operand_instruction_texts[0o005400] = "negative"
        self.single_operand_instruction_texts[0o005500] = "add carry"
        self.single_operand_instruction_texts[0o005600] = "subtract carry"
        self.single_operand_instruction_texts[0o005700] = "test"
        self.single_operand_instruction_texts[0o006000] = "rotate right"
        self.single_operand_instruction_texts[0o006100] = "rotate left"
        self.single_operand_instruction_texts[0o006200] = "arithmetic shift right"
        self.single_operand_instruction_texts[0o006300] = "arithmetic shift left"
        self.single_operand_instruction_texts[0o006400] = "subroutine cleanup"
        self.single_operand_instruction_texts[0o006500] = "move from previous instruction space"
        self.single_operand_instruction_texts[0o006600] = "move to previous instruction space"
        self.single_operand_instruction_texts[0o006700] = "sign extend"

        self.single_operand_instruction_texts[0o105000] = "clear destination byte"
        self.single_operand_instruction_texts[0o105100] = "complement byte"
        self.single_operand_instruction_texts[0o105200] = "increment byte"
        self.single_operand_instruction_texts[0o105300] = "decrement byte"
        self.single_operand_instruction_texts[0o105400] = "negative byte"
        self.single_operand_instruction_texts[0o105500] = "add carry byte"
        self.single_operand_instruction_texts[0o105600] = "subtract carry byte"
        self.single_operand_instruction_texts[0o105700] = "test byte"
        self.single_operand_instruction_texts[0o106000] = "rotate right byte"
        self.single_operand_instruction_texts[0o106100] = "rotate left byte"
        self.single_operand_instruction_texts[0o106200] = "arithmetic shift right byte"
        self.single_operand_instruction_texts[0o106300] = "arithmetic shift left byte"
        self.single_operand_instruction_texts[0o106400] = "move to PSW"
        self.single_operand_instruction_texts[0o106500] = "move from previous data space"
        self.single_operand_instruction_texts[0o106600] = "move to previous data space"
        self.single_operand_instruction_texts[0o106700] = "move from psw"

    def mask(self, value, B):
        """Apply the correct byte or word mask to the value"""
        result = 0o0
        if B == "B":
            result = value & MASK_LOW_BYTE
        else:
            result = value & MASK_WORD
        return result

    def JMP(self, operand, B):
        """00 01 DD JMP jump 4-56"""
        # print(f'JMP calling set_pc({oct(operand)})')
        self.reg.set_pc(operand, 'JMP')
        return operand

    def SWAB(self, operand, B):
        """00 03 DD Swap Bytes 4-17"""
        # Exchanges high-order byte and low-order byte of the destina- tion word
        # get_n: set if high-order bit of low-order byte (bit 7) of result is set; cleared otherwise
        # get_z: set if low-order byte of result = 0; cleared otherwise
        # get_v: cleared
        # get_c: cleared
        result = ((operand & 0xFF00) >> 8) + ((operand & 0x00FF) << 8)
        self.psw.set_n("B", result & 0x00FF)
        self.psw.set_z("B", result & 0x00FF)
        self.psw.set_psw(v=0, c=0)
        return result

    def CLR(self, operand, B):
        """00 50 DD Clear Destination"""
        result = 0o0
        self.psw.set_psw(n=0, z=1, v=0, c=0)
        return result

    def COM(self, operand, B):
        """00 51 DD Complement Destination"""
        # Replaces the contents of the destination address by their logical complement
        # (each bit equal to 0 is set and each bit equal to 1 is cleared)
        result = ~operand
        self.psw.set_n(B, result)
        self.psw.set_z(B, result)
        self.psw.set_psw(v=0, c=1)
        return result

    def INC(self, operand, B):
        """00 52 DD Increment Destination"""
        result = operand + 1
        self.psw.set_v(B, result)
        self.psw.set_n(B, result)
        self.psw.set_z(B, result)
        return result

    def DEC(self, operand, B):
        """00 53 DD Decrement Destination"""
        result = operand - 1
        self.psw.set_v(B, result)
        self.psw.set_n(B, result)
        self.psw.set_z(B, result)
        return result

    def NEG(self, operand, B):
        """00 54 DD negate Destination"""
        result = -operand
        self.psw.set_v(B, result)
        self.psw.set_n(B, result)
        self.psw.set_z(B, result)
        if result == 0:
            C = 1
        else:
            C = 0
        return self.mask(result, B)

    def ADC(self, operand, B):
        """00 55 DD Add Carry"""
        result = operand + self.psw.get_c()
        return self.mask(result, B)

    def SBC(self, operand, B):
        """00 56 DD Subtract Carry"""
        result = operand - self.psw.get_c()
        return self.mask(result, B)

    def TST(self, operand, B):
        """00 57 DD Test Destination"""
        self.psw.set_n(B, operand)
        self.psw.set_z(B, operand)
        self.psw.set_psw(v=0, c=0)
        return operand

    def ROR(self, operand, B):
        """00 60 DD ROR rotate right"""
        # Rotates all bits of the destination right one place.
        # Bit 0 is loaded into the get_c-bit and
        # the previous contents of the get_c-bit are loaded into bit 15 of the destination.
        # get_n: set if the high-order bit of the result is set (result < 0); cleared otherwise
        # get_z: set if all bits of result = 0; cleared otherwise
        # get_v: loaded with the Exclusive OR of the get_n-bit and get_c-bit
        # (as set by the completion of the rotate operation)
        # get_c: loaded with the low-order bit of the destination
        rotatebit = operand & 0o01
        if B == "B":
            bits = 8
        else:
            bits = 16
        result = operand >> 1 + rotatebit << bits
        N = self.psw.set_n(B, result)
        Z = self.psw.set_z(B, result)
        C = result & 0o01
        V = N ^ C
        self.psw.set_psw(n=N, z=Z, v=V, c=C)
        return self.mask(result, B)

    def ROL(self, operand, B):
        """00 61 DD ROL rotate left"""
        # Rotate all bits of the destination left one place.
        # Bit 15 is loaded into the get_c·bit of the status word and
        # the previous contents of the get_c-bit are loaded into Bit 0 of the destination.
        # get_n: set if the high-order bit of the result word is set
        # (result < 0): cleared otherwise
        # get_z: set if all bits of the result word =0; cleared otherwise
        # get_v: loaded with the Exclusive OR of the get_n-bit and get_c-bit
        # (as set by the completion of the rotate operation)
        # get_c: loaded with the high-order bit of the destination
        if B == "B":
            msb = MASK_WORD_MSB & operand
            bits = 8
        else:
            msb = MASK_BYTE_MSB & operand
            bits = 16
        rotatebit = operand & msb
        result = operand << 1 + rotatebit >> bits
        N = self.psw.set_n(B, result)
        Z = self.psw.set_z(B, result)
        C = result & msb >> bits
        V = N ^ C
        self.psw.set_psw(n=N, z=Z, v=V, c=C)
        return self.mask(result, B)

    def ASR(self, operand, B):
        """00 62 DD ASR arithmetic shift right"""
        # Shifts all bits of the destination right one place. Bit 15 is replicated.
        # get_n: set if the high-order bit of the result is set (result < 0); cleared otherwise
        # get_z: set if the result = 0; cleared otherwise
        # get_v: loaded from the Exclusive OR of theN-bit and get_c-bit
        # (as set by the completion of the shift operation)
        # get_c: loaded from low-order bit of the destination
        if B == "B":
            msb = MASK_WORD_MSB & operand
        else:
            msb = MASK_BYTE_MSB & operand
        result = (operand >> 1) | msb
        N = self.psw.set_n(B, result)
        Z = self.psw.set_z(B, result)
        C = result & 0o01
        V = N ^ C
        self.psw.set_psw(n=N, z=Z, v=V, c=C)
        return result

    def ASL(self, operand, B):
        """00 63 DD ASL arithmetic shift left"""
        # Shifts all bits of the destination left one place. Bit 0 is loaded with an 0.
        # get_n: set if high-order bit of the result is set (result < 0); cleared otherwise
        # get_z: set if the result =0; cleared otherwise
        # get_v: loaded with the exclusive OR of the get_n-bit and get_c-bit
        # (as set by the completion of the shift operation)
        # get_c: loaded with the high-order bit of the destination
        result = operand << 1
        if B == "B":
            msb = MASK_WORD_MSB & result
            bits = 8
        else:
            msb = MASK_BYTE_MSB & result
            bits = 16
        N = self.psw.set_n(B, result)
        Z = self.psw.set_z(B, result)
        C = result & msb >> bits
        V = N ^ C
        self.psw.set_psw(n=N, z=Z, v=V, c=C)
        return result

    def SXT(self, operand, B):
        """00 67 DD Sign Extend"""
        # (dst)<- 0 if get_n bit is clear
        # (dst)<- -1 get_n bit is set
        # get_z: set if get_n bit clear
        if self.psw.get_n() == 0:
            result = 0
            Z = 1
        else:
            result = 1
            Z = self.psw.get_z()
        self.psw.set_psw(z=Z)
        return result

    def MARK (self, operand, B):
        # standard PDP11 subroutine return
        # stack operation LSI11-03
        print('MARK **** not implemented')
        return operand

    def MTPS (self, operand, B):
        # move byte to PSW
        # stack operation LSI11-03
        print('MTPS **** not implemented')
        return operand

    def MFPI (self, operand, B):
        # Move from Previous Instruction Space
        # MMU instruction not in LSI11-03
        print('MFPI NOT IMPLEMENTED')
        return operand

    def MTPI (self, operand, B):
        # move to previous instruction space
        # MMU instruction not in LSI11-03
        print('MTPI NOT IMPLEMENTED')
        return operand

    def MFPS (self, operand, B):
        # Not PDP11-40
        # MMU instruction not in LSI11-03
        print('MFPS NOT IMPLEMENTED')
        return operand

    def MFPD(self, operand, B):
        """10 65 SS Move from previous data space"""
        # MMU instruction not in LSI11-03
        print('MFPD NOT IMPLEMENTED')
        return operand

    def MTPD(self, operand, B):
        """10 66 SS Move to previous data space"""
        # MMU instruction not in LSI11-03
        print('MTPD NOT IMPLEMENTED')
        return operand

    def is_single_operand(self, instruction):
        """Using instruction bit pattern, determine whether it's a single-operand instruction"""
        # 15  12 10  876 543 210
        #  * 000 101 *** *** ***
        #  * 000 110 *** *** ***
        # bit 15 can be 1 or 0
        # bits 14,13,12 must be 0
        # bits 11,10,9 must be 5 or 6
        # bits 8,7,6 can be anything
        # bits 5-0 can be anything
        # 0o000301 is one of these
        # 0 000 000 101 *** ***
        # print(f'    is_single_operand({oct(instruction)})')
        bits_14_13_12 = instruction & 0o070000 == 0o000000
        bits_11_10_9 = instruction & 0o007000 in [0o006000, 0o005000]
        is_jmp = instruction & 0o177700 == 0o000100
        is_swab = instruction & 0o177700 == 0o000300
        # print(f'    is_single_operand {bits_14_13_12} {bits_11_10_9} {is_swab}  {is_jmp}')
        return (bits_14_13_12 and bits_11_10_9) or is_swab or is_jmp

    def do_single_operand(self, instruction):
        """dispatch a single-operand opcode"""
        # parameter: opcode of form * 000 1** *** *** ***
        # single operands
        # 15-6 opcode
        # 15 is 1 to indicate a byte instruction
        # 15 is 0 to indicate a word instruction
        # 5-0 dst

        self.sw.start("single operand")

        # is it a Byte or Word instruction?
        if (instruction & 0o100000) == 0o100000:
            BW = 'B'
        else:
            BW = ''
        source = instruction & 0o000077
        opcode = instruction & 0o107700
        run = True
        if opcode == 0o000100:
            # special handling for JMP with R7.
            run, source_value, parameter = self.am.addressing_mode_jmp(source)
            report = f'{self.single_operand_instruction_names[opcode]} {parameter}'
            result = self.single_operand_instructions[opcode](source_value, BW)
        else:
            source_value, out_register, out_address, operand = self.am.addressing_mode_get(BW, source)
            report = f'{self.single_operand_instruction_names[opcode]} {operand}'
            try:
                result = self.single_operand_instructions[opcode](source_value, BW)
                #print(f'    result:{oct(result)}  source_value:{oct(source_value)}  out_address:{oct(out_address)}  ')
                self.am.addressing_mode_set(BW, result, out_register, out_address)
            except KeyError:
                report = 'Error: single-operand opcode not found'
                result = False

        self.sw.stop("single operand")
        return run, report
