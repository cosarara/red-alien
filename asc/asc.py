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

''' Main compiler/decompiler module '''

import sys
import os
import binascii
import argparse
import re
import ast
from . import pokecommands as pk
from . import text_translate
from pprint import pprint

MAX_NOPS = 10
USING_WINDOWS = (os.name == 'nt')
USING_DYNAMIC = False
END_COMMANDS = ["end", "jump", "return"]
END_HEX_COMMANDS = [0xFF]

OPERATORS_LIST = ("==", "!=", "<=", ">=", "<", ">")

OPERATORS = {"==": "1", "!=": "5", "<": "0", ">": "2",
             "<=": "3", ">=": "4"}
OPPOSITE_OPERATORS = {"==": "!=", "!=": "==", "<": ">=", ">": "<=",
                      "<=": ">", ">=": "<"}

QUIET = False
VERBOSE = 0
def debug(*args):
    if not QUIET:
        print(*args)

def vdebug(*args):
    if VERBOSE:
        print(*args)

def pdebug(*args):
    if not QUIET:
        pprint(*args)

def vpdebug(*args):
    if VERBOSE:
        pprint(*args)

def hprint(bytes):
    def pad(s):
        return "0" + s if len(s) == 1 else s

    for b in bytes:
        print(pad(hex(b)[2:]), end=" ")
    print("")

def phdebug(bytes):
    if not QUIET:
        hprint(bytes)

def dirty_compile(text_script):
    text_script = remove_comments(text_script)
    text_script = re.sub("^[ \t]*", "", text_script, flags=re.MULTILINE)
    text_script = apply_includes(text_script)
    text_script = apply_defs(text_script)
    text_script = regexps(text_script)
    text_script = compile_clike_blocks(text_script)
    return text_script

def regexps(text_script):
    ''' Part of the preparsing '''
    # FIXME: We beak line numbers everywhere :(
    # XSE 1.1.1 like msgboxes
    text_script = re.sub(r"msgbox (.+?) (.+?)", r"msgbox \1\ncallstd \2",
                         text_script)
    text_script = text_script.replace("goto", "jump")

    # Join lines ending with \
    text_script = re.sub("\\\\\\n", r"", text_script)
    for label in re.findall(r"@\S+", text_script, re.MULTILINE):
        if not "#org "+label in text_script:
            raise Exception("ERROR: Unmatched @ label %s" % label)
    return text_script

def remove_comments(text_script):
    comment_symbols = ['//', "'"]
    for symbol in comment_symbols:
        pattern = symbol + "(.*?)$"
        text_script = re.sub(pattern, "", text_script, flags=re.MULTILINE)
    return text_script

def apply_includes(text_script):
    list_script = text_script.split("\n")
    for n, line in enumerate(list_script):
        if "'" in line:
            line = line[:line.find("'") - 1]
        words = line.split(" ")
        if len(words) == 2:
            command = words[0]
            name = words[1]
            if command == "#include":
                name = ast.literal_eval(name)
                with open(name) as f:
                    t = f.read()
                text_script = t + text_script
    return text_script

def apply_defs(text_script):
    ''' Runs the #define substitutions '''
    list_script = text_script.split("\n")
    for line in list_script:
        if "'" in line:
            line = line[:line.find("'") - 1]
        words = line.split(" ")
        if len(words) >= 3:
            command = words[0]
            name = words[1]
            value = ' '.join(words[2:])
            if command == "#define":
                # Because CAMERA mustn't conflict with CAMERA_START
                for i, j in ((" ", " "), ("(", " "), (" ", ")"), (" ", "\n"),
                          ("\n", "\n")):
                    text_script = text_script.replace(i + name + j, i + value + j)

                if name[0] == '[' and name[-1] == ']':
                    text_script = text_script.replace(name, value)
    text_script = text_script.replace("#define", "'#define")
    text_script = text_script.replace("#include", "'#include")
    return text_script

