from array import array

class Emulator:
    def get_function(self, ins):
        if   ins == 0b00000: return self.add
        elif ins == 0b00001: return self.sub
        elif ins == 0b00010: return self.mul
        elif ins == 0b00011: return self.div
        elif ins == 0b00100: return self.shl
        elif ins == 0b00101: return self.shr
        elif ins == 0b00110: return self.and_
        elif ins == 0b00111: return self.orr
        elif ins == 0b01000: return self.xor
        elif ins == 0b01001: return self.not_
        elif ins == 0b01010: return self.psh
        elif ins == 0b01011: return self.pop
        elif ins == 0b01100: return self.cal
        elif ins == 0b01101: return self.ret
        elif ins == 0b01110: return self.jmp
        elif ins == 0b01111: return self.jif
        elif ins == 0b10000: return self.lod
        elif ins == 0b10001: return self.lod
        elif ins == 0b10010: return self.ldi
        elif ins == 0b10011: return self.ldi
        elif ins == 0b10100: return self.sto
        elif ins == 0b10101: return self.sto
        elif ins == 0b10110: return self.inc
        elif ins == 0b10111: return self.dec
        elif ins == 0b11000: return self.cmp
        elif ins == 0b11001: return self.nop
        elif ins == 0b11010: return self.hlt
        elif ins == 0b11011: return self.mov

    def __init__(self):
        self.program_counter = 0
        self.registers = array("B", [0]*16)
        self.memory = array("B", [0]*65535)
        self.carry = 0
        self.zero = 0
        self.instructions = array("B", [0, 0, 0])
        self.halted = False

    def load(self, program):
        self.program_counter = 0
        self.registers[0xf] = 0
        self.memory = array("B", program)+self.memory[len(program):]
        self.halted = False

    def step(self):
        self.instructions[0] = self.memory[self.program_counter]
        self.program_counter += 1
        function = self.get_function()
        if function not in [
            self.ret,
            self.nop,
            self.hlt,
        ]:
            self.instructions[1] = self.memory[self.program_counter]
            self.program_counter += 1
            if function in [
                self.cal,
                self.jump,
                self.jif,
                self.lod,
                self.sto,
            ]:
                self.instructions[2] = self.memory[self.program_counter]
                self.program_counter += 1
        self.function()

    def add(self):
        A = (self.instructions[1]&0b11110000)>>4
        B = (self.instructions[1]&0b00001111)
        R = self.registers
        result = R[A]+R[B]
        self.carry = int(result >= 256)
        R[A] = (result)%256
        self.zero = int(R[A] == 0)

    def sub(self):
        A = (self.instructions[1]&0b11110000)>>4
        B = (self.instructions[1]&0b00001111)
        R = self.registers
        result = R[A]-R[B]
        self.carry = int(result < 0)
        R[A] = (result)%256
        self.zero = int(R[A] == 0)

    def mul(self):
        A = (self.instructions[1]&0b11110000)>>4
        B = (self.instructions[1]&0b00001111)
        R = self.registers
        result = R[A]*R[B]
        R[A] = (result&0xff00)>>8
        R[B] = (result&0x00ff)
        self.carry = int(R[A] > 0)
        self.zero = int(R[B] == 0)

    def div(self):
        A = (self.instructions[1]&0b11110000)>>4
        B = (self.instructions[1]&0b00001111)
        R = self.registers
        high = R[A]//R[B]
        low = R[A]%R[B]
        R[A] = (high&0xff00)>>8
        R[B] = (low&0x00ff)
        self.carry = int(R[A] > 0)
        self.zero = int(R[B] == 0)

    def shl(self):
        A = (self.instructions[1]&0b11110000)>>4
        R = self.registers
        result = R[A]<<1
        self.carry = (R[A]&0b10000000)>>7
        R[A] = (result)%256
        self.zero = int(R[A] == 0)

    def shr(self):
        A = (self.instructions[1]&0b11110000)>>4
        R = self.registers
        result = R[A]>>1
        self.carry = (R[A]&0b00000001)
        R[A] = (result)%256
        self.zero = int(R[A] == 0)

    def and_(self):
        A = (self.instructions[1]&0b11110000)>>4
        B = (self.instructions[1]&0b00001111)
        R = self.registers
        result = R[A]&R[B]
        R[A] = (result)%256
        self.zero = int(R[A] == 0)

    def orr(self):
        A = (self.instructions[1]&0b11110000)>>4
        B = (self.instructions[1]&0b00001111)
        R = self.registers
        result = R[A]|R[B]
        R[A] = (result)%256
        self.zero = int(R[A] == 0)

    def xor(self):
        A = (self.instructions[1]&0b11110000)>>4
        B = (self.instructions[1]&0b00001111)
        R = self.registers
        result = R[A]^R[B]
        R[A] = (result)%256
        self.zero = int(R[A] == 0)

    def not_(self):
        A = (self.instructions[1]&0b11110000)>>4
        R = self.registers
        result = ~R[A]
        R[A] = (result)%256
        self.zero = int(R[A] == 0)

    def psh(self):
        A = (self.instructions[1]&0b11110000)>>4
        R = self.registers
        M = self.memory
        M[0xff00+R[0xf]] = R[A]
        R[0xf] += 1

    def pop(self):
        A = (self.instructions[1]&0b11110000)>>4
        R = self.registers
        M = self.memory
        R[0xf] -= 1
        R[A] = M[0xff00+R[0xf]]

    def cal(self):
        addr = (self.instructions[1]<<8)|self.instructions[2]
        R = self.registers
        M = self.memory
        high = (self.program_counter&0xff00)>>8
        low = (self.program_counter&0x00ff)
        M[0xff00+R[0xf]] = high
        R[0xf] += 1
        M[0xff00+R[0xf]] = low
        R[0xf] += 1
        self.program_counter = addr

    def ret(self):
        R = self.registers
        M = self.memory
        R[0xf] -= 1
        low = M[0xff00+R[0xf]]
        R[0xf] -= 1
        high = M[0xff00+R[0xf]]
        self.program_counter = (high<<0xff00)&low

    def jmp(self):
        addr = (self.instructions[1]<<8)|self.instructions[2]
        self.program_counter = addr

    def jif(self):
        zcs = self.instructions[0]&0b00000111
        addr = (self.instructions[1]<<8)|self.instructions[2]
        if (
            zcs == 0b101 and self.zero == 1 or
            zcs == 0b100 and self.zero == 0 or
            zcs == 0b011 and self.zero == 1 or
            zcs == 0b010 and self.zero == 0
        ):
            self.program_counter = addr

    def lod(self):
        A = self.instructions[0]&0b00001111
        addr = (self.instructions[1]<<8)|self.instructions[2]
        R = self.registers
        M = self.memory
        R[A] = M[addr]
        self.zero = int(R[A] == 0)

    def ldi(self):
        A = self.instructions[0]&0b00001111
        imm = self.instructions[1]
        R = self.registers
        R[A] = imm
        self.zero = int(R[A] == 0)

    def sto(self):
        A = self.instructions[0]&0b00001111
        addr = (self.instructions[1]<<8)|self.instructions[2]
        R = self.registers
        M = self.memory
        M[addr] = R[A]
        self.zero = int(R[A] == 0)

    def inc(self):
        A = (self.instructions[1]&0b11110000)>>4
        R = self.registers
        result = R[A]+1
        self.carry = int(result >= 256)
        R[A] = (result)%256
        self.zero = int(R[A] == 0)

    def dec(self):
        A = (self.instructions[1]&0b11110000)>>4
        R = self.registers
        result = R[A]-1
        self.carry = int(result < 0)
        R[A] = (result)%256
        self.zero = int(R[A] == 0)

    def cmp(self):
        A = (self.instructions[1]&0b11110000)>>4
        B = (self.instructions[1]&0b00001111)
        R = self.registers
        result = R[A]-R[B]
        self.carry = int(result >= 256)
        self.zero = int((result%256) == 0)

    def nop(self):
        pass

    def hlt(self):
        self.halted = True

    def mov(self):
        A = (self.instructions[1]&0b11110000)>>4
        B = (self.instructions[1]&0b00001111)
        R = self.registers
        R[B] = R[A]

