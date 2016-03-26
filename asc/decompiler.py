#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

from .utils import debug, vdebug, data_path, get_rom_offset
from . import pokecommands as pk
from . import text_translate
from .compiler import remove_comments

MAX_NOPS = 10
END_COMMANDS = ["end", "jump", "return"]
END_HEX_COMMANDS = [0xFF]

def decompile(file_name, offset, type_="script", raw=False,
              end_commands=END_COMMANDS, end_hex_commands=END_HEX_COMMANDS,
              cmd_table=pk.pkcommands, dec_table=pk.dec_pkcommands,
              verbose=0):
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
        type_ = offsets[0][1]
        if type_ == "script":
            textscript_, new_offsets, incs = demake_bytecode(
                rombytes, offset, offsets,
                end_commands=end_commands,
                end_hex_commands=end_hex_commands,
                raw=raw,
                cmd_table=cmd_table,
                dec_table=dec_table,
                verbose=verbose)
            inced = False
            for inc in incs:
                a = '#include "{}"\n'.format(inc)
                if a not in textscript:
                    textscript += a
                    inced = True
            if inced:
                textscript += "\n"
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
            textscript += ("#org " + hex(offset) + "\n" + text + "\n")
        if type_ == "movs":
            textscript_tmp, includes = decompile_movs(rombytes, offset, raw=raw)
            textscript += ("#org " + hex(offset) + "\n" +
                           textscript_tmp + "\n")
            inctxt = ""
            for include in includes:
                inctxt += '#include "{}"\n'.format(include)
            textscript = inctxt + "\n" + textscript
        if type_ == "raw":
            textscript_tmp = decompile_rawb(rombytes, offset)
            textscript += ("#org " + hex(offset) + "\n" +
                           textscript_tmp + "\n")
        del offsets[0]
        decompiled_offsets.append(offset)
        # Removing duplicates doesn't hurt, right?
        decompiled_offsets = list(set(decompiled_offsets))
        if len(textscript) > 200000:
            raise Exception('This seems too long, crashing for your safety')
    return textscript

def const_arg(cmd, arg, arg_i, cmd_table, dec_table, rombytes, history):
    cmd_data = cmd_table[cmd]
    #print(cmd)
    types = cmd_data["args"][0]
    #sizes = cmd_data["args"][1]
    type = types.split(",")[arg_i].strip()
    intt = lambda a: int(a, 16) if a.startswith("0x") else int(a)
    # abilities
    with open(os.path.join(data_path, "stdlib", "stdabilities.rbh")) as f:
        abis = f.read().strip()
    abis = {intt(a.split()[2]): a.split()[1]
            for a in abis.split("\n")}
    # random args
    with open(os.path.join(data_path, "stdlib", "stdargs.rbh")) as f:
        arg_names_list = f.read().strip().split("//@")
    args_for_type = {}
    for arg_names in arg_names_list:
        this_type = arg_names.split("\n")[0]
        args = list(filter(lambda s: "#define" in s,
                           remove_comments(arg_names).split("\n")))
        arglist = {intt(value): name
                   for _, name, value in map(str.split, args)}
        args_for_type[this_type] = arglist
    # attacks
    with open(os.path.join(data_path, "stdlib", "stdattacks.rbh")) as f:
        attacks = f.read().strip()
    attacks = {intt(a.split()[2]): a.split()[1]
               for a in attacks.split("\n")}
    args_for_type["moveid"] = attacks
    # effects
    with open(os.path.join(data_path, "stdlib", "stdeffects.rbh")) as f:
        effects = f.read().strip()
    effects = {intt(a.split()[2]): a.split()[1]
               for a in effects.split("\n")}
    args_for_type["movescriptid"] = effects
    #
    with open(os.path.join(data_path, "stdlib", "stdargs.rbh")) as f:
        attacks = f.read().strip().split("\n")
    if cmd_table == pk.aicommands:
        if cmd[:3] == "bvb" and type == "byte":
            if "getability" in history: # todo: find latest relevant thing
                if arg in abis:
                    return abis[arg], "stdabilities.rbh"
        if type in args_for_type:
            args = args_for_type[type]
            header = ("stdattacks.rbh" if type == "moveid" else
                      "stdeffects.rbh" if type == "movescriptid" else
                      "stdargs.rbh")
            if arg in args:
                return args[arg], header
    return None, ""

