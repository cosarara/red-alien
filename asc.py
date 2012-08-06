# -*- coding: utf-8 -*-

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

import sys
import pokecommands as pk
import binascii
import text_translate
import bytefy
# TODO: Implantar arg_len al decompilador <-- valid encara?


using_windows = False
using_dynamic = False
end_commands = ["end", "jump", "return"]


def apply_defs(text_script):
    list_script = text_script.split("\n")
    for n, line in enumerate(list_script):
        if "'" in line:
            line = line[:line.find("'") - 1]
        words = line.split(" ")
        if len(words) == 3:
            command = words[0]
            name = words[1]
            value = words[2]
            if command == "#define":
                # Because CAMERA mustn't override CAMERA_START
                text_script = text_script.replace(" " + name + " ",
                                                  " " + value + " ")
                text_script = text_script.replace(" " + name + "\n",
                                                  " " + value + "\n")
    text_script = text_script.replace("#define", "'#define")
    #print text_script
    return text_script


def read_text_script(text_script, end_commands=["end", "jump", "return"]):
    text_script = apply_defs(text_script)
    list_script = text_script.split("\n")
    #org = 0
    org_i = 0
    has_org = False
    parsed_list = []
    for num, line in enumerate(list_script):
        line = line.rstrip(" ")
        if "'" in line:                # Eliminem commentaris
            line = line[:line.find("'")]
            line = line.rstrip(" ")
        if line == "":
            continue
        words = line.split(" ")                 # Separem paraules
        command = words[0]
        args = words[1:]
        if command not in pk.pkcommands:
            error = ("ERROR: command not found in line " + str(num + 1) + ":" +
                     "\n" + str(line))
            return None, error
        if "args" in pk.pkcommands[command]:    # Si la comanda te args
            #print pk.pkcommands[command]["args"]
            arg_num = len(pk.pkcommands[command]["args"][1])
        else:
            arg_num = 0
#        print "args needed by command", command, ":", arg_num
        if len(args) != arg_num and command != '=':
            error = "ERROR: wrong argument number in line " + str(num + 1)
            error += "\nargs given: " + str(len(args))
            if pk.pkcommands[command]['args'] and \
             pk.pkcommands[command]['args'][0]:
                error += "args needed: " + pk.pkcommands[command]['args'][0] \
                    + " " + str(pk.pkcommands[command]['args'][1])
            return None, error
        else:
            #print line
            if command == "#org":
                offset = args
                parsed_list.append(offset)
                has_org = True

            elif command == "#dyn" or command == "#dynamic":
                if len(args) == 1:
                    global using_dynamic
                    using_dynamic = True
                    global dynamic_start_offset
                    dynamic_start_offset = args[0]
                else:
                    error = "ERROR: #dyn/#dynamic statement needs offset"
                    return None, error

            elif has_org is False:
                error = ("ERROR: No #org found - " + str(num))
                #print line
                return None, error

            elif command in end_commands or words == ["#raw", "0xFE"]:
                #print "END"
                parsed_list[org_i].append(words)
                org_i += 1
                has_org = False

            elif command == "=":
                has_org = False
                parsed_list[org_i].append(line)
                org_i += 1

#            elif command == "#raw":
#                parsed_list.append(args)

            elif command == "if":
                if len(args) != 3:
                    error = ("ERROR: syntax error on line " + str(num + 1) +
                           "\nArgument number wrong in 'if'")
                    return None, error
                if args[1] == "jump":
                    branch = "jumpif"
                elif args[1] == "call":
                    branch = "callif"
                elif args[1] == "jumpstd":
                    branch = "jumpstdif"
                elif args[1] == "callstd":
                    branch = "callstdif"
                else:
                    error = ("ERROR: Command in 'if' must be jump, call, "
                             "jumpstd or callstd.")
                    return None, error
                operator = args[0]
                operators = {"==": "1", "!=": "5", "<": "0", ">": "2",
                                "<=": "3", ">=": "4"}
                if operator in operators:
                    operator = operators[operator]
                words = [branch, operator, args[2]]
                parsed_list[org_i].append(words)

            else:
                parsed_list[org_i].append(words)
        if command != "=" and command != "if":
            for i, arg in enumerate(args):
                arg_len = pk.pkcommands[command]["args"][1][i]
                #print "arg_len = " + str(arg_len)
                #print arg
                if arg[:2] == "0x":
                    this_arg_len = len(arg[2:]) / 2
                else:
                    this_arg_len = len(arg) / 2
                if this_arg_len > arg_len and arg[0] != "@":
                    print "We wan't this:", arg_len
                    print "But we have this:", this_arg_len
                    print "and the arg is this: ", arg
                    error = ("ERROR: Arg too long (" + str(arg_len) + ", " +
                             str(this_arg_len) + ") on line " + str(num + 1))
                    return None, error
        #print line
    #print parsed_list
    return parsed_list, None


