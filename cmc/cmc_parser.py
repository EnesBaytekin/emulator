from cmc_nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
    
    def match(self, token_type):
        if self.index < len(self.tokens) and \
        self.tokens[self.index].type == token_type:
            token = self.tokens[self.index]
            self.index += 1
            return token
    
    def parse(self):
        return self.parse_program()

    def parse_program(self):
        
        index_checkpoint = self.index
        _1 = self.parse_new_line()
        if _1 is not None:
            _2 = self.parse_statement()
            if _2 is not None:
                _3 = self.parse_new_line()
                if _3 is not None:
                    _4 = self.parse_program()
                    if _4 is not None:
                        return NodeProgram1(_1, _2, _3, _4)
        
        self.index = index_checkpoint
        return NodeProgram2()

    def parse_new_line(self):
    
        index_checkpoint = self.index
        _1 = self.match("LINE")
        if _1 is not None:
            _2 = self.parse_new_line()
            if _2 is not None:
                return NodeNewLine1(_1, _2)

        self.index = index_checkpoint
        return NodeNewLine2()

    def parse_statement(self):
        
        index_checkpoint = self.index
        _1 = self.match("LABEL")
        if _1 is not None: return NodeStatement1(_1)

        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.parse_instruction()
        if _1 is not None: return NodeStatement2(_1)

        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("GO")
        if _1 is not None:
            _2 = self.match("NUM")
            if _2 is not None:
                return NodeStatement3(_1, _2)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("PUT")
        if _1 is not None:
            _2 = self.parse_data()
            if _2 is not None:
                return NodeStatement4(_1, _2)
    
    def parse_data(self):
        
        index_checkpoint = self.index
        _1 = self.match("NUM")
        if _1 is not None:

            index_checkpoint_a = self.index
            _2 = self.parse_data()
            if _2 is not None:
                return NodeData2(_1, _2)
            
            self.index = index_checkpoint_a
            return NodeData1(_1)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("STR")
        if _1 is not None:

            index_checkpoint_a = self.index
            _2 = self.parse_data()
            if _2 is not None:
                return NodeData2(_1, _2)
            
            self.index = index_checkpoint_a
            return NodeData1(_1)

        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("WORD")
        if _1 is not None:
            return NodeData5(_1)

    def parse_byte(self):

        index_checkpoint = self.index
        _1 = self.match("NUM")
        if _1 is not None:
            return NodeByte1(_1)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("STR")
        if _1 is not None:
            return NodeByte2(_1)

    def parse_instruction(self):
        
        index_checkpoint = self.index
        _1 = self.match("ADD")
        if _1 is not None:
            _2 = self.parse_reg()
            if _2 is not None:
                _3 = self.parse_reg()
                if _3 is not None:
                    return NodeInstruction1(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("SUB")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.match("REG")
                if _3 is not None:
                    return NodeInstruction2(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("MUL")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.match("REG")
                if _3 is not None:
                    return NodeInstruction3(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("DIV")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.match("REG")
                if _3 is not None:
                    return NodeInstruction4(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("SHL")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.match("NUM")
                if _3 is not None:
                    return NodeInstruction5(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("SHR")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.match("NUM")
                if _3 is not None:
                    return NodeInstruction6(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("AND")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.match("REG")
                if _3 is not None:
                    return NodeInstruction7(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("ORR")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.match("REG")
                if _3 is not None:
                    return NodeInstruction8(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("XOR")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.match("REG")
                if _3 is not None:
                    return NodeInstruction9(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("NOT")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                return NodeInstruction10(_1, _2)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("PSH")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                return NodeInstruction11(_1, _2)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("POP")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                return NodeInstruction12(_1, _2)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("CAL")
        if _1 is not None:
            _2 = self.parse_address()
            if _2 is not None:
                return NodeInstruction13(_1, _2)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("RET")
        if _1 is not None:
            return NodeInstruction14(_1)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("JMP")
        if _1 is not None:
            _2 = self.parse_address()
            if _2 is not None:
                return NodeInstruction15(_1, _2)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("JIF")
        if _1 is not None:
            _2 = self.match("FLAG")
            if _2 is not None:
                _3 = self.match("NUM")
                if _3 is not None:
                    _4 = self.parse_address()
                    if _4 is not None:
                        return NodeInstruction16(_1, _2, _3, _4)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("LOD")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.parse_address()
                if _3 is not None:
                    return NodeInstruction17(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("LDI")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.parse_byte()
                if _3 is not None:
                    return NodeInstruction18(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("STO")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.parse_address()
                if _3 is not None:
                    return NodeInstruction19(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("INC")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                return NodeInstruction20(_1, _2)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("DEC")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                return NodeInstruction21(_1, _2)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("CMP")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.match("REG")
                if _3 is not None:
                    return NodeInstruction22(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("NOP")
        if _1 is not None:
            return NodeInstruction23(_1)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("HLT")
        if _1 is not None:
            return NodeInstruction24(_1)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("MOV")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.match("REG")
                if _3 is not None:
                    return NodeInstruction25(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("RTI")
        if _1 is not None:
            return NodeInstruction26(_1)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("SEI")
        if _1 is not None:
            return NodeInstruction27(_1)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("CLI")
        if _1 is not None:
            return NodeInstruction28(_1)
    
    def parse_address(self):
        
        index_checkpoint = self.index
        _1 = self.match("WORD")
        if _1 is not None:
            return NodeAddress1(_1)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("NUM")
        if _1 is not None:
            return NodeAddress1(_1)
