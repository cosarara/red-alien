#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from pprint import pprint

USING_WINDOWS = (os.name == 'nt')

QUIET = False
VERBOSE = 0

# windows builds are frozen
if getattr(sys, 'frozen', False):
    data_path = os.path.join(os.path.dirname(sys.executable), "data")
else:
    data_path = os.path.join(os.path.dirname(__file__), "data")

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

def hprint(bytes_):
    def pad(s):
        return "0" + s if len(s) == 1 else s

    for b in bytes_:
        print(pad(hex(b)[2:]), end=" ")
    print("")

def phdebug(bytes_):
    if not QUIET:
        hprint(bytes_)

def get_rom_offset(offset):
    rom_offset = offset
    if rom_offset >= 0x8000000:
        rom_offset -= 0x8000000
    return rom_offset

def find_file(name, include_path):
    name = name.strip("<>\"")
    for d in include_path:
        fname = os.path.join(d, name)
        if os.path.isfile(fname):
            return fname
    raise FileNotFoundError("#include'd file {} not found".format(name))

def open_script(file_name):
    ''' Open file and replace \\r\\n with \\n '''
    with open(file_name, "r") as script_file:
        script_text = script_file.read()
    script_text = script_text.replace("\r\n", "\n")
    return script_text

def write_text_script(text, file_name):
    if USING_WINDOWS:
        text = text.replace("\n", "\r\n")
    with open(file_name, "w") as script_file:
        script_file.write(text)

