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


# Format:
# pkcommands = {
#        [[["<command_name>": {["hex":"<hex value>"],
#                           ["args": ("<description>",
#                            (<arg> [[[arg], arg], ...] ))]},
#        ...], ...]}
#

pkcommands = {
    # "fake" commands (commands without hex translation)
    "#org": {"args": ("offset", (4,))},
    "=": {"args": ("text", ("*",))},
    "#dyn": {"args": ("offset", (4,))},
    "#raw": {"args": ("hex byte", (1,))},
    "if": {"args": ("comp, command, offset", (1, 1, 4))},
    "softend": {}, # An end with doesn't compile to end
    # "Real" commands
    "nop0": {"hex": 0x00},
    "nop1": {"hex": 0x01},
    "end": {"hex": 0x02},
    "return": {"hex": 0x03},
    "call": {"hex": 0x04, "args": ("adress", (4,)),
               "offset": (0, "script")},
    "jump": {"hex": 0x05, "args": ("adress", (4,)),
               "offset": (0, "script")},
    "jumpif": {"hex": 0x06, "args": ("ops, adress", (1, 4)),
               "offset": (1, "script")},
    "callif": {"hex": 0x07, "args": ("ops, adress", (1, 4)),
               "offset": (1, "script")},
    "jumpstd": {"hex": 0x08, "args": ("type", (1,))},
    "callstd": {"hex": 0x09, "args": ("type", (1,))},
    "jumpstdif": {"hex": 0x0A, "args": ("ops, type", (1, 1))},
    "callstdif": {"hex": 0x0B, "args": ("ops, type", (1, 1))},
    "jumpram": {"hex": 0x0C},
    "killscript": {"hex": 0x0E},
    "setbyte": {"hex": 0x0D, "args": ("byte", (1,))},
    "msgbox": {"hex": 0x0F, "args": ("offset", (4,), b"\x00"),
               "offset": (0, "text")},
    "setbyte2": {"hex": 0x10, "args": ("bank, byte", (1, 1))},
    "writebytetooffset": {"hex": 0x11, "args": ("byte, adress", (1, 4))},
    "loadbytefrompointer": {"hex": 0x12, "args": ("byte, adress", (1, 4))},
    "setfarbyte": {"hex": 0x13, "args": ("byte, adress", (1, 4))},
    "copyscriptbanks": {"hex": 0x14, "args": ("bank, bank", (1, 1))},
    "copybyte": {"hex": 0x15, "args": ("adress, adress", (4, 4))},
    "setvar": {"hex": 0x16, "args": ("var, value", (2, 2))},
    "addvar": {"hex": 0x17, "args": ("var, value", (2, 2))},
    "subtractvar": {"hex": 0x18, "args": ("var, value", (2, 2))},
    "copyvar": {"hex": 0x19, "args": ("var, var", (2, 2))},
    "copyvarifnotzero": {"hex": 0x1A, "args": ("var, var", (2, 2))},
    "comparebuffers": {"hex": 0x1B, "args": ("buffer, buffer", (2, 2))},
    "comparevartobyte": {"hex": 0x1C, "args": ("var, byte", (2, 1))},
    "comparevartofarbyte": {"hex": 0x1D, "args": ("var, adress", (2, 4))},
    # TODO: Afegir tots els que falten
    # ...
    "compare": {"hex": 0x21, "args": ("var, val", (2, 2))},
    "comparevars": {"hex": 0x22, "args": ("var, val", (2, 2))},
    "callasm": {"hex": 0x23, "args": ("address", (4,))},
    "callasm2": {"hex": 0x24, "args": ("address", (4,))},
    "special": {"hex": 0x25, "args": ("type", (2,))},
    "special2": {"hex": 0x26, "args": ("var, type", (2, 2))},
    # ...
    "applymovement": {"hex": 0x4F, "args": ("minisprite, offset",
                                            (2, 4)),
                      "offset": (1, "movs")},
    "pause": {"hex": 0x28, "args": ("time", (2,))},
    "pauseevent": {"hex": 0x51, "args": ("minisprite", (2,))},
    # ?
    "disappear": {"hex": 0x53, "args": ("minisprite", (2,))},
    # ...
    "reappear": {"hex": 0x55, "args": ("minisprite", (2,))},
    # ...
    "faceplayer": {"hex": 0x5A},
    # ...
    "lockall": {"hex": 0x69},
    "lock": {"hex": 0x6A},
    "release": {"hex": 0x6B},
    "releaseall": {"hex": 0x6C},
    # ...
    "addpokemon": {"hex": 0x79, "args": ("poke, lvl, item, ??, ??, ??",
                                         (2, 1, 2, 1, 4, 4))},
    # ...
    "storevar": {"hex": 0x83, "args": ("text_var, var", (1, 2))},
    # ...
    "random": {"hex": 0x8F, "args": ("max?", (2,))}
    }

# Alias:normal_name
aliases = {"waitmovement": "pauseevent",
           "givepokemon": "addpokemon",
           "#dynamic": "#dyn",
           "goto": "jump"}

pkcommands_and_aliases = pkcommands
for alias in aliases:
    normal_name = aliases[alias]
    pkcommands_and_aliases[alias] = pkcommands[normal_name]

#print pkcommands_and_aliases

# We just need the name, because then we use it to get the rest of
# information from the other function

#dec_pkcommands = {
#        "02": "end",
#        "0F": "msgbox",
#        "09": "callstd",
#        "4F": "applymovement",
#        "28": "pause",
#        "51": "pauseevent"
#        }

dec_pkcommands = {}

for command in pkcommands:
#    print command
    if "hex" in pkcommands[command]:
#        print pkcommands[command]["hex"]
        dec_pkcommands[pkcommands[command]["hex"]] = command

#print dec_pkcommands

pkcommands = pkcommands_and_aliases
