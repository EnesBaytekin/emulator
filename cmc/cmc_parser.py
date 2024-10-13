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
    
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("WORD")
        if _1 is not None:
            _2 = self.match("EQ")
            if _2 is not None:
                _3 = self.parse_data()
                if _3 is not None:
                    return NodeStatement5(_1, _2, _3)
    
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
                return NodeData4(_1, _2)
            
            self.index = index_checkpoint_a
            return NodeData3(_1)

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
                    return NodeInstruction_add(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("SUB")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.match("REG")
                if _3 is not None:
                    return NodeInstruction_sub(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("MUL")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.match("REG")
                if _3 is not None:
                    return NodeInstruction_mul(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("DIV")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.match("REG")
                if _3 is not None:
                    return NodeInstruction_div(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("SHL")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.match("NUM")
                if _3 is not None:
                    return NodeInstruction_shl(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("SHR")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.match("NUM")
                if _3 is not None:
                    return NodeInstruction_shr(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("AND")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.match("REG")
                if _3 is not None:
                    return NodeInstruction_and(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("ORR")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.match("REG")
                if _3 is not None:
                    return NodeInstruction_orr(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("XOR")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.match("REG")
                if _3 is not None:
                    return NodeInstruction_xor(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("NOT")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                return NodeInstruction_not(_1, _2)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("PSH")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                return NodeInstruction_psh(_1, _2)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("POP")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                return NodeInstruction_pop(_1, _2)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("CAL")
        if _1 is not None:
            _2 = self.parse_address()
            if _2 is not None:
                return NodeInstruction_cal(_1, _2)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("RET")
        if _1 is not None:
            return NodeInstruction_ret(_1)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("JMP")
        if _1 is not None:
            _2 = self.parse_address()
            if _2 is not None:
                return NodeInstruction_jmp(_1, _2)
        
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
                        return NodeInstruction_jif(_1, _2, _3, _4)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("LOD")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.parse_address()
                if _3 is not None:
                    index_checkpoint_a = self.index
                    _4 = self.parse_offset()
                    if _4 is not None:
                        return NodeInstruction_lod2(_1, _2, _3, _4)
                    self.index = index_checkpoint_a
                    return NodeInstruction_lod(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("LDI")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.parse_byte()
                if _3 is not None:
                    return NodeInstruction_ldi(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("STO")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.parse_address()
                if _3 is not None:
                    index_checkpoint_a = self.index
                    _4 = self.parse_offset()
                    if _4 is not None:
                        return NodeInstruction_sto2(_1, _2, _3, _4)
                    self.index = index_checkpoint_a
                    return NodeInstruction_sto(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("INC")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                return NodeInstruction_inc(_1, _2)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("DEC")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                return NodeInstruction_dec(_1, _2)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("CMP")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.match("REG")
                if _3 is not None:
                    return NodeInstruction_cmp(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("NOP")
        if _1 is not None:
            return NodeInstruction_nop(_1)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("HLT")
        if _1 is not None:
            return NodeInstruction_hlt(_1)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("MOV")
        if _1 is not None:
            _2 = self.match("REG")
            if _2 is not None:
                _3 = self.match("REG")
                if _3 is not None:
                    return NodeInstruction_mov(_1, _2, _3)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("RTI")
        if _1 is not None:
            return NodeInstruction_rti(_1)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("SEI")
        if _1 is not None:
            return NodeInstruction_sei(_1)
        
        self.index = index_checkpoint
        index_checkpoint = self.index
        _1 = self.match("CLI")
        if _1 is not None:
            return NodeInstruction_cli(_1)
    
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

    def parse_offset(self):

        _1 = self.match("[")
        if _1 is not None:

            index_checkpoint = self.index
            _2 = self.match("NUM")
            if _2 is not None:
                _3 = self.match("]")
                if _3 is not None:
                    return NodeOffset1(_1, _2, _3)
            
            self.index = index_checkpoint
            _2 = self.match("WORD")
            if _2 is not None:
                
                index_checkpoint_a = self.index
                _3 = self.match("]")
                if _3 is not None:
                    return NodeOffset2(_1, _2, _3)
                
                self.index = index_checkpoint_a
                _3 = self.parse_offset()
                if _3 is not None:
                    _4 = self.match("]")
                    if _4 is not None:
                        return NodeOffset3(_1, _2, _3, _4)
            
