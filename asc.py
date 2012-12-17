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

#import sys
import pokecommands as pk
import binascii
import text_translate
import argparse
#import bytefy

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

# Here we'll make the compiler really advanced :)
def advanced_preparsing(text_script):
    return text_script

# The basic language pre-parser
def read_text_script(text_script, end_commands=["end", "return"]):
    text_script = apply_defs(text_script)
    text_script = advanced_preparsing(text_script)
    list_script = text_script.split("\n")
    #org = 0
    org_i = 0
    has_org = False
    dyn = (False, 0)
    parsed_list = []

    for num, line in enumerate(list_script):
        line = line.rstrip(" ")
        if "'" in line:                # Eliminem commentaris
            line = line[:line.find("'")]
            line = line.rstrip(" ")
        if line == "":
            continue
        if line[0] == ":": # Labels for goto's
            #label_list.append(line, parsed_list[0]) 
            parsed_list[org_i].append([line])
            continue

        words = line.split(" ")
        command = words[0]
        args = words[1:]

        if command not in pk.pkcommands:
            error = ("ERROR: command not found in line " + str(num + 1) + ":" +
                     "\n" + str(line))
            return None, error, dyn
        if "args" in pk.pkcommands[command]:    # if command has args
            arg_num = len(pk.pkcommands[command]["args"][1])
        else:
            arg_num = 0

        if len(args) != arg_num and command != '=':
            error = "ERROR: wrong argument number in line " + str(num + 1)
            error += "\nargs given: " + str(len(args))
            if (pk.pkcommands[command]['args'] and
                pk.pkcommands[command]['args'][0]):
                error += ("args needed: " + pk.pkcommands[command]['args'][0]
                          + " " + str(pk.pkcommands[command]['args'][1]))
            return None, error, dyn

        else:
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
                    dyn = (True, args[0])
                else:
                    error = "ERROR: #dyn/#dynamic statement needs offset"
                    return None, error, dyn

            elif has_org is False:
                print(command)
                error = ("ERROR: No #org found - " + str(num))
                #print line
                return None, error, dyn

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
                    return None, error, dyn
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
                    return None, error, dyn
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
                if arg[0] in (":", "@"):
                    continue
                arg_len = pk.pkcommands[command]["args"][1][i]
                #print "arg_len = " + str(arg_len)
                #print arg
                if arg[:2] == "0x":
                    this_arg_len = len(arg[2:]) // 2
                else:
                    this_arg_len = len(arg) // 2
                if this_arg_len > arg_len:
                    print("We wan't this:", arg_len)
                    print("But we have this:", this_arg_len)
                    print("and the arg is this: ", arg)
                    error = ("ERROR: Arg too long (" + str(arg_len) + ", " +
                             str(this_arg_len) + ") on line " + str(num + 1))
                    return None, error, dyn
        #print line
    #print parsed_list
    return parsed_list, None, dyn


def compile_script(script_list):
    hex_scripts = []
    for script in script_list:
        hex_script = [script[0], b"", []]  # hex_script = [offset, "bytes",
                                           #               [labels]]
        for line in script[1:]:
            command = line[0]
            args = line[1:]
            if command == '=':
                # The text conversion table in the module
                text_table = text_translate.table
                # encoding table
                e_table = text_translate.read_table_encode(text_table)
                text = args[1:]
                hex_script[1] = text_translate.ascii_to_hex(text, e_table)
            elif command == '#raw':
                hexcommand = args[0]
                hex_script[1] += int(hexcommand, 16).to_bytes(1, "little")
            elif command[0] == ":":
                hex_script[2].append([command, len(hex_script[1])])
            else:
                hexcommand = pk.pkcommands[command]["hex"]
                hexargs = bytearray()
                for i, arg in enumerate(args):
                    if arg[0] != "@" and arg[0] != ":":
                        arg_len = pk.pkcommands[command]["args"][1][i]
                        #print arg_len
                        if arg[0:2] != "0x":
                            #print arg
                            arg = (int(arg) & 0xffffff)
                        else:
                            arg = (int(arg, 16) & 0xffffff)
                        if ("offset" in pk.pkcommands[command] and
                            pk.pkcommands[command]["offset"][0] == i):
                            arg |= 0x8000000
                        #if len(arg.to_bytes("little")) // 2 > arg_len:
                        try:
                            arg_bytes = arg.to_bytes(arg_len, "little")
                        except OverflowError:
                            print(script)
                            print(line)
                            error = ("Arg too long! "
                                     "We did something wrong preparsing... "
                                     "Arg: " + hex(arg) +
                                     "\nCommand: " + command)
                            return None, error
                        #if len(arg) // 2 < arg_len:
                        #    if len(arg) // 2 < 4 and arg_len == 4:
                        #        arg = (b"\x08" + b"\x00" *
                        #               (arg_len - len(arg)) + arg
                        #    else:
                        #        arg = b"\x00" * (arg_len - len(arg) // 2) + arg
