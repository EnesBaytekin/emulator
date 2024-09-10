from cmc_instruction_table import instruction_table

def is_hex(value):
    if len(value) <= 1: return False
    if value[-1] != "x": return False
    for char in value[:-1]:
        if char not in "0123456789abcdef":
            return False
    return True

def is_bin(value):
    if len(value) <= 1: return False
    if value[-1] != "b": return False
    for char in value[:-1]:
        if char not in "01":
            return False
    return True

def is_dec(value):
    if len(value) == 0: return False
    for char in value:
        if char not in "0123456789":
            return False
    return True

def is_reg(value):
    return (
        len(value) == 2 and
        value[0] == "r" and
        value[1] in "0123456789abcdef"
    )

class Token:
    def __init__(self, _type, value):
        self.type = _type
        self.value = value
    def __repr__(self):
        return f"[{self.type}: {repr(self.value)}]"

def tokenize(code):
    tokens = []
    state = ""
    value = ""
    index = 0
    size = len(code)
    while index < size:
        char = code[index]
        if state == "":
            if char.isalnum():
                state = "word"
                value = char
            elif char in ('"', "'"):
                state = "string"
                value = char
            elif char == ";":
                state = "comment"
            elif char == "\n":
                token = Token("LINE", "\n")
                tokens.append(token)
            elif char in "=":
                token = Token("EQ", "=")
                tokens.append(token)
            elif char in "+":
                token = Token("PLUS", "+")
                tokens.append(token)
            elif char in ".":
                state = "label"
                value = ""
        elif state == "word":
            if char.isalnum() or char == "_":
                value += char
            else:
                if is_hex(value):
                    token = Token("NUM", int(value[:-1], 16))
                elif is_bin(value):
                    token = Token("NUM", int(value[:-1], 2))
                elif is_dec(value):
                    token = Token("NUM", int(value))
                elif is_reg(value):
                    token = Token("REG", int(value[1], 16))
                elif value in instruction_table:
                    token = Token(value.upper(), value)
                elif value == "go":
                    token = Token("GO", value)
                elif value == "put":
                    token = Token("PUT", value)
                elif value in ("z", "c"):
                    token = Token("FLAG", value)
                else:
                    token = Token("WORD", value)
                tokens.append(token)
                state = ""
                index -= 1
        elif state == "string":
            if char != value[0]:
                value += char
            else:
                token = Token("STR", value[1:])
                tokens.append(token)
                state = ""
        elif state == "comment":
            if char == "\n":
                state = ""
                index -= 1
        elif state == "label":
            if (len(value) == 0 and char.isalpha()) or \
            (len(value) > 0 and (char.isalnum() or char == "_")):
                value += char
            else:
                token = Token("LABEL", value)
                tokens.append(token)
                index -= 1
                state = ""
        index += 1
    return tokens