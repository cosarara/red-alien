#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Red Alien.

#    Red Alien is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Red Alien is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Red Alien.  If not, see <http://www.gnu.org/licenses/>.

import sys
import binascii
import argparse
import re
from . import pokecommands as pk
from . import text_translate

max_nops=10
using_windows = False
using_dynamic = False
end_commands = ["end", "jump", "return"]
end_lalmands = 25
end_hex_commands = [0xFF]

operators = {"==": "1", "!=": "5", "<": "0", ">": "2",
             "<=": "3", ">=": "4"}
contrary_operators = {"==": "!=", "!=": "==", "<": ">=", ">": "<=",
                      "<=": ">", ">=": "<"}

quiet = False
def debug(*args):
    print(*args) if not quiet else None

def preparse(text_script):
    text_script = remove_comments(text_script)
    text_script = re.sub("^[ \t]*", "", text_script, flags=re.MULTILINE)
    text_script = apply_defs(text_script)
    text_script = regexps(text_script)
    text_script = advanced_preparsing(text_script)
    return text_script

def regexps(text_script):
    ''' Part of the preparsing '''
    # FIXME: We beak line numbers everywhere :(
    # XSE 1.1.1 like msgboxes
    text_script = re.sub(r"msgbox (.+?) (.+?)", r"msgbox \1\ncallstd \2",
            text_script)
    # Join lines ending with \
    text_script = re.sub("\\\\\\n", r"", text_script)
    return text_script

def remove_comments(text_script):
    comment_symbols = ['//', "'"]
    for symbol in comment_symbols:
        pattern = symbol + "(.*?)$"
        text_script = re.sub(pattern, "", text_script, flags=re.MULTILINE)
    return text_script


def apply_defs(text_script):
    ''' Runs the #define substitutions '''
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
                # Because CAMERA mustn't conflict with CAMERA_START
                text_script = text_script.replace(" " + name + " ",
                                                  " " + value + " ")
                text_script = text_script.replace("(" + name + " ",
                                                  "(" + value + " ")
                text_script = text_script.replace(" " + name + ")",
                                                  " " + value + ")")
                text_script = text_script.replace(" " + name + "\n",
                                                  " " + value + "\n")
                if name[0] == '[' and name [-1] == ']':
                    text_script = text_script.replace(name, value)
    text_script = text_script.replace("#define", "'#define")
    return text_script

