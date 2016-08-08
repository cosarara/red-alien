#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from collections import namedtuple
from ast import literal_eval

from .operators import OPERATOR_LIST, OPERATORS, OPPOSITE_OPERATORS
from .utils import open_script, find_file, debug, vdebug, get_rom_offset
from . import pokecommands as pk
from . import text_translate

Line = namedtuple('Line', ['file_name', 'line_num', 'text'])
CleanLine = namedtuple('CleanLine', ['items', 'source_line'])

def print_source_location(self):
    return "{}:{} - {}\n{}".format(self.source_line.file_name,
                                           self.source_line.line_num,
                                           self.items,
                                           self.source_line.text)
CleanLine.__repr__ = print_source_location

SourceBlock = namedtuple('SourceBlock', ['origin', 'lines'])

# TODO:
# support opening brace on new line

def get_source_lines(script_src, file_name):
    return [Line(file_name, line_num+1, text) for
            line_num, text in enumerate(script_src.split('\n'))]

def remove_comments(text):
    pattern = "(//|')(.*?)$"
    replace = lambda s: re.sub(pattern, "", s)
    # remove comments only in nontext lines
    text = "\n".join([replace(s) if (len(s) > 1 and s[0] != "=") else s
                      for s in text.split("\n")])
    return text

def preprocess(source_lines, include_path, game):
    symbols = {}
    if game:
        symbols = {game: True}
    out = []
    removing = False # inside false #ifdef, etc.
    # can't iterate because we'll mutate the list
    n = 0
    if_level = 0
    while n < len(source_lines):
        line = source_lines[n]
        n += 1
        clean_line = remove_comments(line.text)
        # merge line continuation \
        while clean_line and clean_line[-1] == "\\":
            clean_line = clean_line[:-1]
            clean_line += source_lines[n].text
            n += 1
            if n == len(source_lines):
                raise Exception("Script file cannot end in \\")
        line_items = clean_line.split()
        if not line_items:
            continue
        command = line_items[0]
        args = line_items[1:]
        if command == "#endif":
            if if_level == removing:
                removing = False
            if_level -= 1
            if if_level < 0:
                raise Exception('found #endif without matching #if {}'.format(line))
            continue
        if re.match('^#if', command):
            if len(args) != 1:
                raise Exception('wrong arg number at {}'.format(line))
            if_level += 1 # if we are removing, we've come here just for this
            if removing:
                continue
            if command == "#ifdef":
                removing = args[0] not in symbols
            elif command == "#ifndef":
                removing = args[0] in symbols
            else:
                raise Exception("unknown #if thing at {}".format(line))
            if removing:
                removing = if_level
            continue
        if command == "#else":
            removing = not removing
            continue
        if removing:
            continue
        if command == "#define":
            if len(args) == 1:
                symbols[args[0]] = True
            elif len(args) > 1:
                symbols[args[0]] = " ".join(args[1:])
            else:
                raise Exception('wrong arg number at {}'.format(line))
            continue
        if command == "#include":
            if len(args) != 1:
                raise Exception('wrong arg number at {}'.format(line))
            file_name = find_file(args[0], include_path)
            source_lines[n-1:n] = get_source_lines(open_script(file_name), file_name)
            n -= 1
            continue

        for symbol in symbols:
            value = symbols[symbol]
            items = clean_line.split()
            if items[0] == symbol and "$" in value:
                args = items[1:]
                new_line = value
                for arg_n, arg in enumerate(args):
                    new_line = new_line.replace("$"+str(arg_n+1), arg)
                clean_line = new_line
            else:
                clean_line = " ".join(
                    [str(value) if item == symbol else item for item in items])
        for l in clean_line.split(';'):
            if not l:
                continue
            l_items = l.split()
            if l_items and l_items[0] == '=':
                out.append(CleanLine(['=', l[l.find('=')+2:]], line))
            else:
                out.append(CleanLine(l.split(), line))
    return out, symbols

last_id = 0
def get_uid():
    global last_id
    last_id += 1
    return str(last_id)

def print_lines(clines):
    for cline in clines:
        print(' '.join(cline.items))