#                                print "arg with 00", arg
                        # Si hi ha alguna cosa a afegir davant les comandes
                        #arg = bytefy.permutate(arg)
                        if len(pk.pkcommands[command]["args"]) == 3:
                            arg_bytes = (pk.pkcommands[command]["args"][2] +
                                         arg_bytes)
                        hexargs += arg_bytes
                    else:
                        if arg[0] == "@" and not using_dynamic:
                            error = "No #dynamic statement"
                            return None, error
                        # If we still have dynamic offsets, this compilation
                        # is just for calculating space,
                        # so we fill this with 00
                        arg = b"\x00\x00\x00\x08" # Dummy bytes, so we can
                                                  # size and then replace
                        hexargs += arg
                hex_script[1] += hexcommand.to_bytes(1, "little") + hexargs
        hex_scripts.append(hex_script)
#    print hex_scripts
    return hex_scripts, None


dynamic_start_offset = "800000"

def put_offsets_labels(hex_chunks, text_script):
    for i, chunk in enumerate(hex_chunks):
        for label in chunk[2]:
            #print(label)
            name = label[0]
            pos = hex(int(chunk[0], 16) + label[1])
            text_script = text_script.replace(" " + name + " ",
                                              " " + pos + " ")
            text_script = text_script.replace(" " + name + "\n",
                                              " " + pos + "\n")
            text_script = text_script.replace("\n" + name + "\n", "\n")
            text_script = text_script.replace("\n" + name + " ", "\n")
    return text_script


def put_offsets(hex_chunks, text_script, file_name, dyn):
#    print dynamic_start_offset
    #dynamic_start = int(dynamic_start_offset, 16) * 2
    dynamic_start = int(dyn, 16)
    alen = 0
    rom_file_r = open(file_name, "rb")
    rom_bytes = rom_file_r.read()
    rom_file_r.close()
    #rom_text = binascii.hexlify(rom_text).upper()
    offsets_found_log = ''
    for i, chunk in enumerate(hex_chunks):
        offset = chunk[0]
        part = chunk[1] # The hex chunk we have to put somewhere
        labels = chunk[2]
        if offset[0] != "@":
            continue
        length = len(part)
        free_space = b"\xFF" * length
        offset_with_free_space = rom_bytes.find(free_space,
                                                dynamic_start + alen)
        if offset_with_free_space == -1:
            print(len(rom_bytes))
            print(len(free_space))
            print(dynamic_start)
            print(alen)
            print("No free space to put script.")
            exit(1)
        #hex_script[i][0] = offset_with_free_space
        text_script = text_script.replace(" " + offset + " ",
                                          " " + hex(offset_with_free_space) + " ")
        text_script = text_script.replace(" " + offset + "\n",
                                          " " + hex(offset_with_free_space) + "\n")
        alen += length + 10
        offsets_found_log += (offset + ' - ' +
                              hex(offset_with_free_space) + '\n')
        for label in labels:
            offset = offset_with_
        #print(offset, "-", offset_with_free_space)
    # TODO: Comprovar si ha quedat alguna direcció (en un argument) dinàmica
    return text_script, None, offsets_found_log


def write_hex_script(hex_scripts, rom_file_name):
    file_name = rom_file_name
    for script in hex_scripts:
        with open(file_name, "rb") as f:
            rom_bytes = f.read()
        rom_ba = bytearray(rom_bytes)
        offset = int(script[0], 16)
        hex_script = script[1]
        print("chunk length = " + hex(len(hex_script)))
        rom_ba[offset:offset+len(hex_script)] = hex_script

        with open(file_name, "wb") as f:
            f.write(rom_ba)


        #rom_file_r = open(file_name, "rb")
        #rom_text = rom_file_r.read()
        #rom_file_w = open(file_name, "wb")
        #offset = script[0]
#       # print offset
        #hex_script = script[1]
        #print("chunk length = " + str(len(hex_script) // 2))
        #b_script = binascii.unhexlify(hex_script)
        #rom_text_first_part = rom_text[:int(offset, 16)]
#       # print binascii.b2a_hex(rom_text_first_part)
        #rom_text_final_part = rom_text[int(offset, 16) + len(b_script):]
        #new_rom = rom_text_first_part + b_script + rom_text_final_part
