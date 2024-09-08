

class Node:
    def __init__(self, _type, *children):
        self.type = _type
        self.children = children
    def get(self):
        result = ""
        result += "{\"type\":\""
        result += self.type
        result += "\",\"children\":"
        if len(self.children) == 0:
            result += "null"
        else:
            result += "["
            for index, child in enumerate(self.children):
                if isinstance(child, Node):
                    result += child.get()
                else:
                    result += "["
                    result += repr(child.type).replace("'", "\"")
                    result += ","
                    result += repr(child.value).replace("'", "\"")
                    result += "]"
                if index < len(self.children)-1:
                    result += ","
            result += "]"
        result += "}"
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

class NodeStatement2(Node):
    def __init__(self, instruction):
        super().__init__("statement", instruction)

class NodeStatement3(Node):
    def __init__(self, go, num):
        super().__init__("statement", go, num)

class NodeStatement4(Node):
    def __init__(self, put, data):
        super().__init__("statement", put, data)

## DATA ##

class NodeData1(Node):
    def __init__(self, num):
        super().__init__("data", num)

class NodeData2(Node):
    def __init__(self, num, data):
        super().__init__("data", num, data)

class NodeData3(Node):
    def __init__(self, str):
        super().__init__("data", str)

class NodeData4(Node):
    def __init__(self, str, data):
        super().__init__("data", str, data)

class NodeData5(Node):
    def __init__(self, word):
        super().__init__("data", word)

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