def compile_script(script_list):
    hex_scripts = []
    for script in script_list:
        hex_script = [script[0], ""]  # hex_script = [offset, ""]
        for line in script[1:]:
            command = line[0]
            args = line[1:]
            if command == '=':
                # The text conversion table in the module
                text_table = text_translate.table
                # encoding table
                e_table = text_translate.read_table_encode(text_table)
                text = unicode(args[1:], "utf-8")
                hex_script[1] = text_translate.ascii_to_hex(text, e_table)
            elif command == '#raw':
                hexcommand = args[0]
#                print hexcommand
                # TODO: acabar això <-- ???
                if hexcommand[0:2] != "0x":
                    #print arg
                    hexcommand = hex(int(hexcommand))  # hex() adds the 0x
                hexcommand = hexcommand[2:]
                hexcommand = bytefy.num_to_bytes(hexcommand)
                hex_script[1] += hexcommand
            else:
                hexcommand = pk.pkcommands[command]["hex"]
                hexargs = ""
                for i, arg in enumerate(args):
                    if arg[0] != "@":
                        arg_len = pk.pkcommands[command]["args"][1][i]
                        #print arg_len
                        if arg[0:2] != "0x":
                            #print arg
                            arg = hex(int(arg))  # hex() adds the 0x
                        arg = arg[2:]
                        arg = bytefy.num_to_bytes(arg)
                        if len(arg) / 2 > arg_len:
                            error = ("Arg too long! "
                                     "We did something wrong preparsing... "
                                     "Arg: " + arg +
                                     "\nCommand: " + command)
                            return None, error
                        if len(arg) / 2 < arg_len:
                            if len(arg) / 2 < 4 and arg_len == 4:
                                arg = "08" + "00" * (arg_len - len(arg)) + arg
                            else:
                                arg = "00" * (arg_len - len(arg) / 2) + arg
#                                print "arg with 00", arg
                        # Si hi ha alguna cosa a afegir davant les comandes
                        arg = bytefy.permutate(arg)
                        if len(pk.pkcommands[command]["args"]) == 3:
                            arg = pk.pkcommands[command]["args"][2] + arg
                        hexargs += arg
                    else:
                        if not using_dynamic:
                            error = "No #dynamic statement"
                            return None, error
                        # If we still have dynamic offsets, this compilation
                        # is just for calculating space,
                        # so we fill this with 00
                        arg = "08000000"
                        arg = bytefy.permutate(arg)
                        hexargs += arg
                hex_script[1] += hexcommand + hexargs
        hex_scripts.append(hex_script)
#    print hex_scripts
    return hex_scripts, None


dynamic_start_offset = "800000"


def put_offsets(hex_script, text_script, file_name):
#    print dynamic_start_offset
    dynamic_start = int(dynamic_start_offset, 16) * 2
    alen = 0
    rom_file_r = open(file_name, "rb")
    rom_text = rom_file_r.read()
    rom_file_r.close()
    rom_text = binascii.hexlify(rom_text).upper()
    for i, script in enumerate(hex_script):
        offset = script[0]
        part = script[1]
        #print offset
        if offset[0] != "@":
            continue
        length = len(part) / 2
#        print length
        free_space = "FF" * (length)
#        if length < 10: print free_space
#        print alen
        offset_with_free_space = (rom_text.find(free_space, dynamic_start)
                                  + (alen * 2))
#        print offset_with_free_space, free_space
        offset_with_free_space = hex(offset_with_free_space / 2)[2:].upper()
        offset_with_free_space = "0x" + offset_with_free_space
#        print offset_with_free_space, free_space
        hex_script[i][0] = offset_with_free_space