#       # print binascii.b2a_hex(new_rom)
        #rom_file_w.write(new_rom)
        #rom_file_r.close()
        #rom_file_w.close()


def decompile(file_name, offset, type_="script", info=False):
    # Preparem ROM text
    print("'file name = " + file_name)
    print("'offset = " + hex(offset))
    with open(file_name, "rb") as f:
        rombytes = f.read()
    offsets = [(offset, type_)]
    textscript = ''
    decompiled_offsets = []
    while offsets:
        print(offsets[0])
        offset = offsets[0][0] & 0xffffff
        #if len(hex(offset)[2:]) == 8 and offset[:2] == "08":
        #    offset = offset[2:]
        type_ = offsets[0][1]
        if type_ == "script":
            textscript_, offsets_ = decompile_script(rombytes, offset, offsets)
            textscript += ("#org " + hex(offset) + "\n" +
                           textscript_ + "\n")
#            added_offsets = list(set(offsets + offsets_))
            for offset_ in offsets_:
                if (offset_[0] & 0xffffff not in decompiled_offsets
                    and offset_ not in offsets):
                    offsets += [offset_]
#                    print ("going to add " + str(offset_[0])
#                           + " because it's not in "
#                           + str(decompiled_offsets))
        if type_ == "text":
            text = decompile_text(rombytes, offset)
            textscript += ("#org " + hex(offset) +
                           "\n= " + text + "\n\n")
        if type_ == "movs":
            print("movs")
            textscript_, offsets_ = decompile_movs(rombytes, offset)
            textscript += ("#org " + hex(offset) + "\n" +
                           textscript_ + "\n")
        del offsets[0]
        decompiled_offsets.append(offset)
        # Removing duplicates doesn't hurt, right?
        decompiled_offsets = list(set(decompiled_offsets))
    print('----')
    #print(textscript)
    return textscript


def decompile_script(rombytes, offset, added_offsets,
                     end_hex_commands=[0xFF], info=False):
    print("decompiling...")
    offset &= 0xffffff
    # Preparem ROM text
    offsets = []
    print(offset)
    #hexscript = romtext[int(offset, 16) * 2:]
    hexscript = rombytes
    i = offset
    textscript = ""
#        finished = False
    text_command = ""
    hex_command = 0
#    while text_command not in end_commands and \
#    (hex_command in pk.dec_pkcommands or hex_command == ""):
    try:
        hex_command = hexscript[i]
    except IndexError:
        return textscript, offsets
    while (text_command not in end_commands and
           hex_command not in end_hex_commands):
        try:
            hex_command = hexscript[i]
        except IndexError:
            break
        #if not hex_command:
        #    break
        print("hex command = " + hex(hex_command))
        if hex_command in pk.dec_pkcommands:
            text_command = pk.dec_pkcommands[hex_command]
            print(text_command)
            textscript += text_command
            i += 1
            command_data = pk.pkcommands[text_command]
            if "args" in pk.pkcommands[text_command]:
                if len(command_data["args"]) == 3:
                    i += len(command_data["args"][2])
                for n, arg_len in enumerate(command_data["args"][1]):
                    # loop tantes vegades com arg's hi ha
                    # afegir cada arg
                    # 2 = el que ocupa la commanda
                    #i += 2
                    arg = hexscript[i:i + arg_len]
                    #arg = bytefy.permutate(arg)
                    arg = int.from_bytes(arg, "little")
                    if "offset" in command_data:
                        if command_data["offset"][0] == n:
                            offset_to_add = arg
                            offset_to_add_type = command_data["offset"][1]
                            tuple_to_add = (offset_to_add, offset_to_add_type)
                            if tuple_to_add not in added_offsets:
                                offsets.append(tuple_to_add)
                    #arg = bytefy.bytes_to_num(arg)
                    textscript += " " + hex(arg)
                    i += arg_len
                    # i sumar a i (index)
        else:
            #print(hex_command in pk.dec_pkcommands)
            text_command = "#raw"
            textscript += "#raw " + hex(hex_command)
            i += 1
        textscript += "\n"
        print("text_command = " + text_command + ", hex_command = "
               + hex(hex_command))
    #print("textscript =", textscript)
    return textscript, offsets


def decompile_movs(romtext, offset, end_commands=["end", "jump", "return"],
                   end_hex_commands=[0xFE, 0xFF]):
    print("decompiling...")
    # Preparem ROM text
    print(offset)
    #hexscript = romtext[int(offset, 16) * 2:]
    hexscript = romtext
    i = offset
    textscript = ""