def compile_clike_blocks(text_script, level=0):
    ''' The awesome preparsing (actually you could call it compiling)
        of cool stuctures '''
    # FIXME: this is crap really

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
        i = 0
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
        pos = re.search(name + r".?\(", text).start()
        condition_start, condition_end = grep_part(text, pos, "(", ")")
        condition = text[condition_start:condition_end]
        body_start, body_end = grep_part(text, pos, "{", "}")
        body = text[body_start:body_end]
        return (pos, body_end+1, condition, body)


    while re.search(r"while.?\(", text_script):
        pos, end_pos, condition, body = grep_statement(text_script, "while")
        body = compile_clike_blocks(body, level+1)
        # Any operator in the condition expression
        part = ":while_start" + str(level) + '\n'
        for operator in OPERATORS_LIST:
            if operator in condition:
                var, constant = condition.split(operator)
                part += "compare " + var.strip() + " " + constant.strip() + "\n"
                part += ("if " + OPPOSITE_OPERATORS[operator] +
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
        part += body
        part += "\njump :while_start" + str(level)
        part += "\n:while_end" + str(level) + "\n"
        # hack
        if text_script[pos] == "\n":
            pos -= 1
        if text_script[end_pos] == "\n":
            end_pos += 1
        text_script = text_script[:pos] + part + text_script[end_pos:]
        level += 1

    # I'll refactor this one day, I promise =P
    while re.search(r"if.?\(", text_script):
        pos, end_pos, condition, body = grep_statement(text_script, "if")
        body = compile_clike_blocks(body)
        have_else = re.match("\\selse\\s*?{", text_script[end_pos:])
        # Any operator in the condition expression
        part = ''
        for operator in OPERATORS_LIST:
            if operator in condition:
                var, constant = condition.split(operator)
                part += "compare " + var.strip() + " " + constant.strip() + "\n"
                part += ("if " + OPPOSITE_OPERATORS[operator] +
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
            part += "if " + operator + " jump :if_end" + str(level) + "\n"
        part += body
        if have_else:
            else_body_start, else_body_end = grep_part(text_script,
                                                       end_pos, "{", "}")
            else_body = text_script[else_body_start:else_body_end]
            else_body = compile_clike_blocks(else_body, level+1)
            part += "\njump :else_end" + str(level) + "\n"
            part += ":if_end" + str(level) + "\n"
            part += else_body + '\n:else_end' + str(level) + '\n'
            end_pos = else_body_end + 1

        else:
            part += "\n:if_end" + str(level)
        text_script = text_script[:pos] + part + text_script[end_pos:]
        #debug(text_script)
        level += 1

    text_script = text_script.strip("\n")
    return text_script

def asm_parse(text_script, END_COMMANDS=["end", "softend"]):
    ''' The basic language preparsing function '''
    list_script = text_script.split("\n")
    org_i = -1
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
            error += "Context:\n"
            for line_num in range(num-3, num+6):
                error += "    " + list_script[line_num] + "\n"
            args = pk.pkcommands[command]['args']
            if args and args[0]:
                error += "Args needed: " + args[0] + " " + str(args[1])
            return None, error, dyn

        else:
            if command == "#org":
                org_i += 1
                offset = args
                parsed_list.append(offset)

            elif command == "#dyn" or command == "#dynamic":
                if len(args) == 1:
                    global USING_DYNAMIC
                    USING_DYNAMIC = True
                    dyn = (True, args[0])
                else:
                    error = "ERROR: #dyn/#dynamic statement needs an address argument"
                    return None, error, dyn

            elif org_i == -1:
                debug(command)
                error = ("ERROR: No #org found on line " + str(num))
                return None, error, dyn

            elif command in END_COMMANDS or words == ["#raw", "0xFE"]:
                parsed_list[org_i].append(words)

            elif command == "=":
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
                if operator in OPERATORS:
                    operator = OPERATORS[operator]
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

def make_bytecode(script_list):
    ''' Compile parsed script list '''
    hex_scripts = []
    for script in script_list:
        addr = script[0]
        bytecode = b""
        labels = []

        for line in script[1:]:
            command = line[0]
            args = line[1:]
            if command == '=':
                text = args[1:]
                bytecode += text_translate.ascii_to_hex(text)
            elif command == '#raw':
                hexcommand = args[0]
                bytecode += int(hexcommand, 16).to_bytes(1, "little")
            elif command[0] == ":":
                labels.append([command, len(bytecode)])
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
                        if arg[0] == "@" and not USING_DYNAMIC:
                            error = "No #dynamic statement"
                            return None, error
                        # If we still have dynamic addresses, this compilation
                        # is just for calculating space,
                        # so we fill this with 00
                        arg = b"\x00\x00\x00\x08" # Dummy bytes, so we can
                                                  # size and then replace
                        if len(pk.pkcommands[command]["args"]) == 3:
                            arg = (pk.pkcommands[command]["args"][2] + arg)
                        hexargs += arg
                bytecode += hexcommand.to_bytes(1, "little") + hexargs

        hex_script = [addr, bytecode, labels]
        hex_scripts.append(hex_script)
    return hex_scripts, None


def put_addresses_labels(hex_chunks, text_script):
    ''' Calculates the real address for :labels and does the needed
        searches and replacements. '''
    for i, chunk in enumerate(hex_chunks):
        for label in chunk[2]:
            vdebug(label)
            name = label[0]
            pos = hex(int(chunk[0], 16) + label[1])
            vdebug(pos)
            text_script = text_script.replace(" " + name + " ",
                                              " " + pos + " ")
            text_script = text_script.replace(" " + name + "\n",
                                              " " + pos + "\n")
            text_script = text_script.replace("\n" + name + "\n", "\n")
            text_script = text_script.replace("\n" + name + " ", "\n")
    return text_script


def put_addresses(hex_chunks, text_script, file_name, dyn):
    ''' Find free space and replace #dynamic @labels with real addresses '''
    dynamic_start = int(dyn, 16)
    rom_file_r = open(file_name, "rb")
    rom_bytes = rom_file_r.read()
    rom_file_r.close()
    offsets_found_log = ''
    last = dynamic_start
    for i, chunk in enumerate(hex_chunks):
        vdebug(chunk)
        offset = chunk[0]
        part = chunk[1] # The hex chunk we have to put somewhere
        labels = chunk[2]
        if offset[0] != "@":
            continue
        length = len(part) + 2
        free_space = b"\xFF" * length
        address_with_free_space = rom_bytes.find(free_space,
                                                last)
        # It's always good to leave some margin around things.
        # If there is free space at the address the user has given us,
        # though, it's ok to use it without margin.
        if address_with_free_space != dynamic_start:
            address_with_free_space += 2
        if address_with_free_space == -1:
            print(len(rom_bytes))
            print(len(free_space))
            print(dynamic_start)
            print(last)
            raise Exception("No free space to put script.")
        text_script = text_script.replace(" " + offset + " ",
                                          " " + hex(address_with_free_space) + " ")
        text_script = text_script.replace(" " + offset + "\n",
                                          " " + hex(address_with_free_space) + "\n")
        hex_chunks[i][0] = hex(address_with_free_space)
        last = address_with_free_space + length + 10
        offsets_found_log += (offset + ' - ' +
                              hex(address_with_free_space) + '\n')
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
        vdebug("chunk length = " + hex(len(hex_script)))
        rom_ba[offset:offset+len(hex_script)] = hex_script

        with open(file_name, "wb") as f:
            f.write(rom_ba)


def decompile(file_name, offset, type_="script", raw=False,
              end_commands=END_COMMANDS, end_hex_commands=END_HEX_COMMANDS):
    # Preparem ROM text
    debug("'file name = " + file_name)
    debug("'address = " + hex(offset))
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
            textscript_, new_offsets = demake_bytecode(rombytes, offset,
                                                        offsets,
                                                        end_commands=end_commands,
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
            lines = [text[i:i+80] for i in range(0, len(text), 80)]
            text = "".join([("= " + line + "\n") for line in lines])
            textscript += ("#org " + hex(offset) + "\n" + text)
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

def demake_bytecode(rombytes, offset, added_offsets,
                     end_commands=END_COMMANDS,
                     end_hex_commands=END_HEX_COMMANDS, raw=False):
    rom_offset = get_rom_offset(offset)
    offsets = []
    hexscript = rombytes
    i = rom_offset
    textscript = ""
    text_command = ""
    hex_command = 0
    hex_command = hexscript[i]
    nop_count = 0 # Stop on 10 nops for safety
    while (text_command not in END_COMMANDS and
           hex_command not in END_HEX_COMMANDS):
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
            if nop_count >= MAX_NOPS and MAX_NOPS != 0:
                textscript += " ' Too many nops. Stopping"
                break
        else:
            nop_count = 0
        textscript += "\n"
    return textscript, offsets


def decompile_movs(romtext, offset, END_HEX_COMMANDS=[0xFE, 0xFF], raw=False):
    rom_offset = get_rom_offset(offset)
    vdebug(offset)
    hexscript = romtext
    i = rom_offset
    textscript = ""
    text_command = ""
    hex_command = ""
    while hex_command not in END_HEX_COMMANDS:
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
    text_table = text_translate.table_str
    # decoding table
    d_table = text_translate.read_table_decode(text_table)
    translated_text = text_translate.hex_to_ascii(text, d_table)
    return translated_text


def write_text_script(text, file_name):
    if USING_WINDOWS:
        text = text.replace("\n", "\r\n")
    with open(file_name, "w") as script_file:
        script_file.write(text)


def open_script(file_name):
    ''' Open file and replace \\r\\n with \\n '''
    with open(file_name, "r") as script_file:
        script_text = script_file.read()
    script_text = script_text.replace("\r\n", "\n")
    return script_text

def assemble(script, rom_file_name):
    ''' Compiles a plain script and returns a tuple containing
        a list and a string. The string is the #dyn log.
        The list contains a list for every location where
        something should be written. These lists are 2
        elements each, the offset where data should be
        written and the data itself '''
    debug("parsing...")
    parsed_script, error, dyn = asm_parse(script)
    vpdebug(parsed_script)
    if error:
        raise Exception(error)
    debug("compiling...")
    hex_script, error = make_bytecode(parsed_script)
    debug(hex_script)
    if error:
        raise Exception(error)
    log = ''
    debug("doing dynamic and label things...")

    if dyn[0] and rom_file_name:
        debug("going dynamic!")
        debug("replacing dyn addresses by offsets...")
        script, error, log = put_addresses(hex_script, script,
                                         rom_file_name, dyn[1])
        vdebug(script)

    # Now with :labels we have to recompile even if 

    debug("re-preparsing")

    script = put_addresses_labels(hex_script, script)
    vdebug(script)

    parsed_script, error, dyn = asm_parse(script)
    if error:
        raise Exception(error)
    debug("recompiling")
    hex_script, error = make_bytecode(parsed_script)
    if error:
        raise Exception(error)
    debug("yay!")

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
    description = 'Red Alien, an Advanced (Pokémon) Script Compiler'
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('--quiet', action='store_true', help='Be quiet')
    parser.add_argument('--verbose', '-v', action='count', help='Be verbose. Like, a lot')
    subparsers = parser.add_subparsers(help='available commands:')

    parser_c = subparsers.add_parser('c', help='compile')
    parser_c.add_argument('rom', help='path to ROM image')
    parser_c.add_argument('script', help='path to pokemon script')
    parser_c.set_defaults(command='c')

    parser_b = subparsers.add_parser('b', help='debug')
    parser_b.add_argument('rom', help='path to ROM image')
    parser_b.add_argument('script', help='path to pokemon script')
    parser_b.add_argument('--compile-only', action='store_true',
                          help='Compile only, don\'t parse the ASM')
    parser_b.add_argument('--parse-only', action='store_true',
                          help='Parse only, don\'t assemble')
    parser_b.set_defaults(command='b')

    parser_d = subparsers.add_parser('d', help='decompile')
    parser_d.add_argument('rom', help='path to ROM image')
    parser_d.add_argument('offset', help='where to decompile')
    parser_d.add_argument('--raw', action='store_true',
                          help='Be dumb (display everything as raw bytes)')
    parser_d.add_argument('--text', action='store_true',
                          help='Decompile as text')
    h = 'How many nop bytes until it stops (0 to never stop). Defaults to 10'
    parser_d.add_argument('--max-nops', default=10, type=int, help=h)

    global END_COMMANDS
    for end_command in END_COMMANDS:
        msg = ('whether or not to stop decompiling when a ' + end_command +
               ' is found')
        parser_d.add_argument('--continue-on-' + end_command,
                              action='append_const',
                              dest='END_COMMANDS_to_delete',
                              const=end_command, help=msg)
    h = 'whether or not to stop decompiling when a 0xFF byte is found'
    parser_d.add_argument('--continue-on-0xFF', action='store_true', help=h)
    parser_d.set_defaults(command='d')

    args = parser.parse_args()
    if not "command" in args:
        parser.print_help()
        exit(1)

    global QUIET, MAX_NOPS, VERBOSE
    QUIET = args.quiet
    VERBOSE = args.verbose
    MAX_NOPS = (args.MAX_NOPS if MAX_NOPS in args else 10)

    if args.command in ["b", "c"]:
        debug("reading file...")
        script = open_script(args.script)
        vdebug(script)
        debug("compiling high-level stuff...")
        script = dirty_compile(script)
        vdebug(script)
        if args.command == "b" and args.compile_only:
            print(script)
            return
        elif args.command == "b" and args.parse_only:
            parsed_script, error, dyn = asm_parse(script)
            pprint(parsed_script)
            print(error)
            print(dyn)
            return
        hex_script, log = assemble(script, args.rom)
        if args.command == "c":
            write_hex_script(hex_script, args.rom)
        else:
            debug("\nHex:")
            for addr, chunk in hex_script:
                debug(addr)
                phdebug(chunk)
        print("\nLog:")
        print(log)

    elif args.command == "d":
        if not args.END_COMMANDS_to_delete:
            args.END_COMMANDS_to_delete = []
        for end_command in args.END_COMMANDS_to_delete:
            END_COMMANDS.remove(end_command)
        print("'" + '-'*20)
        end_hex_commands = [] if args.continue_on_0xFF else END_HEX_COMMANDS
        type = "text" if args.text else "script"
        print(decompile(args.rom, int(args.offset, 16), type, raw=args.raw,
                        end_commands=END_COMMANDS,
                        end_hex_commands=end_hex_commands))


if __name__ == "__main__":
    main()


