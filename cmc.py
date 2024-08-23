from sys import argv, stderr

table = {
  "add": "00000",
  "sub": "00001",
  "mul": "00010",
  "div": "00011",
  "shl": "00100",
  "shr": "00101",
  "and": "00110",
  "orr": "00111",
  "xor": "01000",
  "not": "01001",
  "psh": "01010",
  "pop": "01011",
  "cal": "01100",
  "ret": "01101",
  "jmp": "01110",
  "jif": "01111",
  "lod": "1000",
  "ldi": "1001",
  "sto": "1010",
  "inc": "10110",
  "dec": "10111",
  "cmp": "11000",
  "nop": "11001",
  "hlt": "11010",
  "mov": "11011",
}

def error(msg, code=1):
    print("Error:", msg, file=stderr)
    if code > 0:
        exit(code)

def help():
    print("""
Usage:
    cmc [OPTIONS] <file...>

Options:
    -o <name>   Give a name to the
                output file.
""")

def get_input(files):
    codes = {}
    for file_name in files:
        try:
            with open(file_name) as file:
                codes[file_name] = file.read()
        except IOError:
            error(f"File could not find: {file_name}")
    return codes

def error_line(msg, code=1):
    index = line_number
    print(f"Error at '{file_name}', line: {index}", file=stderr)
    print(msg, file=stderr)
    indexstr = str(index)
    if index > 1: print(f"{index-1}".rjust(len(indexstr))+" | ...", file=stderr)
    print(f"{index} | {line}", file=stderr)
    print(f"{index+1}".rjust(len(indexstr))+" | ...", file=stderr)
    exit(code)

def check_if_register(element):
    if len(element) == 2 and \
    element[0].lower() == "r" and \
    element[1].lower() in "0123456789abcdef":
        reg_index = int(element[1], 16)
        return reg_index
    else:
        error_line(f"Register expected, got: {element}")

def check_if_number(element):
    if element in labels:
        return labels[element]
    element = element.lower()
    if element[-1] == "x":
        chars = "0123456789abcdef"
        number = element[:-1]
        base = 16
    elif element[-1] == "b":
        chars = "01"
        number = element[-1]
        base = 2
    else:
        chars = "0123455789"
        number = element
        base = 10
    if len(number) == 0:
        error_line(f"Number expected, got: {element}")
    for c in number:
        if c not in chars:
            error_line(f"Number expected, got: {element}")
    return int(number, base)