def demake_bytecode(rombytes, offset, added_offsets,
                    end_commands=END_COMMANDS,
                    end_hex_commands=END_HEX_COMMANDS, raw=False,
                    cmd_table=pk.pkcommands,
                    dec_table=pk.dec_pkcommands,
                    verbose=0):
    rom_offset = get_rom_offset(offset)
    offsets = []
    hexscript = rombytes
    i = rom_offset
    textscript = ""
    text_command = ""
    hex_command = 0
    hex_command = hexscript[i]
    nop_count = 0 # Stop on 10 nops for safety
    incs = [] # include statements that will be added
    while (text_command not in end_commands and
           hex_command not in end_hex_commands):
        hex_command = hexscript[i]
        orig_i = i
        if hex_command in dec_table and not raw:
            text_command = dec_table[hex_command]
            textscript += text_command
            i += 1
            command_data = cmd_table[text_command]
            if "args" in command_data:
                if len(command_data["args"]) == 3:
                    i += len(command_data["args"][2])
                for n, arg_len in enumerate(command_data["args"][1]):
                    arg = hexscript[i:i + arg_len]
                    arg = int.from_bytes(arg, "little")
                    if "offset" in command_data:
                        for o_arg_n, o_type in command_data["offset"]:
                            if o_arg_n == n:
                                tuple_to_add = [arg, o_type]
                                if tuple_to_add not in added_offsets+offsets:
                                    offsets.append(tuple_to_add)
                    carg, inc = const_arg(text_command, arg, n, cmd_table,
                                          dec_table, rombytes, textscript)
                    if carg is None:
                        textscript += " " + hex(arg)
                    else:
                        if not inc in incs:
                            incs.append(inc)
                        textscript += " " + carg
                    i += arg_len
        else:
            textscript += "#raw " + hex(hex_command)
            i += 1
        if hex_command == 0:
            nop_count += 1
            if nop_count >= MAX_NOPS and MAX_NOPS != 0:
                textscript += " ' Too many nops. Stopping"
                break
        else:
            nop_count = 0

        if verbose >= 1:
            textscript += " //" + " ".join(hex(n)[2:].zfill(2) for n in hexscript[orig_i:i])
            if verbose >= 2:
                textscript += " -  " + hex(orig_i)
        textscript += "\n"
        if i - rom_offset > 10000:
            textscript += "' This is getting too big, I'll stop"
            break

    return textscript, offsets, incs

def decompile_rawh(romtext, offset, end_hex_commands=(0xFF,)):
    rom_offset = get_rom_offset(offset)
    vdebug(offset)
    hexscript = romtext
    i = rom_offset
    textscript = ""
    hex_command = ""
    while hex_command not in end_hex_commands:
        try:
            hex_command = hexscript[i]
        except IndexError:
            break
        textscript += "#raw " + hex(hex_command)
        i += 1
        textscript += "\n"
    return textscript

def decompile_rawb(romtext, offset, end_hex_commands=(0xFF,)):
    rom_offset = get_rom_offset(offset)
    vdebug(offset)
    hexscript = romtext
    i = rom_offset
    textscript = ""
    hex_command = ""
    while hex_command not in end_hex_commands:
        try:
            hex_command = hexscript[i]
        except IndexError:
            break
        textscript += "#raw " + hex(hex_command)
        i += 1
        textscript += "\n"
    return textscript

# TODO: use nice define'd thingies
def decompile_movs(romtext, offset, end_hex_commands=(0xFE, 0xFF), raw=False):
    rom_offset = get_rom_offset(offset)
    vdebug(offset)
    hexscript = romtext
    i = rom_offset
    textscript = ""
    hex_command = ""
    with open(os.path.join(data_path, "stdlib", "stdmoves.rbh")) as f:
        moves = f.read()
    moves = moves.split("//@")
    rom_code = romtext[0xAC:0xAC+4].decode("ascii")
    includes = []
    for movelist in moves:
        if (rom_code == "AXVE" and movelist.startswith("applymoves_rs") or
                rom_code == "BPRE" and movelist.startswith("applymoves_fr")):

            moves = list(filter(lambda s: "#define" in s,
                                remove_comments(movelist).split("\n")))
            moves = {int(value, 16): name
                     for _, name, _, value in map(str.split, moves)}
            break
    else:
        moves = {}
    while hex_command not in end_hex_commands:
        try:
            hex_command = hexscript[i]
        except IndexError:
            break

        if hex_command in moves:
            textscript += moves[hex_command]
            includes = ["stdmoves.rbh"]
        else:
            textscript += "#raw " + hex(hex_command)
        i += 1
        textscript += "\n"
    return textscript, includes


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