def advanced_preparsing(text_script, level=0):
    ''' The awesome preparsing (actually you could call it compiling)
        of cool stuctures '''
    # Okay, so this is what we want:
    # 1. ----------- while -----------
    # while (<expression>) {
    #   <command>
    #   . . .
    # }
    #
    # 2. ----------- if/else -----------
    # if (<expression>) {
    #   <command>
    #   . . .
    # } [else {
    #   <command>
    #   . . .
    # }]
    #
    # 3. ----------- expressions -----------
    # (<var num> <operator> <literal num>)
    # or
    # (<flag num>)
    # TODO: better names for these functions
    def grep_part(text, start_pos, open, close):
        start_pos = start_pos + text[start_pos:].find(open) + 1
        s = -1
        for i, char in enumerate(text[start_pos:]):
            if char == close:
                s += 1
            elif char == open:
                s -= 1
            if s == 0:
                break
        else:
            raise Exception("No matching " + close + " found")
        end_pos = start_pos + i
        return start_pos, end_pos

    def grep_statement(text, name):
        pos = re.search(name + ".?\(", text).start()
        condition_start, condition_end = grep_part(text, pos, "(", ")")
        condition = text[condition_start:condition_end]
        body_start, body_end = grep_part(text, pos, "{", "}")
        body = text[body_start:body_end]
        return (pos, body_end+1, condition, body)


    while re.search("while.?\(", text_script):
        pos, end_pos, condition, body = grep_statement(text_script, "while")
        body = advanced_preparsing(body, level+1)
        # Any operator in the condition expression
        part = ":while_start" + str(level) + '\n'
        for operator in operators:
            if operator in condition:
                var, constant = condition.split(operator)
                part += "compare " + var.strip() + " " + constant.strip() + "\n"
                part += ("if " + contrary_operators[operator] +
                         " jump :while_end" + str(level) + '\n')
                break
        else:
            # We are checking a flag
            if condition[0] == "!":
                flag = condition[1:]
                operator = "=="
            else:
                flag = condition
                operator = "!="
            part += "checkflag " + flag + "\n"
            part += "if " + operator + " jump :while_end" + str(level) + '\n'
        part += body + '\n'
        part += "jump :while_start" + str(level) + "\n"
        part += ":while_end" + str(level) + "\n"
        text_script = text_script[:pos] + part + text_script[end_pos:]
        level += 1

    # I'll refactor this one day, I promise =P
    while re.search("if.?\(", text_script):
        pos, end_pos, condition, body = grep_statement(text_script, "if")
        body = advanced_preparsing(body)
        have_else = re.match("\\selse\\s*?{", text_script[end_pos:])
        # Any operator in the condition expression
        part = ''
        for operator in operators:
            if operator in condition:
                var, constant = condition.split(operator)
                part += "compare " + var.strip() + " " + constant.strip() + "\n"
                part += ("if " + contrary_operators[operator] +
                         " jump :if_end" + str(level) + '\n')
                break
        else:
            # We are checking a flag
            if condition[0] == "!":
                flag = condition[1:]
                operator = "=="
            else:
                flag = condition
                operator = "!="
            part += "checkflag " + flag + "\n"
            part += "if " + operator + " jump :if_end" + str(level)
        part += body + '\n'
        if have_else:
            else_body_start, else_body_end = grep_part(text_script,
                    end_pos, "{", "}")
            else_body = text_script[else_body_start:else_body_end]
            else_body = advanced_preparsing(else_body, level+1)
            part += "jump :else_end" + str(level) + "\n"
            part += ":if_end" + str(level) + "\n"
            part += else_body + '\n' + ':else_end' + str(level) + '\n'
            end_pos = else_body_end + 1

        else:
            part += ":if_end" + str(level)
        text_script = text_script[:pos] + part + text_script[end_pos:]
        debug(text_script)
        level += 1

    return text_script

def read_text_script(text_script, end_commands=["end", "softend"]):
    ''' The basic language preparsing function '''
    list_script = text_script.split("\n")
    org_i = -1
    has_org = False
    dyn = (False, 0)
    parsed_list = []

    for num, line in enumerate(list_script):
        line = line.rstrip(" ")
        # TODO: deprecated (done in preparsing)
        if "'" in line:                # Eliminem commentaris
            line = line[:line.find("'")]
            line = line.rstrip(" ")
        if line == "":
            continue
        if line[0] == ":": # Labels for goto's
            parsed_list[org_i].append([line])
            continue

        words = line.split()
        command = words[0]
        args = words[1:]

        if command not in pk.pkcommands:
            error = ("ERROR: command not found in line " + str(num+1) + ":" +
                     "\n" + str(line))
            return None, error, dyn
        if "args" in pk.pkcommands[command]:    # if command has args
            arg_num = len(pk.pkcommands[command]["args"][1])
        else:
            arg_num = 0

        if len(args) != arg_num and command != '=':
            error = "ERROR: wrong argument number in line " + str(num+1) + '\n'
            error += line + '\n'
            error += str(args) + '\n'
            error += "Args given: " + str(len(args)) + '\n'
            if (pk.pkcommands[command]['args'] and
                pk.pkcommands[command]['args'][0]):
                error += ("Args needed: " + pk.pkcommands[command]['args'][0]
                          + " " + str(pk.pkcommands[command]['args'][1]))
            return None, error, dyn

        else:
            if command == "#org":
                org_i += 1
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
                debug(command)
                error = ("ERROR: No #org found - " + str(num))
                return None, error, dyn

            elif command in end_commands or words == ["#raw", "0xFE"]:
                parsed_list[org_i].append(words)
                has_org = False

            elif command == "=":
                has_org = False
                parsed_list[org_i].append(line)

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
                if arg[:2] == "0x":
                    this_arg_len = len(arg[2:]) // 2
                else:
                    this_arg_len = len(arg) // 2
                if this_arg_len > arg_len:
                    debug("We wan't this:", arg_len)
                    debug("But we have this:", this_arg_len)
                    debug("and the arg is this: ", arg)
                    error = ("ERROR: Arg too long (" + str(arg_len) + ", " +
                             str(this_arg_len) + ") on line " + str(num + 1))
                    return None, error, dyn
    return parsed_list, None, dyn

