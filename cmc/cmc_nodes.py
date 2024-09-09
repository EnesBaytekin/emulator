from array import array
from sys import stderr

def error(msg, exit_code=1):
    print("\033[31mError:\033[0m", msg, file=stderr)
    exit(exit_code)

class Node:
    label_addresses = {}
    backpatch_list = {}
    address = 0
    @classmethod
    def reset(cls):
        cls.label_addresses = {}
        cls.backpatch_list = {}
        cls.address = 0
    @classmethod
    def get_label(cls, label):
        if label in cls.label_addresses:
            return cls.label_addresses[label]
        cls.backpatch_list[cls.address] = label
        return 0
    @classmethod
    def fix_addresses(cls, program):
        for ins_addr, label in cls.backpatch_list.items():
            label_addr = cls.label_addresses[label]
            addrH = (label_addr&0xff00)>>8
            addrL = label_addr&0x00ff
            program[ins_addr] = addrH
            program[ins_addr+1] = addrL
        return program
    
    def __init__(self, _type, *children):
        self.type = _type
        self.children = children
    def get(self):
        result = array("B", [])
        for child in self.children:
            if isinstance(child, Node):
                result.extend(child.get())
        return result

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
        return super().get()

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
        return super().get()

class NodeStatement4(Node):
    def __init__(self, put, data):
        super().__init__("statement", put, data)
    def get(self):
        result = self.children[1].get()
        Node.address += len(result)
        return result

## DATA ##

class NodeData1(Node):
    def __init__(self, num):
        super().__init__("data", num)
    def get(self):
        number = self.children[0].value
        if number < 0 or number >= 256:
            error("Numbers after 'put' must be in range [0, 255]")
        return array("B", [number])

class NodeData2(Node):
    def __init__(self, num, data):
        super().__init__("data", num, data)
        number = self.children[0].value
        if number < 0 or number >= 256:
            error("Numbers after 'put' must be in range [0, 255]")
        result = array("B", [number])
        result += self.children[0].get()
        return result

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
        return result

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
        result += self.children[1].get()
        return result

class NodeData5(Node):
    def __init__(self, word):
        super().__init__("data", word)
    def get(self):
        label = self.children[0].value
        addr = Node.get_label(label)
        addrH = (addr&0xff00)>>8
        addrL = addr&0x00ff
        result = array("B", [addrH, addrL])
        return result

## BYTE ##

class NodeByte1(Node):
    def __init__(self, num):
        super().__init__("byte", num)

class NodeByte2(Node):
    def __init__(self, str):
        super().__init__("byte", str)

## INSTRUCTION ##

class NodeInstruction1(Node):
    def __init__(self, add, reg1, reg2):
        super().__init__("instruction", add, reg1, reg2)

class NodeInstruction2(Node):
    def __init__(self, sub, reg1, reg2):
        super().__init__("instruction", sub, reg1, reg2)

class NodeInstruction3(Node):
    def __init__(self, mul, reg1, reg2):
        super().__init__("instruction", mul, reg1, reg2)

class NodeInstruction4(Node):
    def __init__(self, div, reg1, reg2):
        super().__init__("instruction", div, reg1, reg2)

class NodeInstruction5(Node):
    def __init__(self, shl, reg, num):
        super().__init__("instruction", shl, reg, num)

class NodeInstruction6(Node):
    def __init__(self, shr, reg, num):
        super().__init__("instruction", shr, reg, num)

class NodeInstruction7(Node):
    def __init__(self, and_, reg1, reg2):
        super().__init__("instruction", and_, reg1, reg2)

class NodeInstruction8(Node):
    def __init__(self, orr, reg1, reg2):
        super().__init__("instruction", orr, reg1, reg2)

class NodeInstruction9(Node):
    def __init__(self, xor, reg1, reg2):
        super().__init__("instruction", xor, reg1, reg2)

class NodeInstruction10(Node):
    def __init__(self, not_, reg):
        super().__init__("instruction", not_, reg)

class NodeInstruction11(Node):
    def __init__(self, psh, reg):
        super().__init__("instruction", psh, reg)

class NodeInstruction12(Node):
    def __init__(self, pop, reg):
        super().__init__("instruction", pop, reg)

class NodeInstruction13(Node):
    def __init__(self, cal, address):
        super().__init__("instruction", cal, address)

class NodeInstruction14(Node):
    def __init__(self, ret):
        super().__init__("instruction", ret)

class NodeInstruction15(Node):
    def __init__(self, jmp, address):
        super().__init__("instruction", jmp, address)

class NodeInstruction16(Node):
    def __init__(self, jif, flag, num, address):
        super().__init__("instruction", jif, flag, num, address)

class NodeInstruction17(Node):
    def __init__(self, lod, reg, address):
        super().__init__("instruction", lod, reg, address)

class NodeInstruction18(Node):
    def __init__(self, ldi, reg, byte):
        super().__init__("instruction", ldi, reg, byte)

class NodeInstruction19(Node):
    def __init__(self, sto, reg, address):
        super().__init__("instruction", sto, reg, address)

class NodeInstruction20(Node):
    def __init__(self, inc, reg):
        super().__init__("instruction", inc, reg)

class NodeInstruction21(Node):
    def __init__(self, dec, reg):
        super().__init__("instruction", dec, reg)

class NodeInstruction22(Node):
    def __init__(self, cmp, reg1, reg2):
        super().__init__("instruction", cmp, reg1, reg2)

class NodeInstruction23(Node):
    def __init__(self, nop):
        super().__init__("instruction", nop)

class NodeInstruction24(Node):
    def __init__(self, hlt):
        super().__init__("instruction", hlt)

class NodeInstruction25(Node):
    def __init__(self, mov, reg1, reg2):
        super().__init__("instruction", mov, reg1, reg2)

class NodeInstruction26(Node):
    def __init__(self, rti):
        super().__init__("instruction", rti)

class NodeInstruction27(Node):
    def __init__(self, sei):
        super().__init__("instruction", sei)

class NodeInstruction28(Node):
    def __init__(self, cli):
        super().__init__("instruction", cli)

## ADDRESS ##

class NodeAddress1(Node):
    def __init__(self, word):
        super().__init__("address", word)

class NodeAddress2(Node):
    def __init__(self, NUM):
        super().__init__("address", NUM)
