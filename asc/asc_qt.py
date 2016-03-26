#!/usr/bin/python3

""" Red Alien's GUI """

import sys
import argparse
import pkgutil
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import Qsci
from .qtgui import Ui_MainWindow
from . import asc

class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        if getattr(sys, 'frozen', False):
            iconpath = os.path.join(
                os.path.dirname(sys.executable),
                "asc", "data", "icon.svg")
            pixmap = QtGui.QPixmap(iconpath)
        else:
            icon = pkgutil.get_data('asc', os.path.join('data', 'icon.svg'))
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(icon)
        icon = QtGui.QIcon()
        icon.addPixmap(pixmap,
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        # Script mode selector
        self.ui.modeGroup = QtWidgets.QActionGroup(self)
        self.ui.actionModeOW = QtWidgets.QAction("OW Script Mode", self)
        self.ui.actionModeOW.setCheckable(True)
        self.ui.actionModeAI = QtWidgets.QAction("AI Script Mode", self)
        self.ui.actionModeAI.setCheckable(True)
        self.ui.menuSettings.addAction(self.ui.actionModeOW)
        self.ui.menuSettings.addAction(self.ui.actionModeAI)
        self.ui.modeGroup.addAction(self.ui.actionModeOW)
        self.ui.modeGroup.addAction(self.ui.actionModeAI)
        self.ui.actionModeOW.setChecked(True)
        self.mode = "ow"

        cons = ((self.ui.actionOpen, self.load_file),
                (self.ui.actionNew, self.new_file),
                (self.ui.actionSave, self.save_file),
                (self.ui.actionSave_As, self.save_as),
                (self.ui.actionLoad_ROM, self.load_rom),
                (self.ui.actionQuit, self.close),
                (self.ui.actionDecompile, self.decompile),
                (self.ui.actionCompile, self.action_compile),
                (self.ui.actionDebug, self.action_debug),
                (self.ui.actionCut, self.ui.textEdit.cut),
                (self.ui.actionCopy, self.ui.textEdit.copy),
                (self.ui.actionPaste, self.ui.textEdit.paste),
                (self.ui.actionDelete, self.ui.textEdit.removeSelectedText),
                (self.ui.actionUndo, self.ui.textEdit.undo),
                (self.ui.actionRedo, self.ui.textEdit.redo),
                (self.ui.actionFind, self.find),
                (self.ui.actionInsert_String, self.insert_string),
                (self.ui.actionAbout, self.help_about),
                (self.ui.actionModeOW, self.set_mode_ow),
                (self.ui.actionModeAI, self.set_mode_ai))
        for action, function in cons:
            action.triggered.connect(function)

        self.rom_file_name = ""
        self.file_name = ""
        # QScintilla
        self.ui.textEdit.setMarginLineNumbers(1, True)
        self.ui.textEdit.setMarginWidth(1, 30)
        self.font = QtGui.QFont("mono", 10)
        self.ui.textEdit.setFont(self.font)
        lexer = Qsci.QsciLexerCPP()
        lexer.setDefaultFont(self.font)
        self.ui.textEdit.setLexer(lexer)

        self.ui.textEdit.setText(asc.get_canvas())

    def ask_save(self):
        # why would you save the base template amirite?
        if self.ui.textEdit.text() == asc.get_canvas():
            return True
        reply = QtWidgets.QMessageBox.question(self, 'Are you sure?',
                                               "Do you want to save this first?",
                                               QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.save_file()
            return False
        return True

    def load_file(self):
        if not self.ask_save():
            return

        fn, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file',
                                                      QtCore.QDir.homePath(),
                                                      "Pokemon script (*.pks);;"
                                                      "All files (*)")
        if not fn:
            return
        self.file_name = fn

        with open(fn, 'r') as f:
            text = f.read()
            self.ui.textEdit.setText(text)
        self.ui.statusbar.showMessage("loaded " + fn)

    def new_file(self):
        if not self.ask_save():
            return

        self.file_name = ''
        self.ui.textEdit.setText(asc.get_canvas())
        self.ui.statusbar.showMessage("")

    def save_as(self):
        fn, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file',
                                                      QtCore.QDir.homePath(),
                                                      "Pokemon Script (*.pks);;"
                                                      "All files (*)")
        if fn:
            self.file_name = fn
            self.save_file()

    def save_file(self):
        if not self.file_name:
            self.save_as()
        fn = self.file_name
        with open(fn, 'w') as f:
            f.write(self.ui.textEdit.text())
        self.ui.statusbar.showMessage("file saved as " + fn)

    def load_rom(self):
        fn, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open ROM file',
                                                      QtCore.QDir.homePath(),
                                                      "GBA ROM (*.gba);;"
                                                      "All files (*)")
        if not fn:
            return
        self.rom_file_name = fn

    def action_compile(self):
        self.compile("compile")

    def action_debug(self):
        self.compile("debug")

    def decompile(self, offset=None):
        if not self.ask_save():
            return

        if not self.rom_file_name:
            QtWidgets.QMessageBox.critical(self, "Error", "No ROM loaded")
            return

        if self.mode == "ai" and not offset:
            with open(self.rom_file_name, "rb") as f:
                f.seek(0xAC)
                code = f.read(4)
            popup = AIScriptGetAddressPopup(self, self.rom_file_name, code)
            popup.exec_()
            offset = popup.selected

        if not offset:
            text, ok = QtWidgets.QInputDialog.getText(
                self, 'Decompile', 'Enter offset (prefix with 0x for hex):')
            if not ok or not text:
                return
            if len(text) > 2 and text[:2] == "0x":
                try:
                    offset = int(text, 16)
                except ValueError:
                    QtWidgets.QMessageBox.critical(self, "Error", "Invalid offset")
                    return
            else:
                try:
                    offset = int(text)
                except ValueError:
                    QtWidgets.QMessageBox.critical(self, "Error", "Invalid offset")
                    return
        from . import pokecommands as pk
        cmd, dec, end = {
            "ow": (pk.pkcommands, pk.dec_pkcommands, pk.end_pkcommands),
            "ai": (pk.aicommands, pk.dec_aicommands, pk.end_aicommands),
        }[self.mode]
        self.ui.textEdit.setText(asc.decompile(self.rom_file_name, offset,
                                               cmd_table=cmd, dec_table=dec,
                                               end_commands=end))

    def error_message(self, msg):
        QtWidgets.QMessageBox.critical(self, "Error", msg)

    def compile(self, mode): # In "compile" mode, writes changes to ROM
                             # In "debug" it doesn't
        if not self.rom_file_name:
            QtWidgets.QMessageBox.critical(self, "Error", "No ROM loaded")
            return
        #with open(self.rom_file_name, 'rb') as f:
        #    self.rom_contents = f.read()
        script = str(self.ui.textEdit.text())
        script = script.replace("\r\n", "\n")
        include_path = (".", os.path.dirname(self.rom_file_name),
                        os.path.dirname(self.file_name), asc.get_program_dir(),
                        asc.data_path)
        from . import pokecommands as pk
        cmd, dec, end = {
            "ow": (pk.pkcommands, pk.dec_pkcommands, pk.end_pkcommands),
            "ai": (pk.aicommands, pk.dec_aicommands, pk.end_aicommands),
        }[self.mode]
        try:
            cleanlines = asc.compile_script(script,
                                            include_path,
                                            self.file_name or "current_script")
            hex_script, log = asc.assemble(cleanlines,
                                           self.rom_file_name,
                                           include_path,
                                           cmd_table=cmd)
        except Exception as e:
            self.error_message(str(e))
            return

        if mode == "compile":
            asc.write_hex_script(hex_script, self.rom_file_name)
            QtWidgets.QMessageBox.information(
                self, "Done!", "Script compiled and written successfully")
        else:
            LogPopup(self, asc.nice_dbg_output(hex_script))

        if log:
            LogPopup(self, log)

    def help_about(self):
        QtWidgets.QMessageBox.about(self, "About Red Alien",
                                    ("Red Alien,"
                                     "the Advanced Pokémon Script Compiler\n"
                                     "Copyright © 2012-2016 Jaume Delclòs Coll\n"
                                     "(aka cosarara97)"))

    def find(self):
        startline, starti = self.ui.textEdit.getCursorPosition()
        line_n = startline
        s, ok = QtWidgets.QInputDialog.getText(self, 'Find', 'Text to find:')
        if not ok or not s:
            return
        t = self.ui.textEdit.text().split('\n')
        b = 0 # break hack
        for got_to_the_end in (0, 1):
            for line_n, line in enumerate(t):
                if startline > line_n and not got_to_the_end:
                    # Skip lines before cursor
                    continue
                if startline == line_n:
                    if got_to_the_end:
                        break
                    i = line[starti:].find(s)
                    if i != -1:
                        i += starti
                else:
                    i = line.find(s)
                if i != -1:
                    b = 1
                    break
            if b:
                break
        if i == -1:
            QtWidgets.QMessageBox.critical(self, "Error", "Text not found")
            return
        self.ui.textEdit.setCursorPosition(line_n, i+len(s))

    def insert_string(self):
        popup = InsertTextBoxPopup(self)
        popup.exec_()
        line, _ = self.ui.textEdit.getCursorPosition()
        text = self.ui.textEdit.text()
        i = asc.find_nth(text, "\n", line)
        to_insert = "".join(["= " + l + "\n" for l in popup.text.split("\n")])
        self.ui.textEdit.setText(text[:i] + to_insert + text[i:])
        print(popup.text)

    def set_mode_ow(self):
        self.mode = "ow"
        print(self.mode)

    def set_mode_ai(self):
        self.mode = "ai"
        print(self.mode)

