import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QGridLayout, QPushButton, QGroupBox, QListWidget, QListWidgetItem,
    QSizePolicy, QTextEdit, QPlainTextEdit, QAction, QFileDialog, QMenuBar, QShortcut
)
from PyQt5.QtGui import QFont, QPainter, QColor, QTextCursor, QTextFormat
from PyQt5.QtCore import QRect, QSize, Qt

class QCodeEditor(QPlainTextEdit):
    '''
    QCodeEditor inherited from QPlainTextEdit providing:
        
        numberBar - set by DISPLAY_LINE_NUMBERS flag equals True
        curent line highligthing - set by HIGHLIGHT_CURRENT_LINE flag equals True
        setting up QSyntaxHighlighter

    references:
        https://john.nachtimwald.com/2009/08/19/better-qplaintextedit-with-line-numbers/    
        http://doc.qt.io/qt-5/qtwidgets-widgets-codeeditor-example.html
    
    '''
    class NumberBar(QWidget):
        '''class that deifnes textEditor numberBar'''

        def __init__(self, editor):
            QWidget.__init__(self, editor)
            
            self.editor = editor
            self.editor.blockCountChanged.connect(self.updateWidth)
            self.editor.updateRequest.connect(self.updateContents)
            self.font = QFont()
            self.numberBarColor = QColor("#e8e8e8")
                     
        def paintEvent(self, event):
            
            painter = QPainter(self)
            painter.fillRect(event.rect(), self.numberBarColor)
             
            block = self.editor.firstVisibleBlock()
 
            # Iterate over all visible text blocks in the document.
            while block.isValid():
                blockNumber = block.blockNumber()
                block_top = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top()
 
                # Check if the position of the block is out side of the visible area.
                if not block.isVisible() or block_top >= event.rect().bottom():
                    break
 
                # We want the line number for the selected line to be bold.
                if blockNumber == self.editor.textCursor().blockNumber():
                    self.font.setBold(True)
                    painter.setPen(QColor("#000000"))
                else:
                    self.font.setBold(False)
                    painter.setPen(QColor("#717171"))
                painter.setFont(self.font)
                
                # Draw the line number right justified at the position of the line.
                paint_rect = QRect(0, block_top, self.width(), self.editor.fontMetrics().height())
                painter.drawText(paint_rect, Qt.AlignRight, str(blockNumber+1))
 
                block = block.next()
 
            painter.end()
            
            QWidget.paintEvent(self, event)
 
        def getWidth(self):
            count = self.editor.blockCount()
            width = self.fontMetrics().width(str(count)) + 10
            return width      
        
        def updateWidth(self):
            width = self.getWidth()
            if self.width() != width:
                self.setFixedWidth(width)
                self.editor.setViewportMargins(width, 0, 0, 0);
 
        def updateContents(self, rect, scroll):
            if scroll:
                self.scroll(0, scroll)
            else:
                self.update(0, rect.y(), self.width(), rect.height())
            
            if rect.contains(self.editor.viewport().rect()):   
                fontSize = self.editor.currentCharFormat().font().pointSize()
                self.font.setPointSize(fontSize)
                self.font.setStyle(QFont.StyleNormal)
                self.updateWidth()
                
        
    def __init__(self, DISPLAY_LINE_NUMBERS=True, HIGHLIGHT_CURRENT_LINE=True,
                 SyntaxHighlighter=None, *args):        
        '''
        Parameters
        ----------
        DISPLAY_LINE_NUMBERS : bool 
            switch on/off the presence of the lines number bar
        HIGHLIGHT_CURRENT_LINE : bool
            switch on/off the current line highliting
        SyntaxHighlighter : QSyntaxHighlighter
            should be inherited from QSyntaxHighlighter
        
        '''                  
        super(QCodeEditor, self).__init__()
        
        self.setFont(QFont("Courier", 11))
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
                               
        self.DISPLAY_LINE_NUMBERS = DISPLAY_LINE_NUMBERS

        if DISPLAY_LINE_NUMBERS:
            self.number_bar = self.NumberBar(self)
            
        if HIGHLIGHT_CURRENT_LINE:
            self.currentLineNumber = None
            self.currentLineColor = self.palette().alternateBase()
            # self.currentLineColor = QColor("#e8e8e8")
            self.cursorPositionChanged.connect(self.highligtCurrentLine)
        
        if SyntaxHighlighter is not None: # add highlighter to textdocument
           self.highlighter = SyntaxHighlighter(self.document())         
                 
    def resizeEvent(self, *e):
        '''overload resizeEvent handler'''
                
        if self.DISPLAY_LINE_NUMBERS:   # resize number_bar widget
            cr = self.contentsRect()
            rec = QRect(cr.left(), cr.top(), self.number_bar.getWidth(), cr.height())
            self.number_bar.setGeometry(rec)
        
        QPlainTextEdit.resizeEvent(self, *e)

    def highligtCurrentLine(self):
        newCurrentLineNumber = self.textCursor().blockNumber()
        if newCurrentLineNumber != self.currentLineNumber:                
            self.currentLineNumber = newCurrentLineNumber
            hi_selection = QTextEdit.ExtraSelection() 
            hi_selection.format.setBackground(self.currentLineColor)
            hi_selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            hi_selection.cursor = self.textCursor()
            hi_selection.cursor.clearSelection() 
            self.setExtraSelections([hi_selection])           

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
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
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
        self.step_button.clicked.connect(self.step)
        left_layout.addWidget(self.step_button)

        # Adjust the width of the left layout to be more compact
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        left_widget.setMaximumWidth(300)

        # Assembly Code Display on the Right using LineNumberedTextEdit
        self.asm_group_box = QGroupBox("Assembly Code")
        self.asm_text_edit = QCodeEditor()
        # self.asm_text_edit.setFont(QFont("Courier", 11))
        self.populate_asm_text()

        asm_layout = QVBoxLayout()
        asm_layout.addWidget(self.asm_text_edit)
        self.asm_group_box.setLayout(asm_layout)

        main_layout.addWidget(left_widget)
        main_layout.addWidget(self.asm_group_box, 1)

        self.setMinimumWidth(800)

    def initEmulator(self):
        """Initialize emulator state."""
        self.pc = 0x0000
        self.registers_values = [0x00] * 16
        self.memory = [0x00] * 65536
        self.stack = [0x00] * 256
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
        if not all(c in "0123456789ABCDEF" for c in address_text.upper()) or len(address_text) > 4:
            return

        address = int(address_text, 16)
        if 0 <= address < 65536:
            item = self.ram_list.item(address)
            self.ram_list.setCurrentItem(item)
            self.ram_list.scrollToItem(item)

    def search_stack(self):
        address_text = self.stack_search.text()
        if not all(c in "0123456789ABCDEF" for c in address_text.upper()) or len(address_text) > 2:
            return

        address = int(address_text, 16)
        if 0 <= address < 256:
            item = self.stack_list.item(address)
            self.stack_list.setCurrentItem(item)
            self.stack_list.scrollToItem(item)

    def populate_ram_list(self):
        """Populate the RAM display list."""
        for address in range(65536):
            item = QListWidgetItem(f"{address:04X}: {self.memory[address]:02X}")
            self.ram_list.addItem(item)

    def populate_stack_list(self):
        """Populate the Stack display list."""
        for address in range(256):
            item = QListWidgetItem(f"{address:02X}: {self.stack[address]:02X}")
            self.stack_list.addItem(item)

    def populate_asm_text(self):
        """Populate the Assembly Code display."""
        # This is a placeholder. Normally, you'd load actual assembly code here.
        example_code = """MOV R1, 0x45
MOV R2, R1
ADD R1, R2
SUB R1, 0x10
JMP 0x0010
"""
        self.asm_text_edit.setPlainText(example_code)

    def step(self):
        """Execute one step of the emulator."""
        # This is a placeholder. Normally, you'd fetch, decode, and execute the next instruction.
        # For now, let's just increment the PC and update the display.
        self.pc += 1
        if self.pc >= 65536:
            self.pc = 0
        self.update_pc(self.pc)
        # You would also update other parts of the emulator state here.

    def open_file(self):
        """Open a file containing assembly code."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Assembly Code File", "", "All Files (*)", options=options)
        if file_name:
            with open(file_name, 'r') as file:
                code = file.read()
                self.asm_text_edit.setPlainText(code)

    def save_file(self):
        """Save the current assembly code to a file."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Assembly Code File", "", "Assembly Files (*.asm);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'w') as file:
                code = self.asm_text_edit.toPlainText()
                file.write(code)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    emulator = Emulator()
    emulator.show()
    sys.exit(app.exec_())