def separate_multilines(cleanlines):
    """ if there are multiple things on a line, like } },
    separate them"""
    # TODO: only does } atm,
    # should do ;, if () {, etc.
    cleanlines = list(cleanlines)
    n = 0
    safe = 0
    while n < len(cleanlines):
        safe += 1
        if safe > 10:
            break
        cleanline = cleanlines[n]
        n += 1
        line = ' '.join(cleanline.items)
        a = line.find('}')
        if a != -1:
            before = line[:a].strip()
            after = line[a+1:].strip()
            to_insert = []
            if before:
                to_insert.append(CleanLine([before], cleanline.source_line))
            to_insert.append(CleanLine(['}'], cleanline.source_line))
            if after:
                to_insert.append(CleanLine([after], cleanline.source_line))
            cleanlines[n-1:n] = to_insert
            if before or after:
                n -= 1
    return cleanlines

def find_matching_bracket(cleanlines, start):
    n = start
    level = 0
    while n < len(cleanlines):
        line = ' '.join(cleanlines[n].items)
        if "{" in line:
            level += 1
        if "}" in line:
            level -= 1
        if level == -1:
            return n
        n += 1
    return None

def instructions_for_condition(condition, end_label):
    #condition = condition.strip()
    to_insert = []
    for operator in OPERATOR_LIST:
        if operator in condition:
            var, constant = condition.split(operator)
            # TODO: comparevars?
            to_insert.append("compare {} {}".format(var.strip(), constant.strip()))
            to_insert.append("if {} jump {}".format(OPPOSITE_OPERATORS[operator],
                                                    end_label))
            break
    else:
        # We are checking a flag
        if condition[0] == "!":
            flag = condition[1:]
            operator = "1"
        else:
            flag = condition
            operator = "0"
        to_insert.append("checkflag {}".format(flag))
        to_insert.append("if {} jump {}".format(operator, end_label))
    return to_insert


def highlevel(cleanlines):
    cleanlines = list(cleanlines)
    n = 0
    while n < len(cleanlines):
        cleanline = cleanlines[n]
        start_n = n
        n += 1
        line = ' '.join(cleanline.items)
        fif = re.match(r'if\s*\(', line)
        fwhile = re.match(r'while\s*\(', line)
        if not fif and not fwhile:
            continue
        condition = re.search(r'\((.*?)\)', line)
        if not condition:
            raise Exception('Control struct without condition at {}'.format(cleanline))
        condition = condition.group(1).strip()
        # pretty hackish
        if re.match('(?:if|while)\s*\(.*?\)\s*{', line):
            if not re.match('(?:if|while)\s*\(.*?\)\s*{$', line):
                raise Exception('garbage at the end of the line at {}'.format(cleanline))
        else:
            if cleanlines[n].items != ['{']:
                raise Exception('Control struct without opening brace {{ at {}'.format(cleanline))
            n += 1
        to_insert = [] # bare strings
        if fwhile:
            label_id = get_uid()
            start_label = ':while_start'+label_id
            end_label = ':while_end'+label_id
            to_insert.append(start_label)
            to_insert += instructions_for_condition(condition, end_label)

            to_insert = [CleanLine(t.split(), cleanline.source_line) for t in to_insert]
            cleanlines[start_n:n] = to_insert
            end_pos = find_matching_bracket(cleanlines, n+1)
            if end_pos is None:
                raise Exception("No matching }} found for line {}".format(cleanline))
            to_insert = ["jump {}".format(start_label), end_label]
            to_insert = [CleanLine(t.split(), cleanlines[end_pos].source_line)
                         for t in to_insert]
            cleanlines[end_pos:end_pos+1] = to_insert
        elif fif:
            # you have to write first the end, then the start, because
            # you fuck up the indices otherwise
            label_id = get_uid()
            end_label = ':if_end'+label_id
            end_pos = find_matching_bracket(cleanlines, n) #if's end
            if end_pos is None:
                raise Exception("matching bracket not found for {}".format(cleanline))
            if len(cleanlines) > end_pos+1 and re.match(
                    'else', cleanlines[end_pos+1].items[0]):
                del cleanlines[end_pos+1]
                else_start = end_pos
                else_start_label = ':else_start'+label_id
                else_end_label = ':else_end'+label_id

                to_insert = [else_end_label]
                else_end = find_matching_bracket(cleanlines, else_start+2)
                to_insert = [CleanLine(t.split(), cleanlines[else_end].source_line)
                             for t in to_insert]
                cleanlines[else_end:else_end+1] = to_insert

                end_label = else_start_label
                end_pos = else_start

            # you have to write first the end, then the start, because
            # you fuck up the indices otherwise
            # end
            to_insert = [end_label]
            to_insert = [CleanLine(t.split(), cleanlines[end_pos].source_line)
                         for t in to_insert]
            cleanlines[end_pos:end_pos+1] = to_insert
            # start
            to_insert = instructions_for_condition(condition, end_label)
            to_insert = [CleanLine(t.split(), cleanline.source_line) for t in to_insert]

            cleanlines[start_n:n] = to_insert
    return cleanlines

