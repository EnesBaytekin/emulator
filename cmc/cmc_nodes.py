from array import array
from sys import stderr
from cmc_instruction_table import instruction_table

def error(msg, exit_code=1):
    print("\033[31mError:\033[0m", msg, file=stderr)
    exit(exit_code)

class Node:
    label_addresses = {}
    backpatch_list = {}
    address = 0
    program = array("B", [0xc8]*65536)
    @classmethod
    def reset(cls):
        cls.label_addresses = {}
        cls.backpatch_list = {}
        cls.address = 0
        cls.program = array("B", [0xc8]*65536)
    @classmethod
    def add(cls, code):
        for byte in code:
            cls.program[cls.address] = byte
            cls.address += 1
    @classmethod
    def get_label(cls, label):
        if label in cls.label_addresses:
            return cls.label_addresses[label]
        cls.backpatch_list[cls.address] = label
        return 0
    @classmethod
    def fix_addresses(cls):
        for ins_addr, label in cls.backpatch_list.items():
            label_addr = cls.label_addresses[label]
            addrH = (label_addr&0xff00)>>8
            addrL = label_addr&0x00ff
            cls.program[ins_addr] = addrH
            cls.program[ins_addr+1] = addrL
    
    def __init__(self, _type, *children):
        self.type = _type
        self.children = children
    def get(self):
        for child in self.children:
            if isinstance(child, Node):
                child.get()

## PROGRAM ##

class NodeProgram1(Node):
    def __init__(self, new_line, statement, line, program):
        super().__init__("program", new_line, statement, line, program)

class NodeProgram2(Node):
    def __init__(self):
        super().__init__("program")

## NEW_LINE ##

class NodeNewLine1(Node):
    def __init__(self, line, new_line):
        super().__init__("new_line", line, new_line)

class NodeNewLine2(Node):
    def __init__(self):
        super().__init__("new_line")

## STATEMENT ##

class NodeStatement1(Node):
    def __init__(self, label):
        super().__init__("statement", label)
    def get(self):
        Node.label_addresses[self.children[0].value] = Node.address

class NodeStatement2(Node):
    def __init__(self, instruction):
        super().__init__("statement", instruction)

class NodeStatement3(Node):
    def __init__(self, go, num):
        super().__init__("statement", go, num)
    def get(self):
        number = self.children[1].value
        if number < 0 or number >= 65536:
            error("Adress value must be in range [0, 65535]")
        Node.address = number

class NodeStatement4(Node):
    def __init__(self, put, data):
        super().__init__("statement", put, data)
    def get(self):
        self.children[1].get()

## DATA ##

class NodeData1(Node):
    def __init__(self, num):
        super().__init__("data", num)
    def get(self):
        number = self.children[0].value
        if number < 0 or number >= 256:
            error("Numbers after 'put' must be in range [0, 255]")
        result = array("B", [number])
        Node.add(result)

class NodeData2(Node):
    def __init__(self, num, data):
        super().__init__("data", num, data)
        number = self.children[0].value
        if number < 0 or number >= 256:
            error("Numbers after 'put' must be in range [0, 255]")
        result = array("B", [number])
        Node.add(result)
        self.children[1].get()

class NodeData3(Node):
    def __init__(self, str):
        super().__init__("data", str)
    def get(self):
        result = array("B", [])
        string = self.children[0].value
        for char in string:
            byte = ord(char)
            if byte >= 256:
                error("String characters must be one byte (ascii)")
            result.append(byte)
        Node.add(result)

class NodeData4(Node):
    def __init__(self, str, data):
        super().__init__("data", str, data)
    def get(self):
        result = array("B", [])
        string = self.children[0].value
        for char in string:
            byte = ord(char)
            if byte >= 256:
                error("String characters must be one byte (ascii)")
            result.append(byte)
        Node.add(result)
        self.children[1].get()

class NodeData5(Node):
    def __init__(self, word):
        super().__init__("data", word)
    def get(self):
        label = self.children[0].value
        addr = Node.get_label(label)
        addrH = (addr&0xff00)>>8
        addrL = addr&0x00ff
        result = array("B", [addrH, addrL])
        Node.add(result)

## BYTE ##

class NodeByte1(Node):
    def __init__(self, num):
        super().__init__("byte", num)
    def get(self):
        number = self.children[0].value
        if number < 0 or number >= 256:
            error("Numbers after 'put' must be in range [0, 255]")
        result = array("B", [number])
        Node.add(result)

class NodeByte2(Node):
    def __init__(self, str):
        super().__init__("byte", str)
    def get(self):
        string = self.children[0].value
        if len(string) != 1:
            error("Length of the string must be one")
        byte = ord(string)
        if byte >= 256:
            error("String characters must be one byte (ascii)")
        result = array("B", [byte])
        Node.add(result)

## INSTRUCTION ##

