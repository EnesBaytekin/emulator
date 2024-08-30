from emulator import Emulator

def color(number):
    return f"\033[{number}m"

class App:
    def __init__(self):
        self.emulator = Emulator()
        self.running = False
        self.m_origin = 0
        self.s_origin = 0xff00
        self.current_file_name = ""
    def start(self):
        self.running = True
        self.draw()
        while self.running:
            data = input("> ")
            if data == "q":
                self.running = False
            elif len(data) > 1 and data[0].lower() in "ms":
                for c in data[1:]:
                    if c.lower() not in "0123456789abcdef":
                        break
                else:
                    if data[0].lower() == "m":
                        addr = int(data[1:], 16)
                        if 0 <= addr < 65536:
                            self.focus_memory_address(addr)
                    elif data[0].lower() == "s":
                        addr = int(data[1:], 16)
                        if 0 <= addr < 256:
                            self.focus_stack_address(addr)
            elif len(data) > 2 and data[:2].lower() == "o ":
                file_name = data[2:].strip()
                try:
                    with open(file_name, "rb") as file:
                        program = file.read()
                    self.emulator.load(program)
                    self.focus_memory_address(0)
                    self.focus_stack_address(0)
                    self.current_file_name = file_name
                except IOError:
                    self.current_file_name = f"invalid file '{file_name}'"
            else:
                self.emulator.step()
                pc = (self.emulator.program_counter>>4)<<4
                if pc-self.m_origin >= 4*0x0010:
                    self.focus_memory_address(pc-3*0x0010)
                elif pc -self.m_origin < 0:
                    self.focus_memory_address(pc)
            self.draw()
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
        screen += f"{color('31;1')}Z:{color(0)} {emu.zero}        {color('32;1')}next-op: "+color('33;1')+ins+color(0)+"\n"
        screen += f"{color('31;1')}C:{color(0)} {emu.carry}\n"
        screen += " "*8+color('33;1')
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
        print(screen)

def main():
    app = App()
    app.start()

if __name__ == "__main__":
    main()

