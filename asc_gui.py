# -*- coding: utf-8 *-*

#This file is part of ASC.

#    ASC is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    ASC is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with ASC.  If not, see <http://www.gnu.org/licenses/>.

VERSION = "git version"
GPLv3 = "GPLv3"
try:
    with open("GPL.txt", "r") as gplfile:
        GPLv3 = gplfile.read()
except IOError as e:
    GPLv3 = ("GPL.txt not found - you can find it at "
            "http://www.gnu.org/licenses/gpl.txt")

import asc
from gi.repository import Gtk, GtkSource, GObject, Gdk
import os


class scriptTextEditor:

    def __init__(self):
        self.filename = None
        self.rom_filename = None
        builder = Gtk.Builder()
        GObject.type_register(GtkSource.View)
        builder.add_from_file("gui.glade")

        self.window = builder.get_object("window")
        self.editor = builder.get_object("editor")
        self.statusbar = builder.get_object("statusbar")
        builder.connect_signals(self)

        self.statusbar_cid = self.statusbar.get_context_id("")
        self.reset_default_status()

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

#        self.editor.set_highlight_current_line(True)

        self.language_manager = GtkSource.LanguageManager.get_default()
        self.language_manager.set_search_path(["./", "./styles/"])
        #print self.language_manager.get_language_ids()
        language = self.language_manager.get_language("pks")
        buff = GtkSource.Buffer()
        buff.set_language(language)

        self.editor.set_buffer(buff)

        menu_item_find = builder.get_object("menu_item_find")
        menu_item_far = builder.get_object("menu_item_far")
        menu_item_find.set_sensitive(False)
        menu_item_far.set_sensitive(False)

    def get_buffer_text(self, buffer_):
        iter_start = buffer_.get_start_iter()
        iter_end = buffer_.get_end_iter()
        text = buffer_.get_text(iter_start, iter_end, 0)
        return text

    def get_open_filename(self, file_type="script"):
        filename = None
        chooser = Gtk.FileChooserDialog("Open File...", self.window,
                                        Gtk.FileChooserAction.OPEN,
                                        (Gtk.STOCK_CANCEL,
                                        Gtk.ResponseType.CANCEL,
                                         Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        if file_type == "script":
            filter_pks = Gtk.FileFilter()
            filter_pks.set_name("Pokemon script")
            filter_pks.add_pattern("*.pks")
            chooser.add_filter(filter_pks)

        if file_type == "rom":
            filter_gba = Gtk.FileFilter()
            filter_gba.set_name("GBA ROM Image")
            filter_gba.add_pattern("*.gba")
            chooser.add_filter(filter_gba)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        chooser.add_filter(filter_any)

        response = chooser.run()
        if response == Gtk.ResponseType.OK:
            filename = chooser.get_filename()
        chooser.destroy()

        return filename

    def error_message(self, message):
        # log to terminal window
        print message
        # create an error message dialog and display modally to the user
#        dialog = Gtk.MessageDialog(None,
#                Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
#                Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, message)
#        dialog.run()
#        dialog.destroy()

        dialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.ERROR,
            Gtk.ButtonsType.CANCEL, "ERROR!")
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def info_message(self, title, message):
        print message
        dialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK, title)
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def get_save_filename(self):
        filename = None
        chooser = Gtk.FileChooserDialog("Save File...", self.window,
                                        Gtk.FileChooserAction.SAVE,
                                        (Gtk.STOCK_CANCEL,
                                        Gtk.ResponseType.CANCEL,
                                         Gtk.STOCK_SAVE,
                                         Gtk.ResponseType.OK))

        response = chooser.run()
        if response == Gtk.ResponseType.OK:
            filename = chooser.get_filename()
        chooser.destroy()

        return filename

    def load_file(self, filename):
        # add Loading message to status bar and ensure GUI is current
        self.statusbar.push(self.statusbar_cid, "Loading %s" % filename)
        while Gtk.events_pending():
            Gtk.main_iteration()

        try:
            # get the file contents
            fin = open(filename, "r")
            text = fin.read()
            fin.close()

            # disable the text view while loading the buffer with the text
            self.editor.set_sensitive(False)
            buff = self.editor.get_buffer()
            buff.set_text(text)
            buff.set_modified(False)
            self.editor.set_sensitive(True)

            # now we can set the current filename since loading was a success
            self.filename = filename

        except:
            # error loading file, show message to user
            self.error_message("Could not open file: %s" % filename)

        # clear loading status and restore default
        self.statusbar.pop(self.statusbar_cid)
        self.reset_default_status()

    def write_file(self, filename):
        # add Saving message to status bar and ensure GUI is current
        if filename:
            self.statusbar.push(self.statusbar_cid, "Saving %s" % filename)
        else:
            self.statusbar.push(self.statusbar_cid,
                "Saving %s" % self.filename)

        while Gtk.events_pending():
            Gtk.main_iteration()

        try:
            # disable text view while getting contents of buffer
            buff = self.editor.get_buffer()
            self.editor.set_sensitive(False)
            text = self.get_buffer_text(buff)
            self.editor.set_sensitive(True)
            buff.set_modified(False)

            # set the contents of the file to the text from the buffer
            if filename:
                fout = open(filename, "w")
            else:
                fout = open(self.filename, "w")
            fout.write(text)
            fout.close()

            if filename:
                self.filename = filename

        except:
            # error writing file, show message to user
            self.error_message("Could not save file: %s" % filename)

        # clear saving status and restore default
        self.statusbar.pop(self.statusbar_cid)
        self.reset_default_status()

    def check_for_save(self):
        ret = False
        buff = self.editor.get_buffer()
        if buff.get_modified():
            # we need to prompt for save
            message = "Do you want to save the changes you have made?"
            dialog = Gtk.MessageDialog(self.window,
                Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO,
                message)
            dialog.set_title("Save?")
            if dialog.run() == Gtk.ResponseType.NO:
                ret = False
            else:
                ret = True
            dialog.destroy()
        return ret

    def reset_default_status(self):
        if self.filename:
            status = "File: %s" % os.path.basename(self.filename)
        else:
            status = "File: (UNTITLED)"
        self.statusbar.pop(self.statusbar_cid)
        self.statusbar.push(self.statusbar_cid, status)

    def onDeleteWindow(self, widget, data=None):
        Gtk.main_quit()

    def onFileNew(self, widget, data=None):
        if self.check_for_save():
            self.onFileSave(None, None)
        # clear editor for a new file
        buff = self.editor.get_buffer()
        buff.set_text("")
        buff.set_modified(False)
        self.filename = None
        self.reset_default_status()

    def onFileOpen(self, widget):
        if self.check_for_save():
            self.onFileSave(None, None)
        filename = self.get_open_filename()
        if filename:
            self.load_file(filename)

    def onFileSave(self, widget, data=None):
        if self.filename is None:
            filename = self.get_save_filename()
            if filename:
                self.write_file(filename)
        else:
            self.write_file(None)

    def onFileSaveAs(self, widget):
        filename = self.get_save_filename()
        if filename:
            self.write_file(filename)

    def onFileLoadRom(self, widget):
        self.rom_filename = self.get_open_filename("rom")

    def onEditCut(self, widget):
        print "aaa"
        buff = self.editor.get_buffer()
        buff.cut_clipboard(self.clipboard, True)

    def onEditCopy(self, widget):
        buff = self.editor.get_buffer()
        buff.copy_clipboard(self.clipboard)

    def onEditPaste(self, widget):
        buff = self.editor.get_buffer()
        buff.paste_clipboard(self.clipboard, None, True)

    def onEditDelete(self, widget):
        buff = self.editor.get_buffer()
        buff.delete_selection(False, True)

    def onEditUndo(self, widget):
        buff = self.editor.get_buffer()
        buff.do_undo(buff)

    def onEditRedo(self, widget):
        buff = self.editor.get_buffer()
        buff.do_redo(buff)

    def onROMDecompile(self, widget):
        # TODO: Save changes?
        if not self.rom_filename:
            self.error_message("ERROR: No ROM loaded!")
            return
        get_offset_dialog = getOffsetDialog(self.window)