def compile(codes):
    global labels, file_name, line_number, line
    bytelist = []
    addr = 0
    labels = {}
    for file_name, code in codes.items():
        lines = [line for line in code.split("\n")]
        for line_number, line in enumerate(lines, 1):
            if len(line) == 0: continue
            if line[0] == ".":
                if len(line) == 1:
                    error_line("Label name cannot be empty.")
                label = line[1:]
                if label in labels:
                    error_line(f"Redefinition of label: {label}")
                labels[label] = addr
            else:
                elements = line.split()
                instruction = elements.pop(0).lower()
                if instruction in [
                    "jmp","cal","jif","lod","sto"
                ]:
                    addr += 3
                elif instruction in [
                    "add","sub","mul","div",
                    "and","orr","xor","cmp","mov",
                    "shl","shr","not",
                    "psh","pop","inc","dec","ldi"
                ]:
                    addr += 2
                elif instruction in [
                    "ret","nop","hlt"
                ]:
                    addr += 1
    for file_name, code in codes.items():
        lines = [line for line in code.split("\n")]
        for line_number, line in enumerate(lines, 1):
            if len(line) == 0: continue
            if line[0] == ".":
                pass
            else:
                bitstring = ""
                elements = line.split()
                instruction = elements.pop(0).lower()
                if instruction in table:
                    bitstring += table[instruction]
                else:
                    line_error("Unknown instruction.")
                if instruction in [
                    "jmp","cal"
                ]:
                    bitstring += "000"
                    if len(elements) != 1:
                        error_line(f"'{instruction}' takes 1 arguments, {len(elements)} given.")
                    element = elements[0]
                    addr = check_if_number(element)
                    if addr<0 or 65535<=addr:
                        error_line(f"'{addr}' is not in the range [0, 65535]")
                    bitstring += bin(addr)[2:].zfill(16)
                elif instruction in [
                    "jif"
                ]:
                    if len(elements) != 3:
                        error_line(f"'{instruction}' takes 1 arguments, {len(elements)} given.")
                    element = elements[0]
                    if len(element) == 1 and \
                    element.lower() in "zc":
                        flag = element.lower()
                    else:
                        error_line(f"'Z or C expected, {element} given.")
                    element = elements[1]
                    if len(element) == 1 and \
                    element.lower() in "01":
                        set_ = element
                    else:
                        error_line(f"'Z or C expected, {element} given.")
                    if flag == "z":
                        bitstring += "10"
                    if flag == "c":
                        bitstring += "01"
                    bitstring += set_
                    element = elements[2]
                    addr = check_if_number(element)
                    if addr<0 or 256<=addr:
                        error_line(f"'{addr}' is not in the range [0, 255]")
                    bitstring += bin(addr)[2:].zfill(16)
                elif instruction in [
                    "ldi"
                ]:
                    if len(elements) != 2:
                        error_line(f"'{instruction}' takes 2 arguments, {len(elements)} given.")
                    element = elements[0]
                    reg_index = check_if_register(element)
                    bitstring += bin(reg_index)[2:].zfill(4)
                    element = elements[1]
                    imm = check_if_number(element)
                    if imm<0 or 256<=imm:
                        error_line(f"'{imm}' is not in the range [0, 255]")
                    bitstring += bin(imm)[2:].zfill(8)
                elif instruction in [
                    "lod","sto"
                ]:
                    if len(elements) != 2:
                        error_line(f"'{instruction}' takes 2 arguments, {len(elements)} given.")
                    element = elements[0]
                    reg_index = check_if_register(element)
                    bitstring += bin(reg_index)[2:].zfill(4)
                    element = elements[1]
                    addr = check_if_number(element)
                    if addr<0 or 65535<=addr:
                        error_line(f"'{addr}' is not in the range [0, 65535]")
                    bitstring += bin(addr)[2:].zfill(16)
                elif instruction in [
                    "add","sub","mul","div",
                    "and","orr","xor","cmp","mov"
                ]:
                    bitstring += "000"
                    if len(elements) != 2:
                        error_line(f"'{instruction}' takes 2 arguments, {len(elements)} given.")
                    for element in elements:
                        reg_index = check_if_register(element)
                        bitstring += bin(reg_index)[2:].zfill(4)
                elif instruction in [
                    "shl","shr","not",
                    "psh","pop","inc","dec"
                ]:
                    bitstring += "000"
                    if len(elements) != 1:
                        error_line(f"'{instruction}' takes 1 arguments, {len(elements)} given.")
                    element = elements[0]
                    reg_index = check_if_register(element)
                    bitstring += bin(reg_index)[2:].zfill(4)
                    bitstring += "0000"
                elif instruction in [
                    "ret","nop","hlt"
                ]:
                    bitstring += "000"
                    if len(elements) != 0:
                        error_line(f"'{instruction}' takes no arguments, {len(elements)} given.")
                while len(bitstring) > 0:
                    byte = int(bitstring[:8], 2)
                    bitstring = bitstring[8:]
                    bytelist.append(byte)
    return bytes(bytelist)

def main():
    if len(argv) == 1:
        help()
    else:
        output_name = "a"
        files = argv[1:]
        if "-o" in files:
            index = files.index("-o")
            if index+1 < len(files):
                output_name = files[index+1]
                files.pop(index+1)
                files.pop(index)
            else:
                error("No output name given after -o")
        code = get_input(files)
        bytecode = compile(code)
        print(bytecode)
        with open(output_name, "wb") as file:
            file.write(bytecode)
        print(f"Saved as '{output_name}'")

if __name__ == "__main__":
    main()