def compile_script(text, include_path, filename, game):
    """ goes from text to a list of CleanLine's,
    each with a list of simple items:
    #org, #dyn, #raw, commands, :labels and = lines"""
    lines, symbols = preprocess(get_source_lines(text, filename), include_path, game)
    return highlevel(separate_multilines(lines)), symbols

def parse_int(nn, line=""):
    try:
        n = int(literal_eval(nn))
    except (TypeError, SyntaxError, ValueError):
        raise Exception("Bad number {} at {}".format(nn, line))
    return n

def separate_scripts(cleanlines): #, end_commands=("end", "softend"),
              #cmd_table=pk.pkcommands):
    ''' Separates blocks at #org positions
    returns list of blocks and dynamic address '''
    # a list of SourceChunk
    block_list = []
    dyn = None
    for line in cleanlines:
        command = line.items[0]
        args = line.items[1:]
        if command == "#org":
            if len(args) != 1:
                raise Exception("wrong number of args for #org at {}".format(line))
            if args[0][0] == '@' and dyn is None:
                raise Exception("#org with @label used before #dynamic at {}".format(line))
            block_list.append(SourceBlock(args[0], []))
        elif command == "#dyn" or command == "#dynamic":
            if dyn:
                raise Exception("second #dyn seen at {}".format(line))
            if len(args) != 1:
                raise Exception("wrong number of args for #dyn at {}".format(line))
            dyn = parse_int(args[0], line)
        else:
            if len(block_list) == 0:
                raise Exception("something without previous #org at {}".format(line))

            if command == "if":
                if len(args) != 3:
                    raise Exception("wrong number of args on if at {}".format(line))
                if args[1] in ["jump", "goto"]:
                    branch = "jumpif"
                elif args[1] == "call":
                    branch = "callif"
                elif args[1] in ["jumpstd", "gotostd"]:
                    branch = "jumpstdif"
                elif args[1] == "callstd":
                    branch = "callstdif"
                else:
                    raise Exception("Command after 'if' must be jump, call, "
                                    "jumpstd, callstd or goto variant at {}".format(line))
                operator = args[0]
                if operator in OPERATORS:
                    operator = OPERATORS[operator]
                line = CleanLine([branch, operator, args[2]], line.source_line)

            block_list[-1].lines.append(line)
    return block_list, dyn