class LogPopup(QtWidgets.QDialog):
    def __init__(self, parent=None, text=""):
        QtWidgets.QDialog.__init__(self, parent)

        self.resize(400, 300)

        vbox = QtWidgets.QVBoxLayout()
        self.textedit = QtWidgets.QTextEdit()
        self.textedit.setReadOnly(True)
        self.textedit.setFont(QtGui.QFont("mono", 10))
        self.textedit.setText(text)
        quit_button = QtWidgets.QPushButton("OK")
        quit_button.clicked.connect(self.close)
        vbox.addWidget(self.textedit)
        vbox.addWidget(quit_button)

        self.setLayout(vbox)
        self.show()

class InsertTextBoxPopup(QtWidgets.QDialog):
    def __init__(self, parent=None, text=""):
        QtWidgets.QDialog.__init__(self, parent)

        self.resize(400, 300)

        vbox = QtWidgets.QVBoxLayout()
        self.textedit = Qsci.QsciScintilla(None)
        self.textedit.setFont(QtGui.QFont("mono", 10))
        self.textedit.setEdgeMode(Qsci.QsciScintilla.EdgeLine)
        self.textedit.setEdgeColumn(35)
        self.textedit.setEdgeColor(QtGui.QColor("#FF0000"))
        self.textedit.setText(text)
        self.textedit.cursorPositionChanged.connect(self.curPosChanged)

        quit_button = QtWidgets.QPushButton("OK")
        quit_button.clicked.connect(self.ok)

        self.label = QtWidgets.QLabel()

        vbox.addWidget(self.textedit)
        vbox.addWidget(quit_button)
        vbox.addWidget(self.label)

        self.setLayout(vbox)
        self.text = ""

    def curPosChanged(self, l, _):
        text = self.textedit.text()
        line = text.split("\n")[l]
        out = str(asc.text_len(line)) + "/" + str(35*6) + " px"
        self.label.setText(out)
        return

    def ok(self):
        self.hide()
        self.close()
        self.text = self.textedit.text()
        return