#        print length, "in", offset_with_free_space
        text_script = text_script.replace(" " + offset + " ",
                                          " " + offset_with_free_space + " ")
        text_script = text_script.replace(" " + offset + "\n",
                                          " " + offset_with_free_space + "\n")
        alen += length + 10
        print offset, "-", offset_with_free_space
    # TODO: Comprovar si ha quedat alguna direcció (en un argument) dinàmica
    return text_script, None


def write_hex_script(hex_scripts, rom_file_name):
    file_name = rom_file_name
    for script in hex_scripts:
#        rom_file = open_rom()
        rom_file_r = open(file_name, "rb")
        rom_text = rom_file_r.read()
        rom_file_w = open(file_name, "wb")
        offset = script[0]
#        print offset
        hex_script = script[1]
        print "chunk length = " + str(len(hex_script) / 2)
        b_script = binascii.unhexlify(hex_script)
        rom_text_first_part = rom_text[:int(offset, 16)]
#        print binascii.b2a_hex(rom_text_first_part)
        rom_text_final_part = rom_text[int(offset, 16) + len(b_script):]
        new_rom = rom_text_first_part + b_script + rom_text_final_part
#        print binascii.b2a_hex(new_rom)
        rom_file_w.write(new_rom)
        rom_file_r.close()
        rom_file_w.close()


def decompile(file_name, offset, type_="script"):
    # Preparem ROM text
    print "file name = " + file_name
    print "offset = " + offset
    romfile = open(file_name)
    romtext = romfile.read()
    romtext = binascii.hexlify(romtext).upper()
    offsets = [(offset, type_)]
    textscript = ''
    decompiled_offsets = []
    while offsets:
        print offsets[0]
        offset = offsets[0][0]
        if len(offset) == 8 and offset[:2] == "08":
            offset = offset[2:]
        type_ = offsets[0][1]
        if type_ == "script":
            textscript_, offsets_ = decompile_script(romtext, offset, offsets)
            textscript += "#org 0x" + bytefy.bytes_to_num(offset) + "\n" + \
                          textscript_ + "\n"
#            added_offsets = list(set(offsets + offsets_))
            for offset_ in offsets_:
                if (offset_[0][2:] not in decompiled_offsets
                    and offset_ not in offsets):
                    print ("going to add " + str(offset_[0])
                           + " because it's not in "
                           + str(decompiled_offsets))
                    offsets += [offset_]
        if type_ == "text":
            text = decompile_text(romtext, offset)
            textscript += "#org 0x" + bytefy.bytes_to_num(offset) + \
                          "\n= " + text + "\n\n"
        if type_ == "movs":
            print "movs"
            textscript_, offsets_ = decompile_movs(romtext, offset)
            textscript += "#org 0x" + bytefy.bytes_to_num(offset) + "\n" + \
                          textscript_ + "\n"
        del offsets[0]
        decompiled_offsets.append(offset)
        # Removing duplicates doesn't hurt, right?
        decompiled_offsets = list(set(decompiled_offsets))
    print '----'
    print textscript.encode("utf-8")


def decompile_script(romtext, offset, added_offsets,
                     end_hex_commands=["FF"]):
    print "decompiling..."
    # Preparem ROM text
    offsets = []
    print offset
    #hexscript = romtext[int(offset, 16) * 2:]
    hexscript = romtext
    i = int(offset, 16) * 2
    textscript = ""
#        finished = False
    text_command = ""
    hex_command = ""
#    while text_command not in end_commands and \
#    (hex_command in pk.dec_pkcommands or hex_command == ""):
    while (text_command not in end_commands and
           hex_command not in end_hex_commands):
        hex_command = hexscript[i:i + 2]
        if not hex_command:
            break
        print "hex command = " + hex_command
        if hex_command in pk.dec_pkcommands:
            text_command = pk.dec_pkcommands[hex_command]
            print text_command
            textscript += text_command
            i += 2
            command_data = pk.pkcommands[text_command]
            if "args" in pk.pkcommands[text_command]:
                if len(command_data["args"]) == 3:
                    i += 2
                for n, arg_len in enumerate(command_data["args"][1]):
                    # loop tantes vegades com arg's hi ha
                    # afegir cada arg
                    # 2 = el que ocupa la commanda
                    #i += 2
                    arg = hexscript[i:i + arg_len * 2]
                    arg = bytefy.permutate(arg)
                    if "offset" in command_data:
                        if command_data["offset"][0] == n:
                            offset_to_add = arg
                            offset_to_add_type = command_data["offset"][1]
                            tuple_to_add = (offset_to_add, offset_to_add_type)
                            if tuple_to_add not in added_offsets:
                                offsets.append(tuple_to_add)
                    arg = bytefy.bytes_to_num(arg)
                    textscript += " 0x" + arg
                    i += arg_len * 2
                    # i sumar a i (index)
        else:
            print hex_command in pk.dec_pkcommands
            text_command = "#raw"
            textscript += "#raw 0x" + hex_command
            i += 2
        textscript += "\n"
        print ("text_command = " + text_command + ", hex_command = "
               + hex_command)
    print "textscript =", textscript
    return textscript, offsets


