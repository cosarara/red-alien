#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from collections import namedtuple

from .utils import debug, vdebug, data_path, get_rom_offset
from . import pokecommands as pk
from . import text_translate
from .compiler import remove_comments

MAX_NOPS = 10
END_COMMANDS = ["end", "jump", "return"]
END_HEX_COMMANDS = [0xFF]

Chunk = namedtuple("Chunk", ["addr", "type", "length", "content"])
Instruction = namedtuple("Instruction", ["addr", "name", "cmd", "args", "length"])


def decompile(file_name, start_address, type_="script",
              cmd_table=pk.pkcommands, dec_table=pk.dec_pkcommands,
              end_commands=END_COMMANDS, end_hex_commands=END_HEX_COMMANDS,
              verbose=0):
    """
    An instruction has:
    * a start address
    * command name
    * a command: entry in pk.pkcommands
    * arguments:
        * pairs of (int value, nice text)
    * a length

    We build a list of chunks, then convert it to a string and return it.
    """
    with open(file_name, "rb") as f:
        rombytes = f.read()

    # build mov table
    with open(os.path.join(data_path, "stdlib", "stdmoves.rbh")) as f:
        moves = f.read()
    moves = moves.split("//@")
    rom_code = rombytes[0xAC:0xAC+4].decode("ascii", errors="replace")
    includes = set()
    for movelist in moves:
        if (rom_code == "AXVE" and movelist.startswith("applymoves_rs") or
                rom_code == "BPRE" and movelist.startswith("applymoves_fr")):

            moves = filter(lambda s: "#define" in s,
                                remove_comments(movelist).split("\n"))
            moves = {int(value, 16): name
                     for _, name, _, value in map(str.split, moves)}
            break
    else:
        moves = {}

    chunk = Chunk(start_address, type_, None, None)
    todo_chunks = [chunk]
    done_chunks = []
    chunks = [chunk]

    def is_redundant(c, chunks):
        for c2 in chunks:
            if c is c2:
                continue
            if c.type != c2.type:
                continue
            if c.addr == c2.addr:
                return c2
            if c2.length is None:
                continue
            if c.addr >= c2.addr and c.addr < c2.addr+c2.length:
                return c2
        return False

    while todo_chunks:
        # remove redundant todo chunks:
        todo_chunks = list(filter(
            lambda c: not is_redundant(c, todo_chunks+done_chunks),
            todo_chunks))

        if not todo_chunks:
            break

        # decompile a chunk

        c, nc = decompile_chunk(todo_chunks.pop(), rombytes, chunks, cmd_table, dec_table,
                                end_commands, end_hex_commands, moves, verbose)
        todo_chunks += nc
        done_chunks.append(c)

    chunks = done_chunks
    chunks = list(filter(lambda c: not is_redundant(c, chunks), chunks))

    # Convert to text
    text = ""
    for chunk in sorted(chunks, key=lambda i: chunk.addr):
        if chunk.length is None:
            continue
        text += "\n#org 0x{:x}\n".format(chunk.addr)
        if chunk.type in ["script", "movs"]:
            #print("' chunk")
            for instruction in chunk.content:
                if instruction.addr != chunk.addr:
                    for chunk2 in chunks:
                        if instruction.addr == chunk2.addr:
                            text += "' joined\n"
                            text += "#org 0x{:x}\n".format(chunk2.addr)
                #print(instruction.name, instruction.args, "'", instruction.addr)
                if instruction.name is not None:
                    text += instruction.name
                    if instruction.args:
                        text += ' '
                    text += ' '.join(nice for num, nice in instruction.args)
                    text += '\n'
                else:
                    text += "#raw 0x{:02X}\n".format(instruction.cmd["hex"])
        elif chunk.type == "text":
            text += split_text(chunk.content)
        if chunk.type == "movs":
            includes.add("stdlib/stdmoves.rbh")

    for inc in includes:
        text = '#include "' + inc + '"\n' + text
    return text

def decompile_chunk(chunk, rombytes, chunks,
                    cmd_table=pk.pkcommands, dec_table=pk.dec_pkcommands,
                    end_commands=END_COMMANDS, end_hex_commands=END_HEX_COMMANDS,
                    moves={}, verbose=0):
    address = chunk.addr
    content = []
    new_chunks = []
    if chunk.type == "script":
        while True:
            instruction, nc = decompile_instruction(
                rombytes, address, cmd_table, dec_table, chunks, verbose)
            new_chunks = new_chunks + nc
            #print(instruction)
            address += instruction.length
            content.append(instruction)
            if (instruction.name in end_commands or
                    instruction.cmd["hex"] in end_hex_commands):
                break
    elif chunk.type == "movs":
        while True:
            b = rombytes[address]
            name = None
            if b in moves:
                name = moves[b]
            instruction = Instruction(addr=address, name=name, cmd={"hex": b},
                                      args=[], length=1)
            address += 1
            content.append(instruction)
            if (instruction.name in END_COMMANDS or
                    instruction.cmd["hex"] in (0xFE, 0xFF)):
                break
    elif chunk.type == "text":
        length = rombytes[chunk.addr:].find(b"\xff")
        content = decompile_text(rombytes, chunk.addr)
    length = address - chunk.addr
    return Chunk(chunk.addr, chunk.type, length, content), new_chunks