def bitstring_to_bytes(bitstring):
    byte_array = array("B", [])
    for i in range(len(bitstring)//8):
        byte = int(bitstring[i*8: i*8+8], 2)
        byte_array.append(byte)
    return byte_array

class NodeInstruction1(Node):
    def __init__(self, add, reg1, reg2):
        super().__init__("instruction", add, reg1, reg2)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        reg1 = self.children[1].value
        reg2 = self.children[2].value
        instruction = f"{op_code}000{reg1:04b}{reg2:04b}"
        result = bitstring_to_bytes(instruction)
        Node.add(result)

class NodeInstruction2(Node):
    def __init__(self, sub, reg1, reg2):
        super().__init__("instruction", sub, reg1, reg2)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        reg1 = self.children[1].value
        reg2 = self.children[2].value
        instruction = f"{op_code}000{reg1:04b}{reg2:04b}"
        result = bitstring_to_bytes(instruction)
        Node.add(result)

class NodeInstruction3(Node):
    def __init__(self, mul, reg1, reg2):
        super().__init__("instruction", mul, reg1, reg2)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        reg1 = self.children[1].value
        reg2 = self.children[2].value
        instruction = f"{op_code}000{reg1:04b}{reg2:04b}"
        result = bitstring_to_bytes(instruction)
        Node.add(result)

class NodeInstruction4(Node):
    def __init__(self, div, reg1, reg2):
        super().__init__("instruction", div, reg1, reg2)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        reg1 = self.children[1].value
        reg2 = self.children[2].value
        instruction = f"{op_code}000{reg1:04b}{reg2:04b}"
        result = bitstring_to_bytes(instruction)
        Node.add(result)

class NodeInstruction5(Node):
    def __init__(self, shl, reg, num):
        super().__init__("instruction", shl, reg, num)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        reg1 = self.children[1].value
        num = self.children[2].value
        if num < 1 or num > 8:
            error("Shift offset must be in range [1, 8]")
        instruction = f"{op_code}000{reg1:04b}0{num:03x}"
        result = bitstring_to_bytes(instruction)
        Node.add(result)

class NodeInstruction6(Node):
    def __init__(self, shr, reg, num):
        super().__init__("instruction", shr, reg, num)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        reg1 = self.children[1].value
        num = self.children[2].value
        if num < 1 or num > 8:
            error("Shift offset must be in range [1, 8]")
        instruction = f"{op_code}000{reg1:04b}0{num:03x}"
        result = bitstring_to_bytes(instruction)
        Node.add(result)

class NodeInstruction7(Node):
    def __init__(self, and_, reg1, reg2):
        super().__init__("instruction", and_, reg1, reg2)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        reg1 = self.children[1].value
        reg2 = self.children[2].value
        instruction = f"{op_code}000{reg1:04b}{reg2:04b}"
        result = bitstring_to_bytes(instruction)
        Node.add(result)

class NodeInstruction8(Node):
    def __init__(self, orr, reg1, reg2):
        super().__init__("instruction", orr, reg1, reg2)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        reg1 = self.children[1].value
        reg2 = self.children[2].value
        instruction = f"{op_code}000{reg1:04b}{reg2:04b}"
        result = bitstring_to_bytes(instruction)
        Node.add(result)

class NodeInstruction9(Node):
    def __init__(self, xor, reg1, reg2):
        super().__init__("instruction", xor, reg1, reg2)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        reg1 = self.children[1].value
        reg2 = self.children[2].value
        instruction = f"{op_code}000{reg1:04b}{reg2:04b}"
        result = bitstring_to_bytes(instruction)
        Node.add(result)

class NodeInstruction10(Node):
    def __init__(self, not_, reg):
        super().__init__("instruction", not_, reg)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        reg1 = self.children[1].value
        instruction = f"{op_code}000{reg1:04b}0000"
        result = bitstring_to_bytes(instruction)
        Node.add(result)

class NodeInstruction11(Node):
    def __init__(self, psh, reg):
        super().__init__("instruction", psh, reg)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        reg1 = self.children[1].value
        instruction = f"{op_code}000{reg1:04b}0000"
        result = bitstring_to_bytes(instruction)
        Node.add(result)

class NodeInstruction12(Node):
    def __init__(self, pop, reg):
        super().__init__("instruction", pop, reg)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        reg1 = self.children[1].value
        instruction = f"{op_code}000{reg1:04b}0000"
        result = bitstring_to_bytes(instruction)
        Node.add(result)

class NodeInstruction13(Node):
    def __init__(self, cal, address):
        super().__init__("instruction", cal, address)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        instruction = f"{op_code}000"
        result = bitstring_to_bytes(instruction)
        Node.add(result)
        self.children[1].get()

class NodeInstruction14(Node):
    def __init__(self, ret):
        super().__init__("instruction", ret)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        instruction = f"{op_code}000"
        result = bitstring_to_bytes(instruction)
        Node.add(result)

class NodeInstruction15(Node):
    def __init__(self, jmp, address):
        super().__init__("instruction", jmp, address)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        instruction = f"{op_code}000"
        result = bitstring_to_bytes(instruction)
        Node.add(result)
        self.children[1].get()

class NodeInstruction16(Node):
    def __init__(self, jif, flag, num, address):
        super().__init__("instruction", jif, flag, num, address)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        flag = self.children[1].value
        flag_code = "10" if flag == "z" else "01"
        num = self.children[2].value
        if num != 0 and num != 1:
            error("Flag value must be 0 or 1")
        instruction = f"{op_code}{flag_code}{num}"
        result = bitstring_to_bytes(instruction)
        Node.add(result)
        self.children[3].get()

class NodeInstruction17(Node):
    def __init__(self, lod, reg, address):
        super().__init__("instruction", lod, reg, address)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        reg = self.children[1].value
        instruction = f"{op_code}{reg:04b}"
        result = bitstring_to_bytes(instruction)
        Node.add(result)
        self.children[2].get()

class NodeInstruction18(Node):
    def __init__(self, ldi, reg, byte):
        super().__init__("instruction", ldi, reg, byte)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        reg = self.children[1].value
        instruction = f"{op_code}{reg:04b}"
        result = bitstring_to_bytes(instruction)
        Node.add(result)
        self.children[2].get()

class NodeInstruction19(Node):
    def __init__(self, sto, reg, address):
        super().__init__("instruction", sto, reg, address)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        reg = self.children[1].value
        instruction = f"{op_code}{reg:04b}"
        result = bitstring_to_bytes(instruction)
        Node.add(result)
        self.children[2].get()

class NodeInstruction20(Node):
    def __init__(self, inc, reg):
        super().__init__("instruction", inc, reg)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        reg = self.children[1].value
        instruction = f"{op_code}000{reg:04b}0000"
        result = bitstring_to_bytes(instruction)
        Node.add(result)

class NodeInstruction21(Node):
    def __init__(self, dec, reg):
        super().__init__("instruction", dec, reg)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        reg = self.children[1].value
        instruction = f"{op_code}000{reg:04b}0000"
        result = bitstring_to_bytes(instruction)
        Node.add(result)

class NodeInstruction22(Node):
    def __init__(self, cmp, reg1, reg2):
        super().__init__("instruction", cmp, reg1, reg2)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        reg1 = self.children[1].value
        reg2 = self.children[2].value
        instruction = f"{op_code}000{reg1:04b}{reg2:04b}"
        result = bitstring_to_bytes(instruction)
        Node.add(result)

class NodeInstruction23(Node):
    def __init__(self, nop):
        super().__init__("instruction", nop)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        instruction = f"{op_code}000"
        result = bitstring_to_bytes(instruction)
        Node.add(result)

class NodeInstruction24(Node):
    def __init__(self, hlt):
        super().__init__("instruction", hlt)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        instruction = f"{op_code}000"
        result = bitstring_to_bytes(instruction)
        Node.add(result)

class NodeInstruction25(Node):
    def __init__(self, mov, reg1, reg2):
        super().__init__("instruction", mov, reg1, reg2)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        reg1 = self.children[1].value
        reg2 = self.children[2].value
        instruction = f"{op_code}000{reg1:04b}{reg2:04b}"
        result = bitstring_to_bytes(instruction)
        Node.add(result)

class NodeInstruction26(Node):
    def __init__(self, rti):
        super().__init__("instruction", rti)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        instruction = f"{op_code}000"
        result = bitstring_to_bytes(instruction)
        Node.add(result)

class NodeInstruction27(Node):
    def __init__(self, sei):
        super().__init__("instruction", sei)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        instruction = f"{op_code}000"
        result = bitstring_to_bytes(instruction)
        Node.add(result)

class NodeInstruction28(Node):
    def __init__(self, cli):
        super().__init__("instruction", cli)
    def get(self):
        instruction_name = self.children[0].value
        op_code = instruction_table[instruction_name]
        instruction = f"{op_code}000"
        result = bitstring_to_bytes(instruction)
        Node.add(result)

## ADDRESS ##

class NodeAddress1(Node):
    def __init__(self, word):
        super().__init__("address", word)
    def get(self):
        word = self.children[0].value
        address = Node.get_label(word)
        addrH = (address&0xff00)>>8
        addrL = address&0x00ff
        result = array("B", [addrH, addrL])
        Node.add(result)

class NodeAddress2(Node):
    def __init__(self, NUM):
        super().__init__("address", NUM)
    def get(self):
        num = self.children[0].value
        if num < 0 or num >= 65536:
            error("Address value must be in range [0, 65535]")
        addrH = (num&0xff00)>>8
        addrL = num&0x00ff
        result = array("B", [addrH, addrL])
        Node.add(result)

