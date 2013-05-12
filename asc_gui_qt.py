#!/usr/bin/python3
 
import sys
from PyQt4 import Qt, QtCore, QtGui
from qtgui import Ui_MainWindow
import asc
import argparse

#class ASCSyntaxHighlighter(QtGui.QSyntaxHighlighter):
#    def highlightBlock(self, text):
#        # highlight code for ASC syntax
#        myClassFormat = QTextCharFormat()
#        myClassFormat.setFontWeight(QFont.Bold);
#        myClassFormat.setForeground(Qt.darkRed);
#        pass
 
class Window(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        QtCore.QObject.connect(self.ui.actionOpen,
                               QtCore.SIGNAL("triggered()"),
                               self.load_file)
        QtCore.QObject.connect(self.ui.actionNew,
                               QtCore.SIGNAL("triggered()"),
                               self.new_file)
        QtCore.QObject.connect(self.ui.actionSave,
                               QtCore.SIGNAL("triggered()"),
                               self.save_file)
        QtCore.QObject.connect(self.ui.actionSave_As,
                               QtCore.SIGNAL("triggered()"),
                               self.save_as)
        QtCore.QObject.connect(self.ui.actionLoad_ROM,
                               QtCore.SIGNAL("triggered()"),
                               self.load_rom)
        QtCore.QObject.connect(self.ui.actionQuit,
                               QtCore.SIGNAL("triggered()"),
                               quit)
        QtCore.QObject.connect(self.ui.actionDecompile,
                               QtCore.SIGNAL("triggered()"),
                               self.decompile)
        QtCore.QObject.connect(self.ui.actionCompile,
                               QtCore.SIGNAL("triggered()"),
                               self.action_compile)
        QtCore.QObject.connect(self.ui.actionDebug,
                               QtCore.SIGNAL("triggered()"),
                               self.action_debug)
        QtCore.QObject.connect(self.ui.actionCut,
                               QtCore.SIGNAL("triggered()"),
                               self.ui.textEdit.cut)
        QtCore.QObject.connect(self.ui.actionCopy,
                               QtCore.SIGNAL("triggered()"),
                               self.ui.textEdit.copy)
        QtCore.QObject.connect(self.ui.actionPaste,
                               QtCore.SIGNAL("triggered()"),
                               self.ui.textEdit.paste)
        QtCore.QObject.connect(self.ui.actionDelete,
                               QtCore.SIGNAL("triggered()"),
                               self.ui.textEdit.removeSelectedText)
        QtCore.QObject.connect(self.ui.actionUndo,
                               QtCore.SIGNAL("triggered()"),
                               self.ui.textEdit.undo)
        QtCore.QObject.connect(self.ui.actionRedo,
                               QtCore.SIGNAL("triggered()"),
                               self.ui.textEdit.redo)
        QtCore.QObject.connect(self.ui.actionAbout,
                               QtCore.SIGNAL("triggered()"),
                               self.help_about)
        self.rom_file_name = ""
        self.file_name = ""
        # QScintilla
        self.ui.textEdit.setMarginLineNumbers(1, True)
        self.ui.textEdit.setMarginWidth(1, 30)

        #print(dir(self.ui))
        #QtCore.QObject.connect(self.ui.lineEdit, QtCore.SIGNAL("returnPressed()"), self.add_entry)

    def load_file(self):
        fn = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 
                                               QtCore.QDir.homePath(),
                                               "Pokemon script (*.pks);;"
                                               "All files (*.*)")
        if not fn:
            return
        self.file_name = fn

        with open(fn, 'r') as f:        
            text = f.read()
            self.ui.textEdit.setText(text)
        self.ui.statusbar.showMessage("loaded " + fn)

    def new_file(self):
        #TODO: Unsaved changes!
        self.file_name = ''
        self.ui.textEdit.clear()
        self.ui.statusbar.showMessage("")

    def save_as(self):
        fn = QtGui.QFileDialog.getSaveFileName(self, 'Save file',
                                               QtCore.QDir.homePath())
        if fn:
            self.file_name = fn
            self.save_file()

    def save_file(self):
        if not self.file_name:
            fn = QtGui.QFileDialog.getSaveFileName(self, 'Save file',
                                                   QtCore.QDir.homePath())
            if not fn:
                return
        else:
            fn = self.file_name
        with open(fn, 'w') as f:
            f.write(self.ui.textEdit.text())
        self.ui.statusbar.showMessage("file saved as " + fn)

    def load_rom(self):
        fn = QtGui.QFileDialog.getOpenFileName(self, 'Open ROM file', 
                                               QtCore.QDir.homePath(),
                                               "GBA ROM (*.gba);;"
                                               "All files (*)")
        if not fn:
            return
        self.rom_file_name = fn

        #with open(fn, 'rb') as f:        
        #    self.rom_contents = f.read()
        #self.ui.statusbar.showMessage("loaded ROM " + fn)

    def action_compile(self):
        self.compile("compile")

    def action_debug(self):
        self.compile("debug")

    def decompile(self, offset=None):
        if not self.rom_file_name:
            QtGui.QMessageBox.critical(self, "Error", "No ROM loaded")
            return
        if not offset:
            text, ok = QtGui.QInputDialog.getText(self, 'Decompile', 
                                                  'Enter offset (prefix with 0x for hex):')
            if not ok or not text:
                return
            if len(text) > 2 and text[:2] == "0x":
                try:
                    offset = int(text, 16)
                except ValueError:
                    QtGui.QMessageBox.critical(self, "Error", "Invalid offset")
                    return
            else:
                try:
                    offset = int(text)
                except ValueError:
                    QtGui.QMessageBox.critical(self, "Error", "Invalid offset")
                    return
        self.ui.textEdit.setText(asc.decompile(self.rom_file_name, offset))

    def compile(self, mode): # In "compile" mode, writes changes to ROM
                             # In "debug" it doesn't
        if not self.rom_file_name:
            QtGui.QMessageBox.critical(self, "Error", "No ROM loaded")
            return
        #with open(self.rom_file_name, 'rb') as f:
        #    self.rom_contents = f.read()
        script = str(self.ui.textEdit.text())
        script = script.replace("\r\n", "\n")
        script = asc.preparse(script)
        parsed_script, error, dyn = asc.read_text_script(script)
        if error:
            QtGui.QMessageBox.critical(self, "Error", error)
            return
        hex_script, error = asc.compile_script(parsed_script)
        if error:
            QtGui.QMessageBox.critical(self, "Error", error)
            return
        log = ''
        if dyn[0]: # If there are dynamic addresses, we have to replace
                   # them with real adresses and recompile
            #print "going dynamic!"
            script, error, log = asc.put_offsets(hex_script, script,
                                                 self.rom_file_name, dyn[1])
            script = asc.put_offsets_labels(hex_script, script)
            #print script
            #print "re-preparsing"
            parsed_script, error, dyn = asc.read_text_script(script)
            if error:
                self.error_message(error)
                return
            #print "recompiling"
            hex_script, error = asc.compile_script(parsed_script)
            if error:
                QtGui.QMessageBox.critical(self, "Error", error)
                self.error_message(error)
                return
            #print "yay!"
        else:
            script = asc.put_offsets_labels(hex_script, script)
            parsed_script, error, dyn = asc.read_text_script(script)
            if error:
                self.error_message(error)
                return
            hex_script, error = asc.compile_script(parsed_script)
            if error:
                QtGui.QMessageBox.critical(self, "Error", error)
                self.error_message(error)
                return

        if mode == "compile":
            asc.write_hex_script(hex_script, self.rom_file_name)
            QtGui.QMessageBox.information(self, "Done!",
                                          "Script compiled and written "
                                          "successfully")
        else:
            QtGui.QMessageBox.information(self, "Script in hex",
                        str(hex_script))
        if log:
            QtGui.QMessageBox.information(self, "log", log)

    def help_about(self):
        QtGui.QMessageBox.about(self, "About ASC", "Advanced (Pokémon) Script "
                                      "Compiler\n"
                                      "Copyright © 2012 Jaume Delclòs Coll\n"
                                      "(aka cosarara97)")


 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Advanced (Pokémon) Script Compiler')
    parser.add_argument('file', nargs='?')
    parser.add_argument('offset', nargs='?')
    args = parser.parse_args()
    app = QtGui.QApplication(sys.argv)
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