class AIScriptGetAddressPopup(QtWidgets.QDialog):
    def __init__(self, parent, rom_file_name, code):
        QtWidgets.QDialog.__init__(self, parent)

        self.selected = None
        #self.resize(400, 300)

        vbox = QtWidgets.QVBoxLayout()

        ok_button = QtWidgets.QPushButton("OK")
        ok_button.clicked.connect(self.ok)
        nope_button = QtWidgets.QPushButton("I'll write a custom address tyvm")
        nope_button.clicked.connect(self.nope)

        self.addrs = []

        groupBox = QtWidgets.QGroupBox("AI Script")

        if code == b"BPRE":
            with open(rom_file_name, "rb") as f:
                f.seek(0x1D9BF4)
                for _ in range(32):
                    self.addrs.append(int.from_bytes(f.read(4), "little"))
            self.radios = []
            gbox = QtWidgets.QGroupBox()
            r_vbox = QtWidgets.QVBoxLayout()
            for addr in self.addrs:
                radio = QtWidgets.QRadioButton(hex(addr))
                r_vbox.addWidget(radio)
                self.radios.append(radio)

            self.radios[0].setChecked(True)
            gbox.setLayout(r_vbox)
            scroll = QtWidgets.QScrollArea()
            scroll.setWidget(gbox)
            vbox.addWidget(scroll)
            #vbox.addStretch(1);
            vbox.addWidget(ok_button)
        else:
            self.label = QtWidgets.QLabel("Sry, I don't know the list for this ROM")
            vbox.addWidget(self.label)

        vbox.addWidget(nope_button)

        self.setLayout(vbox)

    def ok(self):
        self.hide()
        self.close()
        for i, radio in enumerate(self.radios):
            if radio.isChecked():
                self.selected = self.addrs[i]
                return

    def nope(self):
        self.hide()
        self.close()
        return

def main():
    parser = argparse.ArgumentParser(description='Red Alien, the Advanced Pokémon Script Compiler')
    parser.add_argument('file', nargs='?', help="Either a script or a ROM")
    parser.add_argument('offset', nargs='?', help="Needed if the file is a ROM image")
    args = parser.parse_args()
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.show()
    if args.file and not args.offset: # opening a script
        win.file_name = args.file
        with open(args.file, 'r') as f:
            text = f.read()
        win.ui.textEdit.setText(text)
    elif args.offset:
        win.rom_file_name = args.file
        win.decompile(int(args.offset, 16))
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