#        box = get_offset_dialog.get_content_area()
#        box.Orientation = Gtk.Orientation.HORIZONTAL
#        box.Orientation = Gtk.Orientation.VERTICAL
#        button1 = Gtk.Button()
#        button2 = Gtk.Button()
#        box.add(button1)
#        box.add(button2)
        get_offset_dialog.show_all()
        response = get_offset_dialog.run()
        if response == Gtk.ResponseType.OK:
            #print "The OK button was clicked"
            decompile_type = get_offset_dialog.selected
            decompile_offset = get_offset_dialog.entry.get_text()
#        elif response == Gtk.ResponseType.CANCEL:
#            #print "The Cancel button was clicked"
#            pass
        else:
            get_offset_dialog.destroy()
            return
        get_offset_dialog.destroy()

        decompiled_script = asc.decompile(self.rom_filename, decompile_offset,
                                          decompile_type)
        self.editor.set_sensitive(False)
        buff = self.editor.get_buffer()
        buff.set_text(decompiled_script)
        buff.set_modified(False)
        self.editor.set_sensitive(True)

    def compile_script(self, mode="compile"):
        if not self.rom_filename:
            self.error_message("ERROR: No ROM loaded!")
            return
        buff = self.editor.get_buffer()
        self.editor.set_sensitive(False)
        text = self.get_buffer_text(buff)
        self.editor.set_sensitive(True)
        script = text.replace("\r\n", "\n")
        preparsed_script, error, dyn = asc.read_text_script(script)
        if error:
            self.error_message(error)
            return
        print preparsed_script
        hex_script, error = asc.compile_script(preparsed_script)
        if error:
            self.error_message(error)
            return
        print hex_script
        log = ''
        if dyn[0]:
            print "going dynamic!"
            script, error, log = asc.put_offsets(hex_script, script,
                                        self.rom_filename, dyn[1])
            #print script
            print "re-preparsing"
            preparsed_script, error, dyn = asc.read_text_script(script)
            if error:
                self.error_message(error)
                return
            print "recompiling"
            hex_script, error = asc.compile_script(preparsed_script)
            if error:
                self.error_message(error)
                return
            print "yay!"

        if mode == "compile":
            asc.write_hex_script(hex_script, self.rom_filename)
        else:
            #self.info_message("Script in hex", str(hex_script))
            hex_script_log = TextPopup(self.window, "Script in hex",
                                       str(hex_script))
            hex_script_log.show_all()
            hex_script_log.run()
            hex_script_log.destroy()

        if log:
            #self.info_message("#dyn log", log)
            info = TextPopup(self.window, "log", log)
            info.show_all()
            info.run()
            info.destroy()

        if mode == "compile":
            self.info_message("Done!", "Script compiled and written "
                              "successfully")
        else:
            self.info_message("Done!", "No problems :)")

    def onROMCompile(self, widget):
        self.compile_script()

    def onROMDebug(self, widget):
        self.compile_script("debug")

    def onHelpAbout(self, widget):
        dialog = Gtk.AboutDialog() #self.window, 0, Gtk.MessageType.INFO,
                                   #Gtk.ButtonsType.OK, title)
        #print dir(dialog)
        dialog.set_program_name("Advanced Script Compiler")
        dialog.set_version(VERSION)
        dialog.set_license(GPLv3)
        dialog.set_copyright("Jaume Delclòs Coll (cosarara97) - "
                             "cosa.rara97@gmail.com")
        dialog.set_comments("ASC is a script compiler and decompiler for"
                            " the script system found in GBA pokemon games.\n"
                            "The language it uses is a mix between the one in"
                            " XSE and the one in PKSV (it is intended to be"
                            " compatible with both), and is constantly"
                            " growing.")
        dialog.run()
        dialog.destroy()

    def onEditFind(self, widget):
        pass

    def onEditFindAndReplace(self, widget):
        pass


