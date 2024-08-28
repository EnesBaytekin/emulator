import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QGridLayout, QPushButton, QGroupBox, QListWidget, QListWidgetItem,
    QSizePolicy, QTextEdit, QAction, QFileDialog, QMenuBar, QShortcut
)
from PyQt5.QtGui import QFont, QKeySequence

class Emulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pc = 0x0000
        self.registers_values = [0x00] * 16
        self.memory = [0x00] * 65536  # 64KB memory
        self.stack = [0x00] * 256  # 256 bytes stack
        self.initUI()
        self.update_ui()

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QHBoxLayout(self.central_widget)

        # Create Menu Bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        
        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        left_layout = QVBoxLayout()

        # Register Display in a GroupBox with Two Rows
        reg_group_box = QGroupBox("Registers")
        reg_layout = QGridLayout()
        self.registers = {}
        for i in range(16):
            reg_label = QLabel(f"R{i:01X}")
            reg_value = QLabel("00")
            self.registers[i] = reg_value
            row = i // 8
            col = i % 8
            reg_layout.addWidget(reg_label, row * 2, col)  # Register name in the first row
            reg_layout.addWidget(reg_value, row * 2 + 1, col)  # Register value in the second row

        reg_group_box.setLayout(reg_layout)
        left_layout.addWidget(reg_group_box)

        # PC, Z, and C Display in a GroupBox with a Table Layout
        status_group_box = QGroupBox("Status Registers")
        status_layout = QGridLayout()
        
        pc_label = QLabel("PC")
        self.pc_value = QLabel("0000")
        status_layout.addWidget(pc_label, 0, 0)
        status_layout.addWidget(self.pc_value, 1, 0)

        z_label = QLabel("Z")
        self.z_flag = QLabel("0")
        status_layout.addWidget(z_label, 0, 1)
        status_layout.addWidget(self.z_flag, 1, 1)

        c_label = QLabel("C")
        self.c_flag = QLabel("0")
        status_layout.addWidget(c_label, 0, 2)
        status_layout.addWidget(self.c_flag, 1, 2)

        status_group_box.setLayout(status_layout)
        left_layout.addWidget(status_group_box)

        # RAM and Stack in a GroupBox side by side
        memory_group_box = QGroupBox("Memory")
        memory_layout = QHBoxLayout()

        # RAM Display using QListWidget
        ram_layout = QVBoxLayout()
        self.ram_search = QLineEdit()
        self.ram_search.setPlaceholderText("Search RAM Address")
        self.ram_search.returnPressed.connect(self.search_ram)
        ram_layout.addWidget(self.ram_search)

        self.ram_list = QListWidget()
        self.populate_ram_list()
        ram_layout.addWidget(self.ram_list)

        memory_layout.addLayout(ram_layout)

        # Stack Display using QListWidget
        stack_layout = QVBoxLayout()
        self.stack_search = QLineEdit()
        self.stack_search.setPlaceholderText("Search Stack Address")
        self.stack_search.returnPressed.connect(self.search_stack)
        stack_layout.addWidget(self.stack_search)

        self.stack_list = QListWidget()
        self.populate_stack_list()
        stack_layout.addWidget(self.stack_list)

        memory_layout.addLayout(stack_layout)

        memory_group_box.setLayout(memory_layout)
        left_layout.addWidget(memory_group_box)

        # Step Button
        self.step_button = QPushButton("Step")
        self.step_button.clicked.connect(self.step)  # Connect Step button to step function
        left_layout.addWidget(self.step_button)

        # Adjust the width of the left layout to be more compact
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        left_widget.setMaximumWidth(300)  # Set a maximum width for the left layout

        # Assembly Code Display on the Right using QTextEdit
        self.asm_group_box = QGroupBox("Assembly Code")
        self.asm_text_edit = QTextEdit()
        self.asm_text_edit.setFont(QFont("Courier", 10))  # Monospace font
        self.asm_text_edit.setReadOnly(False)  # Allow editing
        self.populate_asm_text()

        asm_layout = QVBoxLayout()
        asm_layout.addWidget(self.asm_text_edit)
        self.asm_group_box.setLayout(asm_layout)

        main_layout.addWidget(left_widget)
        main_layout.addWidget(self.asm_group_box, 1)  # 1 indicates the weight of the layout (expandable)

        self.setMinimumWidth(800)  # Set a minimum width for the window

    def initEmulator(self, prog_memory):
        """Initialize emulator state."""
        self.pc = 0x0000
        self.registers_values = [0x00] * 16
        self.memory = list(prog_memory)+[0x00] * (65536-len(prog_memory))  # 64KB memory
        self.stack = [0x00] * 256  # 256 bytes stack
        self.update_ui()

    def update_ui(self):
        """Update the UI with the current state of the emulator."""
        self.update_pc(self.pc)
        for i in range(16):
            self.update_register(i, self.registers_values[i])

    def update_register(self, reg_index, value):
        """Update the value of a register."""
        if 0 <= reg_index < 16:
            self.registers[reg_index].setText(f"{value:02X}")

    def update_pc(self, value):
        """Update the value of the Program Counter."""
        self.pc_value.setText(f"{value:04X}")

    def update_flag(self, flag, value):
        """Update the value of a flag (Z or C)."""
        if flag == 'Z':
            self.z_flag.setText(str(value))
        elif flag == 'C':
            self.c_flag.setText(str(value))

    def update_ram(self, address, value):
        """Update the value in RAM at a given address and select the item."""
        if 0 <= address < 65536:
            item = self.ram_list.item(address)
            item.setText(f"{address:04X}: {value:02X}")
            self.ram_list.setCurrentItem(item)
            self.ram_list.scrollToItem(item)

    def update_stack(self, address, value):
        """Update the value in the Stack at a given address and select the item."""
        if 0 <= address < 65536:
            index = address
            item = self.stack_list.item(index)
            item.setText(f"{address:04X}: {value:02X}")
            self.stack_list.setCurrentItem(item)
            self.stack_list.scrollToItem(item)

    def search_ram(self):
        address_text = self.ram_search.text()
        if not all(c in "0123456789abcdef" for c in address_text):
            return
        address = int(address_text, 16)
        if 0 <= address < 65536:
            item = self.ram_list.item(address)
            self.ram_list.setCurrentItem(item)
            self.ram_list.scrollToItem(item)

    def search_stack(self):
        address_text = self.stack_search.text()
        if not all(c in "0123456789abcdef" for c in address_text):
            return
        address = int(address_text, 16)
        if 0 <= address < 256:
            item = self.stack_list.item(address)
            self.stack_list.setCurrentItem(item)
            self.stack_list.scrollToItem(item)

    def populate_ram_list(self):
        """Populate RAM list with addresses and values."""
        self.ram_list.clear()
        for i in range(65536):
            item_text = f"{i:04X}: {self.memory[i]:02X}"
            item = QListWidgetItem(item_text)
            self.ram_list.addItem(item)

    def populate_stack_list(self):
        """Populate Stack list with addresses and values."""
        self.stack_list.clear()
        for i in range(256):
            addr = i
            item_text = f"{addr:02X}: {self.stack[i]:02X}"
            item = QListWidgetItem(item_text)
            self.stack_list.addItem(item)

    def populate_asm_text(self):
        self.asm_text_edit.setPlainText("")

    def open_file(self):
        """Open a file and load its content into the editor."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if file_name:
            with open(file_name, 'r') as file:
                data = file.read()
            self.asm_text_edit.setPlainText(data)
            from os import system
            output_name = f"{'.'.join(file_name.split('.')[:-1])}.o"
            system(f"cmc.py {file_name} -o {output_name}")
            with open(output_name, 'rb') as file:
                data = file.read()
            self.initEmulator(data)
            self.populate_ram_list()

    def save_file(self):
        """Save the content of the editor to a file."""
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*)")
        if file_name:
            with open(file_name, 'w') as file:
                file.write(self.asm_text_edit.toPlainText())

    def step(self):
        """Execute one step of the program and update the UI."""
        # Example step implementation (simplified)
        if self.pc < 65536:
            # Example: Increment the value at the PC address
            self.memory[self.pc] += 1
            self.update_ram(self.pc, self.memory[self.pc])
            
            # Example: Increment PC (could be replaced by actual instruction execution)
            self.pc = (self.pc + 1) % 65536
            
            # Update PC and RAM
            self.update_pc(self.pc)
            self.update_ram(self.pc, self.memory[self.pc])

            # Optionally, update other parts of the UI (e.g., registers, flags) based on instruction execution

def main():
    app = QApplication(sys.argv)
    emulator = Emulator()
    emulator.setWindowTitle("Emulator")
    emulator.resize(1000, 600)
    emulator.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
