from sys import argv, stderr
from array import array

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
  "rti": "11100",
  "sei": "11101",
  "cli": "11110",
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

def is_register(element):
    return (
        len(element) == 2 and
        element[0].lower() == "r" and
        element[1].lower() in "0123456789abcdef"
    )

def get_register(element):
    if is_register(element):
        reg_index = int(element[1], 16)
        return reg_index
    else:
        error_line(f"Register expected, got: {element}")

def is_hex(element):
    if is_negative(element):
        element = element[-1:]
    element = element.lower()
    if len(element) <= 1:
        return False
    if element[-1] != "x":
        return False
    for c in element[:-1]:
        if c not in "0123456789abcdef":
            return False
    return True

def is_bin(element):
    if is_negative(element):
        element = element[-1:]
    element = element.lower()
    if len(element) <= 1:
        return False
    if element[-1] != "b":
        return False
    for c in element[:-1]:
        if c not in "01":
            return False
    return True

def is_dec(element):
    if is_negative(element):
        element = element[-1:]
    return element.isdigit()

def is_negative(element):
    return len(element) > 1 and element[0] == "-"

def is_number(element):
    return (
        is_hex(element) or
        is_bin(element) or
        is_dec(element) or
        (
            is_string(element) and
            len(get_string(element)) == 1
        )
    )

def get_number(element):
    if is_hex(element):
        number = element[:-1]
        base = 16
    elif is_bin(element):
        number = element[:-1]
        base = 2
    elif is_dec(element):
        number = element
        base = 10
    elif is_string(element):
        string = get_string(element)
        if len(string) != 1:
            error_line(f"String length must be 1")
        return ord(string)
    else:
        error_line(f"Number expected, got: {element}")
    return int(number, base)

def is_label(element):
    return element in labels

def get_label(element):
    return labels[element]

def get_address(element):
    for sign in "+-":
        if sign in element:
            index = element.index(sign)
            if index == 0 or index == len(element)-1:
                error_line(f"Invalid use of '{sign}' in address: {element}")
            symbol = element[:index]
            rest = element[index+1:]
            if is_label(symbol):
                address = get_label(symbol)
            if is_number(symbol):
                address = get_number(symbol)
            address += get_address(rest)
            return address
    else:
        if is_number(element):
            return get_number(element)
        elif is_label(element):
            return get_label(element)
        else:
            error_line(f"Invalid address: {element}")

def is_string(element):
    return element[0] == element[-1] and element[0] == '"' and '"' not in element[1:-1]

def get_string(element):
    return element[1:-1]