class TextPopup(Gtk.Dialog):

    def __init__(self, parent, title, content):
        Gtk.Dialog.__init__(self, title, parent, 0,
                           (Gtk.STOCK_OK, Gtk.ResponseType.OK))
        mainbox = self.get_content_area()
        view = Gtk.TextView()
        view.set_editable(False)
        buff = view.get_buffer()
        buff.set_text(content)
        mainbox.add(view)


class getOffsetDialog(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Script to decomplile", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))
        mainbox = self.get_content_area()
        self.entry = Gtk.Entry()
        label_offset = Gtk.Label("Offset: ")

        hbox = Gtk.Box()
        hbox.orientation = Gtk.Orientation.HORIZONTAL
        hbox.pack_start(label_offset, True, False, 0)
        hbox.pack_start(self.entry, True, False, 0)

        self.selected = "script"
        hbox_radios = Gtk.Box()

        button1 = Gtk.RadioButton.new_with_label_from_widget(None, "Script")
        button1.connect("toggled", self.on_button_toggled, "script")
        hbox_radios.pack_start(button1, False, False, 0)

        button2 = Gtk.RadioButton.new_with_mnemonic_from_widget(button1,
                                                                "Text")
        button2.connect("toggled", self.on_button_toggled, "text")
        hbox_radios.pack_start(button2, False, False, 0)

#        button3 = Gtk.RadioButton.new_with_mnemonic_from_widget(button1,
#                                                                 "B_utton 3")
#        button3.connect("toggled", self.on_button_toggled, "3")
#        hbox_radios.pack_start(button3, False, False, 0)

        mainbox.orientation = Gtk.Orientation.VERTICAL
        mainbox.pack_start(hbox, True, False, 0)
        mainbox.pack_end(hbox_radios, True, False, 0)
        #self.set_modal(True)
        #self.button = Gtk.Button(label="Click Here")

    def on_button_toggled(self, button, name):
        if button.get_active():
            self.selected = name
            print "Button", name, "was turned selected"


if __name__ == "__main__":
    editor = scriptTextEditor()
    editor.window.show()
    Gtk.main()