def autocut_text(text):
    words = text.split(" ")
    text = ''
    line = ''
    i = 0
    delims = ('\\n', '\\p')
    delim = 0
    while i < len(words):
        while i < len(words) and len(line+words[i]) < 35:
            line += words[i] + " "
            i += 1
        text += line.rstrip(" ") + delims[delim]
        delim = not delim
        line = ''
    text = text.rstrip('\\p').rstrip('\\n').rstrip(" ")
    return text

def compile_script(script_list):
    ''' Compile parsed script list '''
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
                text = autocut_text(text)
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
                        if arg[0:2] != "0x":
                            arg = (int(arg) & 0xffffff)
                        else:
                            arg = int(arg, 16)
                        if ("offset" in pk.pkcommands[command] and
                                pk.pkcommands[command]["offset"][0] == i):
                            arg |= 0x8000000
                        try:
                            arg_bytes = arg.to_bytes(arg_len, "little")
                        except OverflowError:
                            debug(script)
                            debug(line)
                            error = ("Arg too long! "
                                     "We did something wrong preparsing... "
                                     "Arg: " + hex(arg) +
                                     "\nCommand: " + command)
                            return None, error
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
                        if len(pk.pkcommands[command]["args"]) == 3:
                            arg = (pk.pkcommands[command]["args"][2] + arg)
                        hexargs += arg
                hex_script[1] += hexcommand.to_bytes(1, "little") + hexargs
        hex_scripts.append(hex_script)
    return hex_scripts, None


dynamic_start_offset = "800000"

def put_offsets_labels(hex_chunks, text_script):
    ''' Calculates the real offset for :labels and does the needed
        searches and replacements. '''
    for i, chunk in enumerate(hex_chunks):
        for label in chunk[2]:
            debug(label)
            name = label[0]
            pos = hex(int(chunk[0], 16) + label[1])
            debug(pos)
            text_script = text_script.replace(" " + name + " ",
                                              " " + pos + " ")
            text_script = text_script.replace(" " + name + "\n",
                                              " " + pos + "\n")
            text_script = text_script.replace("\n" + name + "\n", "\n")
            text_script = text_script.replace("\n" + name + " ", "\n")
    return text_script


def put_offsets(hex_chunks, text_script, file_name, dyn):
    ''' Find free space and replace #dynamic addresses with real offsets '''
    dynamic_start = int(dyn, 16)
    alen = 0
    rom_file_r = open(file_name, "rb")
    rom_bytes = rom_file_r.read()
    rom_file_r.close()
    offsets_found_log = ''
    for i, chunk in enumerate(hex_chunks):
        debug(chunk)
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
            raise Exception("No free space to put script.")
        text_script = text_script.replace(" " + offset + " ",
                                      " " + hex(offset_with_free_space) + " ")
        text_script = text_script.replace(" " + offset + "\n",
                                      " " + hex(offset_with_free_space) + "\n")
        hex_chunks[i][0] = hex(offset_with_free_space)
        alen += length + 10
        offsets_found_log += (offset + ' - ' +
                              hex(offset_with_free_space) + '\n')
    # TODO: Comprovar si ha quedat alguna direcció (en un argument) dinàmica
    #       (No hauria)
    return text_script, None, offsets_found_log


def write_hex_script(hex_scripts, rom_file_name):
    ''' Write every chunk of bytes onto the big ROM file '''
    file_name = rom_file_name
    for script in hex_scripts:
        with open(file_name, "rb") as f:
            rom_bytes = f.read()
        rom_ba = bytearray(rom_bytes)
        offset = int(script[0], 16)
        offset = get_rom_offset(offset)
        hex_script = script[1]
        debug("chunk length = " + hex(len(hex_script)))
        rom_ba[offset:offset+len(hex_script)] = hex_script

        with open(file_name, "wb") as f:
            f.write(rom_ba)


