from sys import argv

class Register:
    def __init__(self, size):
        self.size = size
        self.value = 0
    def write(self, value):
        self.value = value%(2**self.size)
    def read(self):
        return self.value

class ProgramCounter(Register):
    def __init__(self):
        super().__init__(16)
    def increment(self):
        self.value += 1
    def jump(self, address):
        self.value = address
    def writeL(self, value):
        self.value = (self.value&0xff00)|(value%256)
    def writeH(self, value):
        self.value = (self.value&0x00ff)|((value%256)<<8)
    def readL(self):
        return self.value&0x00ff
    def readH(self):
        return (self.value&0xff00)>>8
    def __repr__(self):
        return f"{self.value}"

def add():
    A = Il>>4
    B = Il&0x0f
    global Z, C
    R[A] = R[A]+R[B]
    Z = R[A] == 0
    C = R[A] >= 256
    R[A] = R[A]%256

def sub():
    A = Il>>4
    B = Il&0x0f
    global Z, C
    R[A] = R[A]-R[B]
    Z = R[A] == 0
    C = R[A] < 0
    R[A] = R[A]%256

def mul():
    A = Il>>4
    B = Il&0x0f
    global Z, C
    temp = R[A]*R[B]
    R[A] = temp&0xff00
    R[B] = temp&0x00ff
    Z = R[B] == 0
    C = R[A] > 0

def div():
    A = Il>>4
    B = Il&0x0f
    global Z, C
    R[A] = R[A]//R[B]
    R[B] = R[A]%R[B]
    Z = R[B] == 0
    C = R[A] > 0

def shl():
    A = Il>>4
    global Z, C
    R[A] = R[A]<<1
    Z = R[A] == 0
    C = R[A] >= 256
    R[A] = R[A]%256

def shr():
    A = Il>>4
    global Z, C
    R[A] = R[A]>>1
    Z = R[A] == 0
    C = R[A] >= 256
    R[A] = R[A]%256

def and_():
    A = Il>>4
    B = Il&0x0f
    global Z
    R[A] = R[A]&R[B]
    Z = R[A] == 0

def orr():
    A = Il>>4
    B = Il&0x0f
    global Z
    R[A] = R[A]|R[B]
    Z = R[A] == 0

def xor():
    A = Il>>4
    B = Il&0x0f
    global Z
    R[A] = R[A]^R[B]
    Z = R[A] == 0

def not_():
    A = Il>>4
    global Z
    R[A] = ~R[A]
    Z = R[A] == 0

def psh():
    A = Il>>4
    S[R[0xf]] = R[A]
    R[0xf] += 1

def pop():
    A = Il>>4
    R[0xf] -= 1
    R[A] = S[R[0xf]]

def cal():
    addr = (Il<<8)|I3
    S[R[0xf]] = PC.readH()
    R[0xf] += 1
    S[R[0xf]] = PC.readL()
    R[0xf] += 1
    PC.write(addr)

def ret():
    R[0xf] -= 1
    PC.writeL(S[R[0xf]])
    R[0xf] -= 1
    PC.writeH(S[R[0xf]])

def jmp():
    addr = (Il<<8)|I3
    PC.write(addr)

def jif():
    zcs = Ih&0b00000111
    if (zcs == 0b101 and Z) \
    or (zcs == 0b100 and not Z) \
    or (zcs == 0b011 and C) \
    or (zcs == 0b010 and not C):
        addr = (Il<<8)|I3
        PC.write(addr)

def lod():
    A = Ih&0x0f
    addr = (Il<<8)|I3
    global Z
    R[A] = M[addr]
    Z = R[A] == 0

def ldi():
    A = Ih&0x0f
    imm = Il
    global Z
    R[A] = imm
    Z = R[A] == 0

def sto():
    A = Ih&0x0f
    addr = (Il<<8)|I3
    global Z
    M[addr] = R[A]
    Z = R[A] == 0

def inc():
    A = Il>>4
    global Z, C
    R[A] = R[A]+1
    Z = R[A] == 0
    C = R[A] >= 256
    R[A] = R[A]%256

def dec():
    A = Il>>4
    global Z, C
    R[A] = R[A]-1
    Z = R[A] == 0
    C = R[A] < 0
    R[A] = R[A]%256

def cmp():
    A = Il>>4
    B = Il&0x0f
    global Z, C
    diff = R[A]-R[B]
    Z = diff == 0
    C = diff < 0

def nop():
    pass

def hlt():
    exit()

def mov():
    A = Il>>4
    B = Il&0x0f
    R[B] = R[A]

def instruction_table():
    ROM = {}
    ROM[0b00000] = add
    ROM[0b00001] = sub
    ROM[0b00010] = mul
    ROM[0b00011] = div
    ROM[0b00100] = shl
    ROM[0b00101] = shr
    ROM[0b00110] = and_
    ROM[0b00111] = orr
    ROM[0b01000] = xor
    ROM[0b01001] = not_
    ROM[0b01010] = psh
    ROM[0b01011] = pop
    ROM[0b01100] = cal
    ROM[0b01101] = ret
    ROM[0b01110] = jmp
    ROM[0b01111] = jif
    ROM[0b10000] = lod
    ROM[0b10001] = lod
    ROM[0b10010] = ldi
    ROM[0b10011] = ldi
    ROM[0b10100] = sto
    ROM[0b10101] = sto
    ROM[0b10110] = inc
    ROM[0b10111] = dec
    ROM[0b11000] = cmp
    ROM[0b11001] = nop
    ROM[0b11010] = hlt
    ROM[0b11011] = mov
    return ROM

def main():
    global Z, C, Ih, Il, I3, R, PC, M, S
    R = [0 for _ in range(16)]
    Z = 0
    C = 0
    PC = ProgramCounter()
    ROM = instruction_table()
    with open(argv[1], "rb") as file:
        program = list(file.read())
    M = program+[0xaa for _ in range(2**16-len(program))]
    S = M[2**16-2**8:]
    Ih = 0
    Il = 0
    I3 = 0
    bits = lambda x: bin(x)[2:].zfill(8)
    byte = lambda x: hex(x)[2:].zfill(2)
    while True:
        print("PC:", hex(PC.value)[2:].zfill(4))
        print("Z:", int(Z), "C:", int(C))
        print("R:", end=" ")
        for i in R:
            print(byte(i), end=" ")
        print()
        print("M:")
        for j in range(4):
            for i in M[j*16:j*16+16]:
                print(byte(i), end=" ")
            print()
        print("S:", end=" ")
        for i in S[:16]:
            print(byte(i), end=" ")
        print()
        print(R[0])
        if "q" in input("press enter"):
            break
        Ih = M[PC.read()]
        PC.increment()
        ins = ROM[(Ih&0b11111000)>>3]
        print(ins.__name__)
        if ins.__name__ in ["ret", "nop", "hlt"]:
            print("I:", bits(Ih))
        else:
            Il = M[PC.read()]
            PC.increment()
            if ins.__name__ in ["jmp", "jif", "cal", "sto", "lod"]:
                I3 = M[PC.read()]
                PC.increment()
                print("I:", bits(Ih), bits(Il), bits(I3))
            else:
                print("I:", bits(Ih), bits(Il))
        ins()

if __name__ == "__main__":
    main()