def decompile_movs(romtext, offset, end_commands=["end", "jump", "return"],
                   end_hex_commands=["FE", "FF"]):
    print "decompiling..."
    # Preparem ROM text
    print offset
    #hexscript = romtext[int(offset, 16) * 2:]
    hexscript = romtext
    i = int(offset, 16) * 2
    textscript = ""
#        finished = False
    text_command = ""
    hex_command = ""
#    while text_command not in end_commands and \
#    (hex_command in pk.dec_pkcommands or hex_command == ""):
    while text_command not in end_commands and \
                                        hex_command not in end_hex_commands:
        hex_command = hexscript[i:i + 2]
        if hex_command == "":
            break
#        print i, len(hexscript)
        print "hex command = " + hex_command
        text_command = "#raw"
        textscript += "#raw 0x" + hex_command
        i += 2
        textscript += "\n"
        print ("text_command = " + text_command + ", hex_command = "
               + hex_command)
    print "textscript =", textscript
    return textscript, []


def decompile_text(romtext, offset):
    start = int(offset, 16) * 2
    end = start + romtext[start:].find("FF")
    text = romtext[start:end]
    print text, start, end, hex(start / 2), hex(end / 2)
    text_table = text_translate.table
    # decoding table
    d_table = text_translate.read_table_decode(text_table)
    translated_text = text_translate.hex_to_ascii(text, d_table)
    print translated_text.encode("utf-8")
    return translated_text


def write_text_script(text, filename):
    if using_windows:
        text = text.replace("\n", "\r\n")
    pass


def open_script(file_name):
    script_file = open(file_name, "r")
    script_text = script_file.read()
    script_text = script_text.replace("\r\n", "\n")
    return script_text

if len(sys.argv) > 1:
    if sys.argv[1] == "c":
        script = open_script(sys.argv[2])
        #script = open_script("test.pks")
        #print script
        preparsed_script, error = read_text_script(script)
        #print read_text_script("#org 0x80000\nmsgbox @lol\ncallstd 0x2")
        if error:
            print error
            quit()
        hex_script, error = compile_script(preparsed_script)
        if error:
            print error
            quit()
        if using_dynamic:
            print "going dynamic!"
            script, error = put_offsets(hex_script, script, sys.argv[3])
            #print script
            print "re-preparsing"
            preparsed_script, error = read_text_script(script)
            if error:
                print error
                quit()
            print "recompiling"
            hex_script, error = compile_script(preparsed_script)
            if error:
                print error
                quit()
            print "yay!"
        write_hex_script(hex_script, sys.argv[3])

    elif sys.argv[1] == "b":
        script = open_script(sys.argv[2])
        #script = open_script("test.pks")
        #print script
        preparsed_script, error = read_text_script(script)
#        print preparsed_script
        #print read_text_script("#org 0x80000\nmsgbox @lol\ncallstd 0x2")
        if error:
            print error
            quit()
        hex_script, error = compile_script(preparsed_script)
        print hex_script
        if error:
            print error
            quit()
        if using_dynamic:
            print "going dynamic!"
            #print hex_script
            script, error = put_offsets(hex_script, script, sys.argv[3])
            #print script
            print "re-preparsing"
            preparsed_script, error = read_text_script(script)
            if error:
                print error
                quit()
            print "recompiling"
            hex_script, error = compile_script(preparsed_script)
            if error:
                print error
                quit()
            print "yay!"
        print hex_script
        #write_hex_script(hex_script, sys.argv[3])

    elif sys.argv[1] == "d":
        #decompile_script(sys.argv[2], sys.argv[3])
        decompile(sys.argv[2], sys.argv[3])

    else:
        print "ERROR"