def decompile(file_name, offset, type_="script", raw=False,
        end_commands=end_commands, end_hex_commands=end_hex_commands):
    # Preparem ROM text
    debug("'file name = " + file_name)
    debug("'offset = " + hex(offset))
    debug("'---\n")
    with open(file_name, "rb") as f:
        rombytes = f.read()
    offsets = [[offset, type_]]
    textscript = ''
    decompiled_offsets = []
    while offsets:
        offset = offsets[0][0]
        rom_offset = get_rom_offset(offset)
        type_ = offsets[0][1]
        if type_ == "script":
            textscript_, new_offsets = decompile_script(
                                            rombytes, offset,
                                            offsets, end_commands=end_commands,
                                            end_hex_commands=end_hex_commands,
                                            raw=raw)
            textscript += ("#org " + hex(offset) + "\n" +
                           textscript_ + "\n")
            for new_offset in new_offsets:
                new_offset[0] &= 0xffffff
                if (new_offset not in offsets and
                        new_offset[0] not in decompiled_offsets):
                    offsets += [new_offset]
        if type_ == "text":
            text = decompile_text(rombytes, offset, raw=raw)
            textscript += ("#org " + hex(offset) +
                           "\n= " + text + "\n\n")
        if type_ == "movs":
            textscript_, offsets_ = decompile_movs(rombytes, offset, raw=raw)
            textscript += ("#org " + hex(offset) + "\n" +
                           textscript_ + "\n")
        del offsets[0]
        decompiled_offsets.append(offset)
        # Removing duplicates doesn't hurt, right?
        decompiled_offsets = list(set(decompiled_offsets))
    return textscript


def get_rom_offset(offset):
    rom_offset = offset
    if rom_offset >= 0x8000000:
        rom_offset -= 0x8000000
    return rom_offset

def decompile_script(rombytes, offset, added_offsets,
                     end_commands=["end", "jump", "return"],
                     end_hex_commands=[0xFF], raw=False):
    rom_offset = get_rom_offset(offset)
    offsets = []
    hexscript = rombytes
    i = rom_offset
    textscript = ""
    text_command = ""
    hex_command = 0
    hex_command = hexscript[i]
    nop_count = 0 # Stop on 10 nops for safety
    while (text_command not in end_commands and
           hex_command not in end_hex_commands):
        hex_command = hexscript[i]
        if hex_command in pk.dec_pkcommands and not raw:
            text_command = pk.dec_pkcommands[hex_command]
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
                    arg = hexscript[i:i + arg_len]
                    arg = int.from_bytes(arg, "little")
                    if "offset" in command_data:
                        if command_data["offset"][0] == n:
                            offset_to_add = arg
                            offset_to_add_type = command_data["offset"][1]
                            # lol, a list
                            tuple_to_add = [offset_to_add, offset_to_add_type]
                            if tuple_to_add not in added_offsets:
                                offsets.append(tuple_to_add)
                    textscript += " " + hex(arg)
                    i += arg_len
                    # i sumar a i (index)
        else:
            text_command = "#raw"
            textscript += "#raw " + hex(hex_command)
            i += 1
        if hex_command == 0:
            nop_count += 1
            if nop_count >= max_nops and max_nops != 0:
                textscript += " ' Too many nops. Stopping"
                break
        else:
            nop_count = 0
        textscript += "\n"
    return textscript, offsets


def decompile_movs(romtext, offset, end_hex_commands=[0xFE, 0xFF], raw=False):
    rom_offset = get_rom_offset(offset)
    debug(offset)
    hexscript = romtext
    i = rom_offset
    textscript = ""
    text_command = ""
    hex_command = ""
    while (hex_command not in end_hex_commands):
        try:
            hex_command = hexscript[i]
        except IndexError:
            break
        text_command = "#raw"
        textscript += "#raw " + hex(hex_command)
        i += 1
        textscript += "\n"
    return textscript, []


def decompile_text(romtext, offset, raw=False):
    rom_offset = get_rom_offset(offset)
    start = rom_offset
    end = start + romtext[start:].find(b"\xff")
    text = romtext[start:end]
    text_table = text_translate.table
    # decoding table
    d_table = text_translate.read_table_decode(text_table)
    translated_text = text_translate.hex_to_ascii(text, d_table)
    return translated_text


def write_text_script(text, file_name):
    if using_windows:
        text = text.replace("\n", "\r\n")
    with open(file_name, "w") as script_file:
        script_file.write(text)


