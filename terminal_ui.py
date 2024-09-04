from emulator import Emulator
from sys import argv
from _thread import start_new_thread
from time import time, sleep
from utils import get_character, clear_terminal

def color(number):
    return f"\033[{number}m"

class App:
    def __init__(self):
        self.emulator = Emulator()
        self.running = False
        self.m_origin = 0
        self.s_origin = 0xff00
        self.is_auto = False
        self.has_thread = False
        self.current_file_name = ""
        if len(argv) > 1:
            file_name = argv[1]
            self.load_program(file_name)
        self.speed = 1000
    def start(self):
        self.running = True
        self.draw()
        last_auto = self.is_auto
        while self.running:
            data = input("> ")
            last_auto = self.is_auto
            self.is_auto = False
            if data == "q":
                self.running = False
            elif len(data) > 1 and data[0].lower() in "ms":
                if data[1:] in ("+", "-"):
                    if data[0].lower() =="m":
                        if data[1:] == "+":
                            addr = (self.m_origin+16)&0xffff
                        elif data[1:] == "-":
                            addr = (self.m_origin-16)&0xffff
                        self.focus_memory_address(addr)
                    elif data[0].lower() == "s":
                        if data[1:] == "+":
                            addr = (self.s_origin+16)&0xffff
                        elif data[1:] == "-":
                            addr = (self.s_origin-16)&0xffff
                        else:
                            addr = int(data[1:], 16)
                        self.focus_stack_address(addr)
                for c in data[1:]:
                    if c.lower() not in "0123456789abcdef":
                        break
                else:
                    if data[0].lower() == "m":
                        if 0 <= addr < 65536:
                            self.focus_memory_address(addr)
                    elif data[0].lower() == "s":
                        addr = int(data[1:], 16)
                        if 0 <= addr < 256:
                            self.focus_stack_address(addr)
            elif len(data) > 2 and data[:2].lower() == "o ":
                file_name = data[2:].strip()
                self.load_program(file_name)
            elif len(data) == 1 and data.lower() == "r":
                self.load_program(self.current_file_name)
            elif len(data) == 1 and data.lower() == "a":
                self.is_auto = True
            elif len(data) > 1 and data[0].lower() == "." and data[1:].isdigit():
                self.speed = int(data[1:])
                if last_auto:
                    self.is_auto = True
                else:
                    self.step()
            elif data == "+":
                self.speed = int(self.speed*3/2)
                if last_auto:
                    self.is_auto = True
                else:
                    self.step()
            elif data == "-":
                self.speed = int(self.speed*2/3)
                if last_auto:
                    self.is_auto = True
                else:
                    self.step()
            else:
                self.step()
            if self.is_auto:
                self.start_auto()
            else:
                self.draw()
    def start_auto(self):
        last = 0
        now = 0
        timer_step = 0
        timer_draw = 0
        while self.is_auto:
            if self.emulator.halted:
                self.is_auto = False
                break
            last = now
            now = time()
            dt = now-last
            char = get_character()
            if char is not None:
                if char == "\x03":
                    self.is_auto = False
                    break
                if char == "":
                    char = " "
                self.emulator.set_interrupt()
                self.emulator.memory[0x8000] = ord(char)&0xff
            timer_step += dt
            timer_draw += dt
            if timer_step > 1/self.speed:
                timer_step = 0
                self.step()
            if timer_draw > 0.05:
                timer_draw = 0
                self.draw()
        self.draw()
    def step(self):
        self.emulator.step()
        pc = (self.emulator.program_counter>>4)<<4
        if pc-self.m_origin >= 4*0x0010:
            self.focus_memory_address(pc-3*0x0010)
        elif pc -self.m_origin < 0:
            self.focus_memory_address(pc)
        sp = (self.emulator.registers[0xf]>>4)<<4
        if sp-self.s_origin >= 2*0x0010:
            self.focus_stack_address(sp-1*0x0010)
        elif sp-self.s_origin < 0:
            self.focus_stack_address(sp)
    def load_program(self, file_name):
        try:
            with open(file_name, "rb") as file:
                program = file.read()
            self.emulator.load(program)
            self.focus_memory_address(0)
            self.focus_stack_address(0)
            self.current_file_name = file_name
        except IOError:
            self.current_file_name = f"invalid file '{file_name}'"
    def focus_memory_address(self, addr):
        self.m_origin = (addr>>4)<<4
        self.m_origin = min(self.m_origin, 0xfff0-3*0x0010)
    def focus_stack_address(self, addr):
        self.s_origin = 0xff00|(addr>>4)<<4
        self.s_origin = min(self.s_origin, 0xfff0-1*0x0010)
    def draw(self):
        emu = self.emulator
        screen = ""
        ins = emu.get_function((emu.memory[emu.program_counter]&0b11111000)>>3).__name__[:3]
        file_name = self.current_file_name
        file_name = (file_name if len(file_name)<40 else (file_name[:38]+"...")).rjust(46)
        screen += f"{color('31;1')}PC:{color(0)} {emu.program_counter:04x} {file_name}\n"
        screen += f"{color('31;1')}Z:{color(0)} {emu.zero}        {color('32;1')}next-op: "+color('33;1')+ins+color(0)
        screen += f"    {color('31;1')}HALTED{color(0)}" if emu.halted else ""
        screen += f"\n{color('31;1')}C:{color(0)} {emu.carry}"+" "*36+f"speed: {self.speed}".rjust(15)
        screen += f"\n{color('31;1')}IE:{color(0)} {emu.interrupt_enable}"
        screen += "\n"+" "*8+color('33;1')
        for i in range(16):
            screen += f"{i:01x}  "
        screen += f"\n{color('31;1')}regs  : "+color(0)
        for i in range(16):
            screen += f"{emu.registers[i]:02x} "
        screen += f"\n{color('31;1')}memory:{color(0)}\n"
        for i in range(4):
            screen += f"{color('33;1')}{(self.m_origin+i*16):04x}..: {color(0)}"
            for j in range(16):
                addr = self.m_origin+i*16+j
                if addr == emu.program_counter:
                    screen += color("44;30;1")
                screen += f"{emu.memory[addr]:02x}"
                if addr == emu.program_counter:
                    screen += color(0)
                screen += " "
            screen += "\n"
        screen += f"{color('31;1')}stack:{color(0)}\n"
        for i in range(2):
            screen += f"{color('33;1')}{(self.s_origin++i*16):04x}..: {color(0)}"
            for j in range(16):
                addr = self.s_origin+i*16+j
                if addr == 0xff00|emu.registers[0xf]:
                    screen += color("44;30;1")
                screen += f"{emu.memory[addr]:02x}"
                if addr == 0xff00|emu.registers[0xf]:
                    screen += color(0)
                screen += " "
            screen += "\n"
        width = 32
        height = 8
        screen += "+"+"-"*width+"+\n"
        for row in range(height):
            screen += "|"
            for column in range(width):
                byte = emu.memory[0xfe00+row*width+column]
                if 32 <= byte < 128:
                    character = chr(byte)
                else:
                    character = " "
                screen += character
            screen += "|\n"
        screen += "+"+"-"*width+"+\n"
        if self.is_auto:
            screen += "Auto mode is active. Ctrl+C to exit."
        clear_terminal()
        print(screen)

def main():
    app = App()
    app.start()

if __name__ == "__main__":
    main()

