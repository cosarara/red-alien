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
import argparse
from . import compiler
from .compiler import assemble, compile_script, write_hex_script
from . import decompiler
from .decompiler import decompile
from . import utils
from .utils import open_script, debug, vdebug, phdebug, data_path
from . import pokecommands as pk

def text_len(text):
    #"0-9": "6",
    #"..": "6",
    #"A-Z": "6",
    #"a-h": "6",
    #"s-z": "6",
    #"m-q": "6",
    #"€": "6",
    #'"': "6 (both)",
    #"k": "6",
    #"/": "6",
    #"male": "6",
    #"female": "6",
    kernings = {
        "!": 3,
        "?": 6,
        ".": 3,
        #":": 5,
        "·": 3,
        "'": 3,
        ",": 3,
        "i": 4,
        "j": 5,
        "l": 3,
        "r": 5,
        ":": 3,
        "↑": 7,
        "→": 7,
        "↓": 7,
        "←": 7,
        "+": 7,
        " ": 3,
    }
    return sum([kernings[c] if c in kernings else 6 for c in text])

def autocut_text(text):
    maxlen = 35 * 6
    words = text.split(" ")
    text = ''
    line = ''
    i = 0
    delims = ('\\n', '\\p')
    delim = 0
    while i < len(words):
        word = words[i]
        if text_len(word) > maxlen:
            line += words[i] + " "
            i += 1
        while i < len(words) and text_len(line+words[i]) < maxlen:
            word = words[i]
            line += word + " "
            i += 1
        text += line.rstrip(" ") + delims[delim]
        delim = not delim
        line = ''
    text = text.rstrip('\\p').rstrip('\\n').rstrip(" ")
    return text

def find_nth(text, string, n):
    start = text.find(string)
    while start >= 0 and n > 1:
        start = text.find(string, start+len(string))
        n -= 1
    return start


def get_base_directive(rom_fn):
    with open(rom_fn, "rb") as f:
        f.seek(0xAC)
        code = f.read(4)
    return "#define " + {
        b"AXVE": "RS",
        b"BPRE": "FR",
        b"BPEE": "EM"}[code] + "\n"

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

def get_canvas():
    with open(os.path.join(data_path, "canvas.pks"), encoding="utf8") as f:
        text = f.read()
    return text

def make_clean_script(hex_script):
    text = "// cleaning script"
    for addr, chunk in hex_script:
        text += "\n#org {}\n".format(addr)
        for _ in range(len(chunk)):
            text += "#raw 0xFF\n"
        #text += "="+"\\xFF"*len(chunk)+"\n"
    return text

def get_program_dir():
    try:
        return os.path.dirname(__file__)
    except NameError:
        return os.path.dirname(sys.executable)

def main():
    description = 'Red Alien, an Advanced (Pokémon) Script Compiler'
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('--quiet', action='store_true', help='Be quiet')
    parser.add_argument('--verbose', '-v', action='count', help='Be verbose. Like, a lot')
    parser.add_argument('--mode', default="event", type=str,
                        help='what kind of bytecode, default is map events (event)')
    subparsers = parser.add_subparsers(help='available commands:')

    parser_c = subparsers.add_parser('c', help='compile')
    parser_c.add_argument('rom', help='path to ROM image')
    parser_c.add_argument('script', help='path to pokemon script')
    parser_c.add_argument('--clean', action='store_true',
                          help='Produce a cleaning script')
    parser_c.set_defaults(command='c')

    parser_b = subparsers.add_parser('b', help='debug')
    parser_b.add_argument('rom', help='path to ROM image')
    parser_b.add_argument('script', help='path to pokemon script')
    parser_b.add_argument('--clean', action='store_true',
                          help='Produce a cleaning script')
    parser_b.set_defaults(command='b')

    parser_d = subparsers.add_parser('d', help='decompile')
    parser_d.add_argument('rom', help='path to ROM image')
    parser_d.add_argument('offset', help='where to decompile')
    parser_d.add_argument('--raw', action='store_true',
                          help='Be dumb (display everything as raw bytes)')
    parser_d.add_argument('--moves', action='store_true',
                          help='Decompile as moves')
    parser_d.add_argument('--text', action='store_true',
                          help='Decompile as text')
    h = 'How many nop bytes until it stops (0 to never stop). Defaults to 10'
    parser_d.add_argument('--max-nops', default=10, type=int, help=h)

    for end_command in decompiler.END_COMMANDS:
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
    modes = {
        "event": (pk.pkcommands, pk.dec_pkcommands, pk.end_pkcommands),
        "battle_ai": (pk.aicommands, pk.dec_aicommands, pk.end_aicommands),
        "battle": (pk.bscommands, pk.dec_bscommands, pk.end_bscommands),
    }
    if "command" not in args or args.mode not in modes:
        print('MODE not one of', list(modes.keys()))
        parser.print_help()
        sys.exit(1)
    cmd_table, dec_table, end_cmds = modes[args.mode]

    utils.QUIET = args.quiet
    utils.VERBOSE = args.verbose
    decompiler.MAX_NOPS = args.max_nops if 'max_nops' in args else 10

    if args.command in ["b", "c"]:
        debug("reading file...", args.script)
        script = open_script(args.script)
        vdebug(script)
        debug("compiling high-level stuff...")
        try:
            script = get_base_directive(args.rom) + script
        except KeyError:
            pass
        include_path = ("", ".", os.path.dirname(args.rom),
                        os.path.dirname(args.script), get_program_dir(),
                        data_path, os.path.join(data_path, "stdlib"))
        cleanlines = compile_script(script, include_path, args.script)
        if utils.VERBOSE:
            print("\nscript compiled down to asm:")
            compiler.print_lines(cleanlines)
            print("end of script\n")
        hex_script, log = assemble(cleanlines, args.rom, include_path, cmd_table=cmd_table)
        if args.clean:
            with open(args.script+".clean.pks", "w") as f:
                f.write(make_clean_script(hex_script))

        if args.command == "c":
            debug("writing")
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
            decompiler.END_COMMANDS.remove(end_command)
        print("'" + '-'*20)
        end_hex_commands = [] if args.continue_on_0xFF else decompiler.END_HEX_COMMANDS
        type_ = "text" if args.text else "movs" if args.moves else "script"
        print(decompile(args.rom, int(args.offset, 16), type_, raw=args.raw,
                        end_hex_commands=end_hex_commands,
                        cmd_table=cmd_table,
                        dec_table=dec_table,
                        end_commands=end_cmds,
                        verbose=args.verbose if args.verbose is not None else 0))


if __name__ == "__main__":
    main()


