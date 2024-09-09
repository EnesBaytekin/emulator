from sys import argv, stderr
from cmc_parser import Parser
from cmc_nodes import Node
from cmc_tokenize import tokenize

def compile(code):
    tokens = tokenize(code)
    parser = Parser(tokens)
    parse_tree = parser.parse()
    Node.reset()
    parse_tree.get()
    Node.fix_addresses()
    return Node.program

def get_code(input_files):
    code = ""
    for file_name in input_files: 
        try:
            with open(file_name, "r") as file:
                code += file.read()
        except IOError:
            error(f"Invalid file name: {file_name}")
    return code

def save_program(program, output_file):
    with open(output_file, "wb") as file:
        file.write(Node.program)

def error(msg, exit_code=1):
    print(msg, file=stderr)
    exit(exit_code)

def get_file_names():
    input_files = argv[1:]
    is_output_file_defined = False
    while "-o" in input_files:
        index = input_files.index("-o")
        if index+1 >= len(input_files):
            error("Give file name after -o")
        output_file = input_files[index+1]
        input_files.pop(index+1)
        input_files.pop(index)
        is_output_file_defined = True
    if len(input_files) == 0:
        error("No input file is given.")
    if not is_output_file_defined:
        output_file = input_files[0].split(".")[0]
    return input_files, output_file

def main():
    input_files, output_file = get_file_names()
    code = get_code(input_files)
    program = compile(code)
    save_program(program, output_file)

if __name__ == "__main__":
    main()