def decompile_instruction(rombytes, start_address,
                          cmd_table=pk.pkcommands, dec_table=pk.dec_pkcommands,
                          chunks=[], verbose=0):
    new_chunks = []
    address = start_address
    cmd_val = rombytes[address]
    try:
        cmd_name = dec_table[cmd_val]
        cmd = cmd_table[cmd_name]
    except KeyError:
        cmd_name = None
        cmd = {'hex': cmd_val}

    def is_redundant(addr, type_, chunks):
        for c2 in chunks:
            if type_ != c2.type:
                continue
            if addr == c2.addr:
                return c2
            if c2.length is None:
                continue
            if addr >= c2.addr and addr < c2.addr+c2.length:
                return c2
        return False

    def add_chunk(address, type_):
        address &= 0xFFFFFF
        if not is_redundant(address, type_, chunks):
            new_chunks.append(Chunk(address, type_, None, None))

    address += 1
    args = []
    if "vargs" in cmd:
        type_ = rombytes[address]
        arg_data = cmd["vargs"]([type_])
        for n, arg_len in enumerate(arg_data):
            arg = rombytes[address:address + arg_len]
            address += arg_len
            arg = int.from_bytes(arg, "little")
            if "vptr" in cmd:
                for o_arg_n, o_type in cmd["vptr"]([type_]):
                    if o_arg_n == n:
                        add_chunk(arg, o_type)
            carg, inc = const_arg(cmd_name, arg, n, cmd_table,
                                  dec_table, rombytes, "", types="")
            if carg is None:
                args.append((arg, hex(arg)))
            else:
                args.append((arg, carg))

    elif "args" in cmd:
        if len(cmd["args"]) == 3: # extra padding, happens only with loadpointer
            address += len(cmd["args"][2])
        for n, arg_len in enumerate(cmd["args"][1]):
            arg = rombytes[address:address + arg_len]
            address += arg_len
            arg = int.from_bytes(arg, "little")
            if "offset" in cmd:
                for o_arg_n, o_type in cmd["offset"]:
                    if o_arg_n == n:
                        #print("adding to do chunk at "+hex(arg)+" of type "+str(o_type)+" in "+str(cmd)+" "+hex(address))
                        add_chunk(arg, o_type)
            carg, inc = const_arg(cmd_name, arg, n, cmd_table,
                                  dec_table, rombytes, "")
            if carg is None:
                args.append((arg, hex(arg)))
            else:
                #if not inc in incs:
                #    incs.append(inc)
                args.append((arg, carg))

    instruction = Instruction(
        addr=start_address,
        name=cmd_name,
        cmd=cmd,
        args=args,
        length=address - start_address)
    return instruction, new_chunks

def get_const_replacements():
    """
    Fetch all constants from header files to use in const_arg
    """
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
    return args_for_type

args_for_type = get_const_replacements()

def const_arg(cmd, arg, arg_i, cmd_table, dec_table, rombytes, history, types=None):
    """ Translates an argument to a suitable constant
    TODO: make it work with non-AI scripts
    """
    cmd_data = cmd_table[cmd]
    #print(cmd)
    if types is None:
        types = cmd_data["args"][0]
    #sizes = cmd_data["args"][1]
    try:
        type = types.split(",")[arg_i].strip()
    except IndexError:
        return None, ""
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

def decompile_text(romtext, offset, raw=False):
    rom_offset = get_rom_offset(offset)
    start = rom_offset
    end = start + romtext[start:].find(b"\xff")
    text = romtext[start:end+1]
    text_table = text_translate.table_str
    # decoding table
    d_table = text_translate.read_table_decode(text_table)
    translated_text = text_translate.hex_to_ascii(text, d_table)
    return translated_text

def split_text(text):
    splittable = ("\\n", "\\p", "\\l", " ", "\\c", "\\v")
    line = ""
    word = ""
    out = ""
    char = ""
    for n, c in enumerate(text):
        if char == "\\":
            char += c
        else:
            char = c
        if char == "\\":
            continue

        word += char
        if (char in splittable or n == len(text) - 1 or
                (len(word) >= 3 and word[-4:-2] == "\\h")): # word end
            if len(word) + len(line) > 78:
                if line:
                    out += "= " + line + "\n"
                line = word
            else:
                line += word
            word = ""
    out += "= " + line + "\n"
    return out