def make_bytecode(script_list, cmd_table, have_dynamic, have_labels,
                  incbin_path, end_strings=False):
    ''' Compile list of ScriptBlock '''
    hex_scripts = []
    Label = namedtuple("Label", ['name', 'offset'])
    for script in script_list:
        addr = script.origin
        bytecode = b""
        labels = []

        for line in script.lines:
            command = line.items[0]
            vdebug(' '.join(line.items))
            args = line.items[1:]
            def assert_argn(expected_args):
                if expected_args != len(args):
                    raise Exception(
                        "wrong arg number, expected {} and got {} at {}".format(
                            expected_args, len(args), line))
            if command == '=':
                text = line.items[1]
                bytecode += text_translate.ascii_to_hex(text)
                if end_strings:
                    bytecode += b'\xff'
                continue
            try:
                if command == '#raw' or command == "#byte":
                    assert_argn(1)
                    bytecode += parse_int(args[0], line).to_bytes(1, "little")
                    continue
                if command == '#hword':
                    assert_argn(1)
                    bytecode += parse_int(args[0], line).to_bytes(2, "little")
                    continue
                if command == '#word':
                    assert_argn(1)
                    arg = args[0]
                    if arg[0] in "@:":
                        if arg[0] == "@" and have_dynamic is None:
                            raise Exception("@label without #dyn at {}".format(line))
                        if arg[0] == ":" and not have_labels:
                            raise Exception(":label {} not defined at {}".format(arg, line))
                        bytecode += b'\x00\x00\x00\x00'
                    else:
                        bytecode += parse_int(args[0], line).to_bytes(4, "little")
                    continue
            except OverflowError:
                raise Exception("arg {} too big for {} at {}".format(
                    args[0], command, line))

            if command == "#incbin":
                assert_argn(1)
                fn = find_file(args[0], incbin_path)
                with open(fn, 'rb') as f:
                    bytecode += f.read()
                continue

            if command[0] == ":":
                if any(label.name == command for label in labels):
                    raise Exception("repeated label {} at {}".format(command, line))
                labels.append(Label(command, len(bytecode)))
                continue

            if command not in cmd_table:
                raise Exception("command {} not found at {}".format(command, line))

            expected_args = len(cmd_table[command]["args"][1])
            if command != '=':
                assert_argn(expected_args)
            hexcommand = cmd_table[command]["hex"]
            hexargs = bytearray()
            for i, arg in enumerate(args):
                if arg[0] != "@" and arg[0] != ":":
                    arg_len = cmd_table[command]["args"][1][i]
                    arg = parse_int(arg, line)
                    #if arg[0:2] != "0x":
                    #    arg = (int(arg) & 0xffffff)
                    #else:
                    #    arg = int(arg, 16)
                    if "offset" in cmd_table[command]:
                        for o in cmd_table[command]["offset"]:
                            if o[0] == i:
                                arg |= 0x8000000
                    try:
                        arg_bytes = arg.to_bytes(arg_len, "little")
                    except OverflowError:
                        raise Exception("arg {} too big for len {} at {}".format(
                            arg, arg_len, line))

                    # what is this? padding? used only on loadpointer?
                    if len(cmd_table[command]["args"]) == 3:
                        arg_bytes = (cmd_table[command]["args"][2] +
                                     arg_bytes)
                    hexargs += arg_bytes
                else:
                    if arg[0] == "@" and have_dynamic is None:
                        raise Exception("@label without #dyn at {}".format(line))
                    if arg[0] == ":" and not have_labels:
                        raise Exception(":label {} not defined at {}".format(arg, line))
                    # this pass
                    # is just for calculating space,
                    # so we fill this with dummy bytes
                    arg = b"\x00\x00\x00\x08"
                    # what is this? padding? used only on loadpointer?
                    if len(cmd_table[command]["args"]) == 3:
                        arg = (cmd_table[command]["args"][2] + arg)
                    hexargs += arg
            bytecode += hexcommand.to_bytes(1, "little") + hexargs

        hex_script = [addr, bytecode, labels]
        hex_scripts.append(hex_script)
    return hex_scripts

def blocks_replace(blocks, replacements):
    r = replacements
    return [
        SourceBlock(
            r[block.origin] if block.origin in r else block.origin,
            [CleanLine(
                [line.items[0]] +
                [r[item] if item in r else item for item in line.items[1:]],
                line.source_line) for line in block.lines])
        for block in blocks]

def put_addresses_labels(hex_chunks, blocks):
    ''' Calculates the real address for :labels and does the needed
        searches and replacements. '''
    replacements = {}
    for chunk in hex_chunks:
        for label in chunk[2]:
            vdebug(label)
            name = label[0]
            pos = hex(int(chunk[0], 16) + label[1])
            #vdebug(pos)
            replacements[name] = pos
    blocks = blocks_replace(blocks, replacements)
    return blocks

