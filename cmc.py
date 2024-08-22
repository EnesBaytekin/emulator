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
    code = ""
    for file_name in files:
        try:
            with open(file_name) as file:
                code += file.read()
        except IOError:
            error(f"File could not find: {file_name}")
    return code

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
        print(code)
        print(output_name)

if __name__ == "__main__":
    main()