#        finished = False
    text_command = ""
    hex_command = ""
#    while text_command not in end_commands and \
#    (hex_command in pk.dec_pkcommands or hex_command == ""):
    while (text_command not in end_commands and
           hex_command not in end_hex_commands):
        try:
            hex_command = hexscript[i]
        except IndexError:
            break
#        print i, len(hexscript)
        print("hex command = " + hex(hex_command))
        text_command = "#raw"
        textscript += "#raw " + hex(hex_command)
        i += 1
        textscript += "\n"
        print("text_command = " + text_command + ", hex_command = "
               + hex(hex_command))
    print("textscript =", textscript)
    return textscript, []


def decompile_text(romtext, offset):
    start = offset
    end = start + romtext[start:].find(b"\xff")
    text = romtext[start:end]
    print(text, start, end, hex(start), hex(end))
    text_table = text_translate.table
    # decoding table
    d_table = text_translate.read_table_decode(text_table)
    translated_text = text_translate.hex_to_ascii(text, d_table)
    print(translated_text)
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

def main():
    parser = argparse.ArgumentParser(description='Advanced (Pokémon) Script Compiler')

    subparsers = parser.add_subparsers(help='available commands:')
    parser_c = subparsers.add_parser('c', help='compile')
    parser_c.add_argument('rom', help='path to ROM image')
    parser_c.add_argument('script', help='path to pokemon script')
    parser_c.set_defaults(command='c')
    parser_b = subparsers.add_parser('b', help='debug')
    parser_b.add_argument('rom', help='path to ROM image')
    parser_b.add_argument('script', help='path to pokemon script')
    parser_b.set_defaults(command='b')
    parser_d = subparsers.add_parser('d', help='decompile')
    parser_d.add_argument('rom', help='path to ROM image')
    parser_d.add_argument('offset', help='where to decompile')
    parser_d.set_defaults(command='d')

    args = parser.parse_args()
    if not "command" in args:
        print("Error. Run with --help for more info.")
        quit()

    if args.command == "c":
        script = open_script(args.script)
        #script = open_script("test.pks")
        #print script
        preparsed_script, error, dyn = read_text_script(script)
        #print read_text_script("#org 0x80000\nmsgbox @lol\ncallstd 0x2")
        if error:
            print(error)
            quit()
        hex_script, error = compile_script(preparsed_script)
        if error:
            print(error)
            quit()
        #if using_dynamic:
        log = ''
        if dyn[0]:
            print("going dynamic!")
            script, error, log = put_offsets(hex_script, script,
                                             args.rom, dyn[1])
            #print script
            script = put_offsets_labels(hex_script, script)
            print("re-preparsing")
            preparsed_script, error, dyn = read_text_script(script)
            if error:
                print(error)
                quit()
            print("recompiling")
            hex_script, error = compile_script(preparsed_script)
            if error:
                print(error)
                quit()
            print("yay!")
        else:
            #print(script)
            script = put_offsets_labels(hex_script, script)
            #print('---')
            #print(script)
            preparsed_script, error, dyn = read_text_script(script)
            hex_script, error = compile_script(preparsed_script)
        write_hex_script(hex_script, args.rom)
        print(log)

    elif args.command == "b":
        script = open_script(args.script)
        #script = open_script("test.pks")
        #print script
        preparsed_script, error, dyn = read_text_script(script)
        #print(preparsed_script)
        #print read_text_script("#org 0x80000\nmsgbox @lol\ncallstd 0x2")
        if error:
            print(error)
            quit()
        hex_script, error = compile_script(preparsed_script)
        #print(hex_script)
        if error:
            print(error)
            quit()
#        if using_dynamic:
        log = ''
        if dyn[0]:
            print("going dynamic!")
            #print hex_script
            script, error, log = put_offsets(hex_script, script,
                                             args.rom, dyn[1])
            print("re-preparsing")
            script = put_offsets_labels(hex_script, script)
            preparsed_script, error, dyn = read_text_script(script)
            if error:
                print(error)
                quit()
            print("recompiling")
            hex_script, error = compile_script(preparsed_script)
            if error:
                print(error)
                quit()
            print("yay!")
        else:
            script = put_offsets_labels(hex_script, script)
            #print(script)
            preparsed_script, error, dyn = read_text_script(script)
            hex_script, error = compile_script(preparsed_script)
        print(hex_script)
        print(log)

    elif args.command == "d":
        print(decompile(args.rom, int(args.offset, 16)))




if __name__ == "__main__":
    main()