def compile(codes):
    global labels, file_name, line_number, line
    bytelist = array("B", [])
    pc_addr = 0
    labels = {}
    for file_name, code in codes.items():
        lines = [line for line in code.split("\n")]
        for line_number, line in enumerate(lines, 1):
            line = line.strip()
            if len(line) == 0: continue
            if line[0] == ".":
                if len(line) == 1:
                    error_line("Label name cannot be empty.")
                label = line[1:]
                if label in labels:
                    error_line(f"Redefinition of label: {label}")
                labels[label] = pc_addr
            else:
                elements = line.split()
                instruction = elements.pop(0).lower()
                if instruction == "put":
                    if is_string(line[4:]):
                        string = get_string(line[4:])
                        pc_addr += len(string)
                    else:
                        pc_addr += len(elements)
                elif instruction == "go":
                    if len(elements) != 1:
                        error_line(f"Give an address after 'go' statement.")
                    addr = get_address(elements[0])
                    if addr<0 or 65535<addr:
                        error_line(f"'{addr}' is not in the range [0, 65535]")
                    pc_addr = addr
                elif instruction in [
                    "jmp","cal","jif","lod","sto"
                ]:
                    pc_addr += 3
                elif instruction in [
                    "add","sub","mul","div",
                    "and","orr","xor","cmp","mov",
                    "shl","shr","not",
                    "psh","pop","inc","dec","ldi"
                ]:
                    pc_addr += 2
                elif instruction in [
                    "ret","nop","hlt","rti","sei","cli"
                ]:
                    pc_addr += 1
    for file_name, code in codes.items():
        lines = [line for line in code.split("\n")]
        for line_number, line in enumerate(lines, 1):
            line = line.strip()
            if len(line) == 0: continue
            if line[0] == ".":
                pass
            else:
                bitstring = ""
                elements = line.split()
                instruction = elements.pop(0).lower()
                if instruction in table:
                    bitstring += table[instruction]
                elif instruction == "put":
                    if is_label(line[4:]):
                        addr = get_address(line[4:])
                        bitstring += bin(addr)[2:].zfill(16)
                    elif is_string(line[4:]):
                        string = get_string(line[4:])
                        for c in string:
                            byte = ord(c)
                            bitstring += bin(byte)[2:].zfill(8)
                    else:
                        for element in elements:
                            byte = get_number(element)
                            if byte<0 or 256<=byte:
                                error_line(f"'{byte}' is not in the range [0, 255]")
                            bitstring += bin(byte)[2:].zfill(8)
                elif instruction == "go":
                    addr = get_address(elements[0])
                    if addr<0 or 65535<addr:
                        error_line(f"'{addr}' is not in the range [0, 65535]")
                    while len(bitstring) > 0:
                        byte = int(bitstring[:8], 2)
                        bitstring = bitstring[8:]
                        bytelist.append(byte)

                    while len(bytelist) < addr:
                        bytelist.append(0)
                else:
                    error_line("Unknown instruction.")
                if instruction in [
                    "jmp","cal"
                ]:
                    bitstring += "000"
                    if len(elements) != 1:
                        error_line(f"'{instruction}' takes 1 arguments, {len(elements)} given.")
                    element = elements[0]
                    addr = get_address(element)
                    if addr<0 or 65535<addr:
                        error_line(f"'{addr}' is not in the range [0, 65535]")
                    bitstring += bin(addr)[2:].zfill(16)
                elif instruction in [
                    "jif"
                ]:
                    if len(elements) != 3:
                        error_line(f"'{instruction}' takes 3 arguments, {len(elements)} given.")
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
                    addr = get_address(element)
                    if addr<0 or 65535<addr:
                        error_line(f"'{addr}' is not in the range [0, 255]")
                    bitstring += bin(addr)[2:].zfill(16)
                elif instruction in [
                    "ldi"
                ]:
                    if len(elements) != 2:
                        error_line(f"'{instruction}' takes 2 arguments, {len(elements)} given.")
                    element = elements[0]
                    reg_index = get_register(element)
                    bitstring += bin(reg_index)[2:].zfill(4)
                    element = elements[1]
                    imm = get_number(element)
                    if imm<0 or 256<=imm:
                        error_line(f"'{imm}' is not in the range [0, 255]")
                    bitstring += bin(imm)[2:].zfill(8)
                elif instruction in [
                    "lod","sto"
                ]:
                    if len(elements) != 2:
                        error_line(f"'{instruction}' takes 2 arguments, {len(elements)} given.")
                    element = elements[0]
                    reg_index = get_register(element)
                    bitstring += bin(reg_index)[2:].zfill(4)
                    element = elements[1]
                    addr = get_address(element)
                    if addr<0 or 65535<addr:
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
                        reg_index = get_register(element)
                        bitstring += bin(reg_index)[2:].zfill(4)
                elif instruction in [
                    "shl","shr","not",
                    "psh","pop","inc","dec"
                ]:
                    bitstring += "000"
                    if len(elements) != 1:
                        error_line(f"'{instruction}' takes 1 arguments, {len(elements)} given.")
                    element = elements[0]
                    reg_index = get_register(element)
                    bitstring += bin(reg_index)[2:].zfill(4)
                    bitstring += "0000"
                elif instruction in [
                    "ret","nop","hlt","rti","sei","cli"
                ]:
                    bitstring += "000"
                    if len(elements) != 0:
                        error_line(f"'{instruction}' takes no arguments, {len(elements)} given.")
                while len(bitstring) > 0:
                    byte = int(bitstring[:8], 2)
                    bitstring = bitstring[8:]
                    bytelist.append(byte)
    return bytes(bytelist+array("B", [0 for i in range(2**15-(len(bytelist)))]))

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
        codes = get_input(files)
        codes = {name: "\n".join([line.split(";")[0] for line in code.split("\n")]) for name, code in codes.items()}
        bytecode = compile(codes)
        last_line = []
        line_bytes = []
        changed = True
        for line in range(len(bytecode)//16+1):
            last_line = line_bytes
            line_bytes = bytecode[line*16:line*16+16]
            if line_bytes == last_line:
                if changed:
                    print("...")
                changed = False
                continue
            changed = True
            print(f"{hex(line<<4)[2:].zfill(4)}:", end=" ")
            for byte in line_bytes:
                print(hex(byte)[2:].zfill(2), end=" ")
            print()
        with open(output_name, "wb") as file:
            file.write(bytecode)
        print(f"Saved as '{output_name}'")

if __name__ == "__main__":
    main()

