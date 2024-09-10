from sys import argv, stderr
from array import array

def get_byte_list():
    if len(argv) != 2:
        print("Give exactly one file name", file=stderr)
        exit(1)
    with open(argv[1], "rb") as file:
        byte_list = file.read()
    return array("B", byte_list)

def main():
    byte_list = get_byte_list()
    # column names
    print(end=" "*7)
    for index in range(16):
        if index == 8:
            print(end=" ")
        print(f"  {index:01x}", end="")
    print()
    # lines
    row = None
    last_row = None
    is_written = False
    for line_index in range(len(byte_list)//16):
        last_row = row
        row = byte_list[line_index*16:(line_index+1)*16]
        if last_row == row:
            if not is_written:
                print("...")
                is_written = True
            continue
        is_written = False
        print(f"{line_index:03x}0..:", end="")
        for index in range(16):
            if index == 8:
                print(end=" ")
            print(f" {row[index]:02x}", end="")
        print(end=" |")
        for index in range(16):
            char = chr(row[index])
            if not char.isprintable():
                char = " "
            print(end=char)
        print(end="|\n")
    print(f"total bytes: {len(byte_list)}")
        



if __name__ == "__main__":
    main()
