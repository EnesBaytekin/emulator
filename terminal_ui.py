from emulator import Emulator

class App:
    def __init__(self):
        self.emulator = Emulator()
        self.running = False
    def start(self):
        self.running = True
        self.draw()
        while self.running:
            if "q" in input("press enter to step"):
                self.running = False
                break
            self.emulator.step()
            self.draw()
    def draw(self):
        emu = self.emulator
        screen = ""
        screen += f"PC: {emu.program_counter:04x}\nZ: {emu.zero} C: {emu.carry}\n"
        screen += "\nregs  : "
        for i in range(16):
            screen += f"{emu.registers[i]:02x} "
        screen += "\n"+" "*8
        for i in range(16):
            screen += f"{i:01x}  "
        screen += "\n"
        for i in range(4):
            screen += f"{(0+i*16):04x}..: "
            for j in range(16):
                screen += f"{emu.memory[0+i*16+j]:02x} "
            screen += "\n"
        print(screen)

def main():
    app = App()
    app.start()
    

if __name__ == "__main__":
    main()