def open_script(file_name):
    ''' Open file and replace \\r\\n with \\n '''
    with open(file_name, "r") as script_file:
        script_text = script_file.read()
    script_text = script_text.replace("\r\n", "\n")
    return script_text

def compile_without_writing(script, rom_file_name):
    ''' Compiles a plain script and returns a tuple containing
        a list and a string. The string is the #dyn log.
        The list contains a list for every location where
        something should be written. These lists are 2
        elements each, the offset where data should be
        written and the data itself '''
    debug("preparsing...")
    script = preparse(script)
    debug(script)
    debug("parsing...")
    parsed_script, error, dyn = read_text_script(script)
    debug(parsed_script)
    if error:
        raise Exception(error)
    debug("compiling...")
    hex_script, error = compile_script(parsed_script)
    debug(hex_script)
    if error:
        raise Exception(error)
    log = ''
    debug("doing dynamic and label things...")
    if dyn[0] and rom_file_name:
        debug("going dynamic!")
        debug("replacing dyn addresses by offsets...")
        script, error, log = put_offsets(hex_script, script,
                                         rom_file_name, dyn[1])
        debug(script)
        debug("re-preparsing")
        script = put_offsets_labels(hex_script, script)
        debug(script)

        parsed_script, error, dyn = read_text_script(script)
        if error:
            raise Exception(error)
        debug("recompiling")
        hex_script, error = compile_script(parsed_script)
        if error:
            raise Exception(error)
        debug("yay!")
    else:
        script = put_offsets_labels(hex_script, script)
        parsed_script, error, dyn = read_text_script(script)
        hex_script, error = compile_script(parsed_script)

    # Remove the labels list, which will be empty and useless now 
    for chunk in hex_script:
        del chunk[2] # Will always be []
    return hex_script, log

def nice_dbg_output(hex_scripts):
    text = ''
    for offset, hex_script in hex_scripts:
        script_text = offset + '\n'
        line = ''
        for byte in hex_script:
            line += '%02x ' % byte
            if len(line) > 40:
                script_text += line + '\n'
                line = ''
        script_text += line
        script_text += '\n'
        text += script_text
    return text


def main():
    parser = argparse.ArgumentParser(description='Red Alien, an Advanced (Pokémon) Script'
            ' Compiler')

    parser.add_argument('--quiet', action='store_true', help='Be quiet')
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
    parser_d.add_argument('--raw', action='store_true',
            help='Be dumb (display everything as raw bytes)')
    parser_d.add_argument('--max-nops', default=10, type=int,
            help=('How many nop bytes until it stops (0 to never stop). '
                'Defaults to 10'))
    global end_commands
    for end_command in end_commands:
        msg = ('whether or not to stop decompiling when a ' + end_command +
               ' is found')
        parser_d.add_argument('--continue-on-' + end_command,
                action='append_const', dest='end_commands_to_delete',
                const=end_command, help=msg)
    parser_d.add_argument('--continue-on-0xFF',
            action='store_true', help=('whether or not to stop decompiling'
                ' when a 0xFF byte is found'))
    parser_d.set_defaults(command='d')

    args = parser.parse_args()
    if not "command" in args:
        raise Exception("Error. Run with --help for more info.")

    global quiet, max_nops
    quiet = args.quiet
    max_nops = (args.max_nops if max_nops in args else 10)

    if args.command == "c":
        script = open_script(args.script)
        print("reading file...")
        script = open_script(args.script)
        print(script)
        hex_script, log = compile_without_writing(script, args.rom)
        write_hex_script(hex_script, args.rom)
        print(log)

    elif args.command == "b":
        print("reading file...")
        script = open_script(args.script)
        print(script)
        hex_script, log = compile_without_writing(script, args.rom)
        print(hex_script)
        print(log)

    elif args.command == "d":
        if not args.end_commands_to_delete:
            args.end_commands_to_delete = []
        for end_command in args.end_commands_to_delete:
            end_commands.remove(end_command)
        print("'" + '-'*20 + '\n' +
              decompile(args.rom, int(args.offset, 16),
                        end_commands=end_commands, raw=args.raw,
                        end_hex_commands=(
                            [] if args.continue_on_0xFF else end_hex_commands
                            )
                        )
              )




if __name__ == "__main__":
    main()


