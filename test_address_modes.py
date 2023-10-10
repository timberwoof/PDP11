from pdp11_hardware import Registers as reg
from pdp11_hardware import Ram
from pdp11_hardware import PSW
from pdp11_hardware import Stack
from pdp11_hardware import AddressModes as am
from pdp11_single_operand_ops import SingleOperandOps as sopr
from pdp11_double_operand_ops import DoubleOperandOps as dopr
from stopwatches import StopWatches as sw

MASK_WORD = 0o177777
MASK_WORD_MSB = 0o100000
MASK_BYTE_MSB = 0o000200
MASK_LOW_BYTE = 0o000377
MASK_HIGH_BYTE = 0o177400

class TestClass():
    reg = reg()
    ram = Ram(reg)
    psw = PSW(ram)
    stack = Stack(reg, ram, psw)
    am = am(reg, ram, psw)
    sw = sw()
    dopr = dopr(reg, ram, psw, am, sw)
    sopr = sopr(reg, ram, psw, am, sw)

    R0 = 0
    R1 = 1
    R2 = 2
    R3 = 3
    R4 = 4
    R5 = 5

    mode0 = 0
    mode1 = 1
    mode2 = 2
    mode3 = 3
    mode4 = 4
    mode5 = 5
    mode6 = 6
    mode7 = 7

    def SS(self, mode, register):
        return (mode<<3 | register) << 6

    def DD(self, mode, register):
        return (mode<<3 | register)

    def ADD(self, modeS=0, regS=0, modeD=0, regD=1):
        return 0o060000 | self.SS(modeS, regS) | self.DD(modeD, regD)

    # *****************************************
    # Mode 0

    def test_mode_0_SD(self):
        print('test_mode_0 register source destination')
        # registers contain operands
        # MOV R1,3
        # MOV R2,1
        # ADD R1, R2

        a = 3
        b = 1

        self.psw.set_psw(psw=0)
        self.reg.set(1, a)
        self.reg.set(2, b)
        instruction = self.ADD(modeS=0, regS=1, modeD=0, regD=2)
        print(oct(instruction))
        assert self.dopr.is_double_operand_SSDD(instruction)
        self.dopr.do_double_operand_SSDD(instruction)

        sum = self.reg.get(2)
        assert sum == a + b

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    # *****************************************
    # Mode 1 Register Deferred
    # Register contains address of the operand

    def test_mode_1_S(self):
        print('test_mode_1 register deferred Source')
        # register contains address of operand
        address = 0o2763
        a = 0o101
        b = 0o2136

        self.ram.write_word(address, a)
        self.reg.set(1, address)
        self.reg.set(2, b)
        instruction = self.ADD(modeS=1, regS=1, modeD=0, regD=2)
        print(oct(instruction))
        assert self.dopr.is_double_operand_SSDD(instruction)
        self.dopr.do_double_operand_SSDD(instruction)

        sum = self.reg.get(2)
        assert sum == a + b

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    def test_mode_1_D(self):
        print('test_mode_1 register deferred Destination')
        # register contains address of operand
        address = 0o2763
        a = 0o101
        b = 0o2136

        self.ram.write_word(address, a)
        self.reg.set(2, address)
        self.reg.set(1, b)
        instruction = self.ADD(modeS=0, regS=1, modeD=1, regD=2)
        print(oct(instruction))
        assert self.dopr.is_double_operand_SSDD(instruction)
        self.dopr.do_double_operand_SSDD(instruction)

        sum = self.ram.read_word(address)
        assert sum == a + b

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"


    def test_mode_1_SD(self):
        print('test_mode_1 register deferred Source Destination')
        # register contains address of operand
        addressA = 0o2763
        A = 0o101
        addressB = 0o1234
        B = 0o2136

        self.ram.write_word(addressA, A)
        self.reg.set(1, addressA)
        self.ram.write_word(addressB, B)
        self.reg.set(2, addressB)
        instruction = self.ADD(modeS=1, regS=1, modeD=1, regD=2)
        print(oct(instruction))  # 0o60102
        assert self.dopr.is_double_operand_SSDD(instruction)
        self.dopr.do_double_operand_SSDD(instruction)

        sum = self.ram.read_word(addressB)
        assert sum == A + B

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    # *****************************************
    # Mode 2 Autoincrement
    # Register contains accress of operand
    # then incremented

    def test_mode_2_S(self):
        print('test_mode_2 autoincrement source')
        address = 0o2763
        a = 0o101
        b = 0o2136

        self.ram.write_word(address, a)
        self.reg.set(1, address)
        self.reg.set(2, b)

        instruction = self.ADD(modeS=2, regS=1, modeD=0, regD=2)
        print(oct(instruction))
        assert self.dopr.is_double_operand_SSDD(instruction)
        self.dopr.do_double_operand_SSDD(instruction)

        sum = self.reg.get(2)
        assert sum == a + b

        r1 = self.reg.get(1)
        assert address+2 == r1

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"


    def test_mode_2_D(self):
        print('test_mode_2 autoincrement destination')
        a = 0o101
        b = 0o2136
        address = 0o2763
        self.reg.set(1, a)
        self.ram.write_word(address, b)
        self.reg.set(2, address)
        expected_sum = a + b

        instruction = self.ADD(modeS=0, regS=1, modeD=2, regD=2)
        print(oct(instruction))  # 0o60102
        assert self.dopr.is_double_operand_SSDD(instruction)
        self.dopr.do_double_operand_SSDD(instruction)

        actual_sum = self.ram.read_word(address)
        assert expected_sum == actual_sum

        assert address+2 == self.reg.get(2)

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    def test_mode_2_SD(self):
        print('test_mode_2 autoincrement source destination')
        a = 0o101
        b = 0o2136
        source_address = 0o2763
        destination_address = 0o1312
        self.reg.set(1, source_address)
        self.ram.write_word(source_address, a)
        self.reg.set(2, destination_address)
        self.ram.write_word(destination_address, b)
        expected_sum = a + b

        instruction = self.ADD(modeS=2, regS=1, modeD=2, regD=2)
        print(oct(instruction))
        assert self.dopr.is_double_operand_SSDD(instruction)
        self.dopr.do_double_operand_SSDD(instruction)

        actual_sum = self.ram.read_word(destination_address)
        assert expected_sum == actual_sum

        assert source_address+2 == self.reg.get(1)
        assert destination_address+2 == self.reg.get(2)

    # *****************************************
    # Mode 3 Autoincrement Deferred
    # Register contains pointer to address of operand
    # then is incremented by 2

    def test_mode_3_S(self):
        print('test_mode_3 autoincrement deferred source')
        address = 0o2763
        a = 0o101
        b = 0o2136

        self.ram.write_word(address, a)
        self.reg.set(1, address)
        self.reg.set(2, b)

        instruction = self.ADD(modeS=2, regS=1, modeD=0, regD=2)
        print(oct(instruction))
        assert self.dopr.is_double_operand_SSDD(instruction)
        self.dopr.do_double_operand_SSDD(instruction)

        sum = self.reg.get(2)
        assert sum == a + b

        r1 = self.reg.get(1)
        assert address+2 == r1

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"


    #def test_mode_3_D(self):
    #    print('test_mode_3 autoincrement deferred destination')

    #def test_mode_3_SD(self):
    #    print('test_mode_3 autoincrement deferred source destination')

    # *****************************************
    # Mode 4 Autodecrement -(Rn)
    # Register is decremented by 2
    # then contains address of operand

    def test_mode_4(self):
        print('test_mode_4 autodecrement source')
        address = 0o2763
        a = 0o101
        b = 0o2136

        self.ram.write_word(address, a)
        self.reg.set(1, address+2)
        self.reg.set(2, b)
        expected_sum = a + b

        instruction = self.ADD(modeS=4, regS=1, modeD=0, regD=2)
        print(oct(instruction))
        assert self.dopr.is_double_operand_SSDD(instruction)
        self.dopr.do_double_operand_SSDD(instruction)

        actual_sum = self.reg.get(2)
        assert actual_sum == expected_sum

        r1 = self.reg.get(1)
        assert address == r1

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    #def test_mode_4(self):
    #    print('test_mode_4 autodecrement destination')

    #def test_mode_4(self):
    #    print('test_mode_4 autodecrement source destination')

    # *****************************************
    # Mode 5 Autodecrement Deferred
    # Register is decremented by 2
    # then contains pointer to address of operand

    def test_mode_5(self):
        print('test_mode_5 autodecrement deferred source')
        operanda = 0o101
        addressa = 0o2763
        pointera = 0o1172
        operandb = 0o2136

        self.ram.write_word(addressa, operanda)
        self.ram.write_word(pointera, addressa)
        self.reg.set(1, pointera+2)
        self.reg.set(2, operandb)
        expected_sum = operanda + operandb

        instruction = self.ADD(modeS=5, regS=1, modeD=0, regD=2)
        print(oct(instruction))
        assert self.dopr.is_double_operand_SSDD(instruction)
        self.dopr.do_double_operand_SSDD(instruction)

        actual_sum = self.reg.get(2)
        assert actual_sum == expected_sum

        assert pointera == self.reg.get(1)

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"


    #def test_mode_5(self):
    #    print('test_mode_5 autodecrement deferred destination')

    #def test_mode_5(self):
    #    print('test_mode_5 autodecrement deferred source destination')

    # *****************************************
    # Mode 6 Index X(Rn)
    # Value X, stored in a word following the instruction,
    # is added to the resgiter.
    # The sum contains the address of the operand.
    # Neither X nor the register are modified.

    def test_mode_6(self):
        print('test_mode_6 index source')

        # build the instruction ADD X(R1),R2
        instruction = self.ADD(modeS=6, regS=1, modeD=0, regD=2)
        print(f'opcode: {oct(instruction)}')
        assert self.dopr.is_double_operand_SSDD(instruction)

        # store the instruction
        instruction_address = 0o2763
        self.ram.write_word(instruction_address, instruction)

        # Value X, stored in a word following the instruction,
        X = 0o2050
        self.ram.write_word(instruction_address+2, X)

        operanda = 0o101  # 65
        self.reg.set(1, operanda)

        # is added to the resgiter.
        # The sum contains the address of the operand.
        operand_address = X + operanda
        self.ram.write_word(operand_address, operanda)

        operandb = 0o2136  # 1118
        self.reg.set(2, operandb)

        expected_sum = operanda + operandb  # 1183

        self.reg.set_pc(instruction_address+2, 'test_mode_6')  # +2 because we just read the PC in the instruciton cycle
        self.dopr.do_double_operand_SSDD(instruction)

        actual_sum = self.reg.get(2)
        assert actual_sum == expected_sum

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    #def test_mode_6(self):
    #    print('test_mode_6 index destination')

    #def test_mode_6(self):
    #    print('test_mode_6 index source destination')

    # *****************************************
    # Mode 7 index Deferred @X(Rn)
    # Value X, stored in a word following the instruction,
    # and the register are added.
    # The sum is used as a pointer to the address of the operand.
    # Neither X nor the register are modified.

    def test_mode_7(self):
        print('test_mode_7 index deferred source')
        # build the instruction ADD X(R1),R2
        instruction = self.ADD(modeS=7, regS=1, modeD=0, regD=2)
        print(f'opcode: {oct(instruction)}')
        assert self.dopr.is_double_operand_SSDD(instruction)

        # store the instruction
        instruction_address = 0o2763
        self.ram.write_word(instruction_address, instruction)

        # Value X, stored in a word following the instruction,
        X = 0o2050
        self.ram.write_word(instruction_address+2, X)

        operanda = 0o101  # 65
        self.reg.set(1, operanda)

        # is added to the register.
        # The sum is used as a pointer to the address of the operand.
        operand_pointer = X + operanda
        operand_address = 0o5432
        self.ram.write_word(operand_address, operanda)
        self.ram.write_word(operand_pointer, operand_address)

        operandb = 0o2136  # 1118
        self.reg.set(2, operandb)

        expected_sum = operanda + operandb  # 1183

        self.reg.set_pc(instruction_address+2, 'test_mode_7')  # +2 because we just read the PC in the instruciton cycle
        self.dopr.do_double_operand_SSDD(instruction)

        actual_sum = self.reg.get(2)
        assert actual_sum == expected_sum

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    #def test_mode_7(self):
    #    print('test_mode_7 index deferred destination')

    #def test_mode_7(self):
    #    print('test_mode_7 index deferred source destination')

    # Program Counter and Address Modes
    # Four modes are useful for position-independent code.
    # The special PC modes are the same as modes described
    # in sections 3.3 and 3.4, but the general register is R7, the program counter.

    def test_PC_mode_0(self):
        print('test_PC_mode_0')
        # jump

        a = 3
        b = 1

        self.psw.set_psw(psw=0)
        self.reg.set(1, a)
        self.reg.set(2, b)
        instruction = self.ADD(modeS=0, regS=1, modeD=0, regD=2)
        print(oct(instruction))
        assert self.dopr.is_double_operand_SSDD(instruction)
        self.dopr.do_double_operand_SSDD(instruction)

        sum = self.reg.get(2)
        assert sum == a + b

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    def test_PC_mode_2(self):
        print('test_PC_mode_2 immediate')
        # #get_n operand follows instruction
        # ADD #10,R0
        instruction = self.ADD(modeS=2, regS=7, modeD=0, regD=0)
        print(oct(instruction))
        assert instruction == 0o062700
        assert self.dopr.is_double_operand_SSDD(instruction)

        address = 0o1020
        self.ram.write_word(address, instruction)
        self.ram.write_word(address+2, 0o000010)
        self.reg.set(0, 0o000020)
        self.reg.set_pc(address, "test_PC_mode_2")
        print(f'{self.reg.registers_to_string()} {self.psw.nvzc_to_string()}')
        self.reg.set_pc(address+2, "test_PC_mode_2")
        self.dopr.do_double_operand_SSDD(instruction)
        print(f'{self.reg.registers_to_string()} {self.psw.nvzc_to_string()}')

        assert self.reg.get(0) == 0o000030
        assert self.reg.get_pc() == 0o1024

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    def test_PC_mode_3(self):
        print('test_PC_mode_3 absolute')
        # ADD @#2000,R3 Absolute address of operand follows instruction
        instruction = self.ADD(modeS=3, regS=7, modeD=0, regD=3)
        print(oct(instruction))
        assert instruction == 0o063703
        assert self.dopr.is_double_operand_SSDD(instruction)
        a = 0o00300
        b = 0o00500
        pc = 0o20
        address = 0o2000
        self.ram.write_word(pc, instruction)
        self.ram.write_word(pc+2, address)
        self.ram.write_word(address, 0o00300)
        self.reg.set(3, b)
        self.reg.set_pc(pc, "test_PC_mode_3")
        print(f'{self.reg.registers_to_string()} {self.psw.nvzc_to_string()}')
        self.reg.set_pc(pc+2, "test_PC_mode_3")
        self.dopr.do_double_operand_SSDD(instruction)
        print(f'{self.reg.registers_to_string()} {self.psw.nvzc_to_string()}')

        assert self.reg.get(3) == a + b
        assert self.reg.get_pc() == pc+4

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    def test_PC_mode_4(self):
        print('test_PC_mode_4')
        address = 0o2763
        a = 0o101
        b = 0o2136

        self.ram.write_word(address, a)
        self.reg.set(1, address+2)
        self.reg.set(2, b)
        expected_sum = a + b

        instruction = self.ADD(modeS=4, regS=1, modeD=0, regD=2)
        print(oct(instruction))
        assert self.dopr.is_double_operand_SSDD(instruction)
        self.dopr.do_double_operand_SSDD(instruction)

        actual_sum = self.reg.get(2)
        assert actual_sum == expected_sum

        r1 = self.reg.get(1)
        assert address == r1

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    def test_PC_mode_5(self):
        print('test_PC_mode_5 relative')
        # INC A. See p. 3-16 of LSI-11 PDP-11/03 Processor Handbook
        instruction = 0o005267
        assert self.sopr.is_single_operand(instruction)
        a = 0o000054
        pc = 0o1020
        address = 0o1100
        self.ram.write_word(pc, instruction)
        self.ram.write_word(pc+2, a)
        self.ram.write_word(address, 0o00000)
        self.reg.set_pc(pc, "test_PC_mode_5")

        #print(f'{self.reg.registers_to_string()} {self.psw.nvzc_to_string()}')
        #self.ram.dump(0o1020, 0o1100)

        self.reg.set_pc(pc+2, "test_PC_mode_5")
        self.sopr.do_single_operand(instruction)

        #print(f'{self.reg.registers_to_string()} {self.psw.nvzc_to_string()}')
        #self.ram.dump(0o1020, 0o1100)

        assert self.reg.get_pc() == 0o1024
        assert self.ram.read_word(0o1100) == 0o01

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    def test_PC_mode_6(self):
        print('test_PC_mode_6 Relative')
        # A - Relative Address (index vlaue) follows the instruction

        # build the instruction ADD X(R1),R2
        instruction = self.ADD(modeS=6, regS=1, modeD=0, regD=2)
        print(f'opcode: {oct(instruction)}')
        assert self.dopr.is_double_operand_SSDD(instruction)

        # store the instruction
        instruction_address = 0o2763
        self.ram.write_word(instruction_address, instruction)

        # Value X, stored in a word following the instruction,
        X = 0o2050
        self.ram.write_word(instruction_address+2, X)

        operanda = 0o101 # 65
        self.reg.set(1, operanda)

        # is added to the resgiter.
        # The sum contains the address of the operand.
        operand_address = X + operanda
        self.ram.write_word(operand_address, operanda)

        operandb = 0o2136 # 1118
        self.reg.set(2, operandb)

        expected_sum = operanda + operandb # 1183

        self.reg.set_pc(instruction_address+2, 'test_mode_6')  # +2 because we just read the PC in the instruciton cycle
        self.dopr.do_double_operand_SSDD(instruction)

        actual_sum = self.reg.get(2)
        assert actual_sum == expected_sum

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0000"

    def test_PC_mode_7(self):
        print('test_mode_7 Relative Deferred')
        # OPR@X(PC)
        # CLR @A. See p. 3-16 of LSI-11 PDP-11/03 Processor Handbook
        instruction = 0o005077
        assert self.sopr.is_single_operand(instruction)
        a = 0o000020
        pc = 0o1020
        pointer = 0o1044
        address = 0o1060
        self.ram.write_word(pc, instruction)
        self.ram.write_word(pc + 2, a)
        self.ram.write_word(pointer, address)
        self.ram.write_word(address, 0o100001)
        self.reg.set_pc(pc, "test_PC_mode_7")

        #print(f'{self.reg.registers_to_string()} {self.psw.nvzc_to_string()}')
        #self.ram.dump(0o1020, 0o1060)

        self.reg.set_pc(pc + 2, "test_PC_mode_7")
        self.sopr.do_single_operand(instruction)

        #print(f'{self.reg.registers_to_string()} {self.psw.nvzc_to_string()}')
        #self.ram.dump(0o1020, 0o1060)

        assert self.reg.get_pc() == 0o1024
        assert self.ram.read_word(address) == 0o0

        condition_codes = self.psw.nvzc_to_string()
        assert condition_codes == "0100"