def put_addresses(hex_chunks, blocks, file_name, dynamic_start, pre_pad, post_pad):
    ''' Find free space and replace #dynamic @labels with real addresses '''
    rom_file_r = open(file_name, "rb")
    rom_bytes = rom_file_r.read()
    rom_file_r.close()
    offsets_found_log = ''
    last = dynamic_start
    replacements = {}
    for i, chunk in enumerate(hex_chunks):
        vdebug(chunk)
        label = chunk[0]
        part = chunk[1] # The hex chunk we have to put somewhere
        #labels = chunk[2]
        if label[0] != "@":
            continue
        length = len(part) + 2
        free_space = b"\xFF" * length
        address_with_free_space = rom_bytes.find(free_space, last)
        # It's always good to leave some margin around things.
        # If there is free space at the address the user has given us,
        # though, it's ok to use it without margin.
        if address_with_free_space != dynamic_start:
            address_with_free_space += pre_pad
        if address_with_free_space == -1:
            print(len(rom_bytes))
            print(len(free_space))
            print(dynamic_start)
            print(last)
            raise Exception("No free space to put script.")
        new_addr = hex(address_with_free_space)
        replacements[label] = new_addr
        hex_chunks[i][0] = new_addr
        last = address_with_free_space + length + post_pad # padding TODO: user configurable
        offsets_found_log += (label + ' - ' +
                              hex(address_with_free_space) + '\n')

    blocks = blocks_replace(blocks, replacements)
    return blocks, offsets_found_log

def write_hex_script(hex_scripts, rom_file_name):
    ''' Write every chunk of bytes onto the big ROM file '''
    file_name = rom_file_name
    with open(file_name, "rb") as f:
        rom_bytes = f.read()
    rom_ba = bytearray(rom_bytes)
    for script in hex_scripts:
        offset = int(script[0], 16)
        offset = get_rom_offset(offset)
        hex_script = script[1]
        vdebug("chunk length = " + hex(len(hex_script)))
        rom_ba[offset:offset+len(hex_script)] = hex_script

    with open(file_name, "wb") as f:
        f.write(rom_ba)

def assemble(script, rom_file_name, include_path, symbols, cmd_table=pk.pkcommands):
    ''' Compiles a plain script and returns a tuple containing
        a list and a string. The string is the #dyn log.
        The list contains a list for every location where
        something should be written. These lists are 2
        elements each, the offset where data should be
        written and the data itself,
        Symbols provide config by magic macros'''
    debug("separating blocks...")
    #parsed_script, dyn = asm_parse(script, cmd_table=cmd_table)
    blocks, dyn = separate_scripts(script)
    #vpdebug(parsed_script)
    debug("compiling down to bytecode...")
    end_strings = "_TERMINATE_STRINGS" in symbols
    hex_script = make_bytecode(blocks, cmd_table, dyn, True, include_path, end_strings)
    debug(hex_script)
    log = ''
    debug("doing dynamic and label things...")

    if dyn and rom_file_name:
        debug("going dynamic!")
        debug("replacing dyn addresses by offsets...")
        pre_pad = 2
        post_pad = 10
        if "_PRE_DYN_PADDING" in symbols:
            pre_pad = parse_int(symbols["_PRE_DYN_PADDING"])
        if "_POST_DYN_PADDING" in symbols:
            post_pad = parse_int(symbols["_POST_DYN_PADDING"])
        blocks, log = put_addresses(hex_script, blocks, rom_file_name, dyn, pre_pad, post_pad)
        #vdebug(script)

    # Now with :labels we have to recompile even if

    debug("re-preparsing")

    blocks = put_addresses_labels(hex_script, blocks)

    #parsed_script, dyn = asm_parse(script, cmd_table=cmd_table)
    debug("recompiling")
    hex_script = make_bytecode(blocks, cmd_table, None, False, include_path, end_strings)

    # Remove the labels list, which will be empty and useless now
    for chunk in hex_script:
        del chunk[2] # Will always be []
    return hex_script, log
