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
# Documentation for writing this table was taken from Score_Under's
# pokedef.h

# perl -pe 's/#define CMD_(.*?)( *?)0x(..) \/\/(.*)/\t\"\L$1\": \{\"hex\": 0x\3,
# \"args\": (\"\4\")},/' to_convert.txt > args_to_add.txt



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
    "comparefarbytetovar": {"hex": 0x1E, "args": ("adress, var", (4, 2))},
    "comparefarbytetobyte": {"hex": 0x1F, "args": ("adress, byte", (4, 1))},
    "comparefarbytetofarbyte": {"hex": 0x20, "args": ("adress, address",
                                                      (4, 4))},
    "compare": {"hex": 0x21, "args": ("var, val", (2, 2))},
    "comparevars": {"hex": 0x22, "args": ("var, val", (2, 2))},
    "callasm": {"hex": 0x23, "args": ("address", (4,))},
    "callasm2": {"hex": 0x24, "args": ("address", (4,))},
    "special": {"hex": 0x25, "args": ("type", (2,))},
    "special2": {"hex": 0x26, "args": ("var, type", (2, 2))},
    "waitspecial": {"hex": 0x27},
    "pause": {"hex": 0x28, "args": ("time", (2,))},
    "setflag": {"hex": 0x29, "args": ("flag", (2,))},
    "clearflag": {"hex": 0x2A, "args": ("flag", (2,))},
    "checkflag": {"hex": 0x2B, "args": ("flag", (2,))},
    # 2 unknown commands TODO: Ask what's in XSE
    "resetvars": {"hex": 0x2E},
    "sound": {"hex": 0x2F, "args": ("id", (2,))},
    "cry": {"hex": 0x30, "args": ("bank, poke", (1, 2))},
    "fanfare": {"hex": 0x31, "args": ("sound", (2,))},
    "waitfanfare": {"hex": 0x32},
    "playsound": {"hex": 0x33, "args": ("sound", (2,))},
    "playsong": {"hex": 0x34, "args": ("song", (2,))},
    "fadedefault": {"hex": 0x35},
    "fadesong": {"hex": 0x36, "args": ("song", (2,))},
    "fadeout": {"hex": 0x37, "args": ("???", (1,))},
    "fadein": {"hex": 0x38, "args": ("???", (1,))},
    "warp": {"hex": 0x39, "args": ("bank, map, warp", (1, 1, 1))},
                            # TODO: FR
                            #supports additional x(2), y(2)
                            # (the same with all types of warps)
    "warpmutted": {"hex": 0x3A, "args": ("bank, map, warp", (1, 1, 1))},
    "warpwalking": {"hex": 0x3B, "args": ("bank, map, warp", (1, 1, 1))},
    "falldownhole": {"hex": 0x3C, "args": ("bank, map, warp", (1, 1, 1))},
    "warpteleport": {"hex": 0x3D, "args": ("bank, map, warp", (1, 1, 1))},
    "warp3": {"hex": 0x3E, "args": ("bank, map, warp", (1, 1, 1))},
    "warpelevator": {"hex": 0x3F, "args": ("bank, map, warp", (1, 1, 1))},
    "warp4": {"hex": 0x40, "args": ("bank, map, warp", (1, 1, 1))},
    "warp5": {"hex": 0x41, "args": ("bank, map, warp", (1, 1, 1))},
    "getplayerxy": {"hex": 0x42, "args": ("var, var", (2, 2))},
    "countpokemon": {"hex": 0x43},
    "additem": {"hex": 0x44, "args": ("item, num", (2, 2))},
    "removeitem": {"hex": 0x44, "args": ("item, num", (2, 2))},
    "checkitemspaceinbag": {"hex": 0x46, "args": ("item?, ???", (2, 2))},
    "checkitem": {"hex": 0x47, "args": ("item, num", (2, 2))},
    "checkitemtype": {"hex": 0x48, "args": ("item", (2,))},
    "giveitemtopc": {"hex": 0x49, "args": ("item, num", (2, 2))},
    "checkiteminpc": {"hex": 0x4A, "args": ("item, num", (2, 2))},
    "addfurniture": {"hex": 0x4B, "args": ("type", (2,))},
    "takefurniture": {"hex": 0x4C, "args": ("type", (2,))},
    "checkifroomforfurniture": {"hex": 0x4D, "args": ("type", (2,))},
    "checkfurniture": {"hex": 0x4E, "args": ("type", (2,))},
    "applymovement": {"hex": 0x4F, "args": ("minisprite, offset",
                                            (2, 4)),
                      "offset": (1, "movs")},
    "applymovementfinishat": {"hex": 0x50, "args": ("minisprite, offset"
                                                    "x, y",
                                                    (2, 4, 1, 1)),
                              "offset": (1, "movs")},
    "pauseevent": {"hex": 0x51, "args": ("minisprite", (2,))},
    # ?
    "disappear": {"hex": 0x53, "args": ("minisprite", (2,))},
    "disappearat": {"hex": 0x54, "args": ("minisprite, x, y", (2, 1, 1))},
    "reappear": {"hex": 0x55, "args": ("minisprite", (2,))},
    "reappearat": {"hex": 0x56, "args": ("minisprite, x, y", (2, 1, 1))},
    "movesprite": {"hex": 0x57, "args": ("id, x, y", (2, 2, 2))},
    "farreappear": {"hex": 0x58, "args": ("minisprite, bank, map", (2, 1, 1))},
    "fardisappear": {"hex": 0x59, "args": ("minisprite, bank, map", (2, 1, 1))},
    "faceplayer": {"hex": 0x5A},
    "spriteface": {"hex": 0x5B, "args": ("sprite, face", (2, 1))},
    "trainerbattle": {"hex": 0x5C, "args": ("kind, num, ?, startmsg, defeatmsg",
                                            (1, 2, 4, 4))},
    "lasttrainerbattle": {"hex": 0x5D},
    "endtrainerbattle": {"hex": 0x5E},
    "endtrainerbattle2": {"hex": 0x5F}, # TODO: Ask ASM guru difference
    "checktrainerflag": {"hex": 0x60, "args": ("flag", (2,))},
    "cleartrainerflag": {"hex": 0x61, "args": ("flag", (2,))},
    "settrainerflag": {"hex": 0x62, "args": ("flag", (2,))},
    # TODO: Ask ASM guru difference:
    "movesprite2": {"hex": 0x63, "args": ("id, x, y", (2, 2, 2))},
    "moveoffscreen": {"hex": 0x64, "args": ("sprite", (2))},
    "spritebehave": {"hex": 0x65, "args": ("sprite, type", (2, 1))},
    "showmsg": {"hex": 0x66},
    "message": {"hex": 0x67, "args": ("addr", (4,))},
    "closemsg": {"hex": 0x68},
    "lock": {"hex": 0x69},
    "lockall": {"hex": 0x6A},
    "release": {"hex": 0x6B},
    "releaseall": {"hex": 0x6C},
    "waitbutton": {"hex": 0x6D},
    "showyesno": {"hex": 0x6E, "args": ("x, y", (1, 1))},
    "multichoice": {"hex": 0x6F, "args": ("x, y, list, able to cancel",
                                          (1, 1, 1, 1))},
    "multichoice2": {"hex": 0x70, "args": ("x, y, list, defchoice",
                                          (1, 1, 1, 1))},
    "multichoice3": {"hex": 0x71, "args": ("x, y, list, per row, "
                                           "able to cancel",
                                          (1, 1, 1, 1))},
    "showbox": {"hex": 0x72, "args": ("x, y, w, h",
                                          (1, 1, 1, 1))},
    "hidebox": {"hex": 0x73, "args": ("x, y, w, h",
                                          (1, 1, 1, 1))},
    "clearbox": {"hex": 0x74, "args": ("x, y, w, h",
                                          (1, 1, 1, 1))},
    "showpokepic": {"hex": 0x75, "args": ("var, x, y", (2, 1, 1))},
    "hidepokepic": {"hex": 0x76},
    "picture": {"hex": 0x77, "args": ("num", (1,))},
    "braille": {"hex": 0x78, "args": ("addr", (4,))},
    "addpokemon": {"hex": 0x79, "args": ("poke, lvl, item, ??, ??, ??",
                                         (2, 1, 2, 1, 4, 4))},
    "giveegg": {"hex": 0x7a, "args": ("poke", (2,))},
    "setpokemonpp": {"hex": 0x7b, "args": ("pkmslot, atkslot, pp",
                                           (1, 1, 2))},
    "checkattack": {"hex": 0x7c, "args": ("attk", (2,))},
    "storepokemon": {"hex": 0x7d, "args": ("txt_var, poke", (1, 2))},
    "storefirstpokemon": {"hex": 0x7e, "args": ("txt_var", (1,))},
    "storepartypokemon": {"hex": 0x7f, "args": ("txt_var, pos", (1, 2))},
    "storeitem": {"hex": 0x80, "args": ("txt_var, itm", (1, 2))},
    "storefurniture": {"hex": 0x81, "args": ("txt_var, itm", (1, 2))},
    "storeattack": {"hex": 0x82, "args": ("txt_var, atk", (1, 2))},
    "storevar": {"hex": 0x83, "args": ("txt_var, var", (1, 2))},
    "storecomp": {"hex": 0x84, "args": ("txt_var, comp", (1, 2))},
    "storetext": {"hex": 0x85, "args": ("txt_var, txt", (1, 4))},
    "pokemart": {"hex": 0x86, "args": ("mart", (4,))},
    "pokemart2": {"hex": 0x87, "args": ("ptr", (4,))},
    "fakejumpstd": {"hex": 0x88, "args": ("type", (1,))}, # FR
    "pokemart3": {"hex": 0x88, "args": ("ptr", (4,))}, # RB
    "fakecallstd": {"hex": 0x89, "args": ("type", (1,))}, # FR
    "slotmachine": {"hex": 0x89, "args": ("??", (2,))}, # RB
    #"8a": {"hex": 0x8a, "args": ("?,?,t", (1, 1, 1))},
    "choosecontestpokemon": {"hex": 0x8b},
    "startcontest": {"hex": 0x8c},
    "startwireless": {"hex": 0x8e}, # emerald only
    "random": {"hex": 0x8F, "args": ("max?", (2,))},
    "givemoney": {"hex": 0x90, "args": ("amt, ???", (4, 1))},
    "paymoney": {"hex": 0x91, "args": ("amt, ???", (4, 1))},
    "checkmoney": {"hex": 0x92, "args": ("amt, ???", (4, 1))},
    "showmoney": {"hex": 0x93, "args": ("x, y, ???", (1,1,1))},
    "hidemoney": {"hex": 0x94, "args": ("x, y", (1, 1))},
    "updatemoney": {"hex": 0x95, "args": ("?, ?, ?", (1, 1, 1))},
    # 0x96
    "fadescreen": {"hex": 0x97, "args": ("blank", (1,))},
    "fadescreendelay": {"hex": 0x98, "args": ("blank, delay", (1, 1))},
    "darkenroom": {"hex": 0x99, "args": ("size", (2,))},
    "lightroom": {"hex": 0x9a, "args": ("size", (1,))},
    "msgbox2": {"hex": 0x9b, "args": ("ptr", (4,))},
    "doanimation": {"hex": 0x9c, "args": ("?", (2,))},
    "setanimation": {"hex": 0x9d, "args": ("?, ?", (1, 2))},
    "checkanimation": {"hex": 0x9e, "args": ("?", (2,))},
    "sethealingplace": {"hex": 0x9f, "args": ("place", (2,))},
    "checkgender": {"hex": 0xa0},
    "cryfr": {"hex": 0xa1, "args": ("?, )", (2, 1))},
    "setmaptile": {"hex": 0xa2, "args": ("x, y, tile, attr", (2, 2, 2, 2))},
    "resetweather": {"hex": 0xa3},
    "setweather": {"hex": 0xa4, "args": ("weather", (1,))},
    "doweather": {"hex": 0xa5},
    "a6": {"hex": 0xa6, "args": ("?", (1,))},
    "setmapfooter": {"hex": 0xa7, "args": ("?", (2,))},
    "increasespritelevel": {"hex": 0xa8, "args": ("id, bank, map, ?",
                                                  (2, 1, 1, 1))},
    "resetspritelevel": {"hex": 0xa9, "args": ("id, bank, map", (2, 1, 1))},
    "createtempsprite": {"hex": 0xaa, "args":
                      ("spr, id, x, y, behave, dir",
                       (1, 1, 2, 2, 1, 1))},
    "tempspriteface": {"hex": 0xab, "args": ("id, dir", (1, 1))},
    "setdooropened": {"hex": 0xac, "args": ("?, ?", (2, 2))},
    "setdoorclosed": {"hex": 0xad, "args": ("?, ?", (2, 2))},
    "doorchange": {"hex": 0xae},
    "setdooropenedstatic": {"hex": 0xaf, "args": ("?, ?", (2, 2))},
    "setdoorclosedstatic": {"hex": 0xb0, "args": ("?, ?", (2, 2))},
    #"b1": {"hex": 0xb1, "args": ("?, ?", (1, 1, 2, 2))},
    #"b2": {"hex": 0xb2, "args": ("?,?, ")},
    "coincasetovar": {"hex": 0xb3, "args": ("var", (2,))},
    "givetocoincase": {"hex": 0xb4, "args": ("coins", (2,))},
    "takefromcoincase": {"hex": 0xb5, "args": ("coins", (2,))},
    "battle": {"hex": 0xb6, "args": ("poke, lvl, item", (2, 1, 2))},
    "lastbattle": {"hex": 0xb7},
    "showcoins": {"hex": 0xc0, "args": ("x, y", (1, 1))},
    "hidecoins": {"hex": 0xc1, "args": ("x, y", (1, 1))},
    "updatecoins": {"hex": 0xc2, "args": ("x, y", (1, 1))},
    "c3": {"hex": 0xc3, "args": ("??", (1,))},
    "warp6": {"hex": 0xc4, "args": ("bnk, map, ext, x, y",
                                    (1, 1, 1, 2, 2))},
    "waitcry": {"hex": 0xc5},
    #"storeboxname": {"hex": 0xc6, "args": ("\v\hxx(1) boxno(2)")},
    "storeboxname": {"hex": 0xc6, "args": ("buf, boxno", (1, 2))},
    "textcolor": {"hex": 0xc7, "args": ("colour", (1,))},
    "msgboxsign": {"hex": 0xca},
    "msgboxnormal": {"hex": 0xcb},
    "comparehiddenvar": {"hex": 0xcc, "args": ("var, val", (1, 2))},
    "setobedience": {"hex": 0xcd, "args": ("id", (2,))},
    "checkobedience": {"hex": 0xce, "args": ("id", (2,))},
    "executeram": {"hex": 0xcf},
    "setworldmapflag": {"hex": 0xd0, "args": ("flag(2)")},
    "warpteleport2": {"hex": 0xd1, "args": ("bnk, map, ext, x, y",
                                    (1, 1, 1, 2, 2))},
    "setcatchlocation": {"hex": 0xd2, "args": ("id, loc", (2, 1))},
    #"d3": {"hex": 0xd3, "args": ("braille", (4,))},
    "storeitems": {"hex": 0xd4, "args": ("?, id, amt", (1, 2, 2))},
    #"fb": {"hex": 0xfb, "args": ("addr", (4))},
    #"fe": {"hex": 0xfe, "args": ("?", (1,))},

    }

# Alias:normal_name
aliases = {"waitmovement": "pauseevent",
           "givepokemon": "addpokemon",
           "#dynamic": "#dyn",
           "goto": "jump",
           "nop": "nop0"}

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
