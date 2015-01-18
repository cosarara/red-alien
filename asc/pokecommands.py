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

import sys
import os
import pkgutil


if getattr(sys, 'frozen', False):
    path = os.path.join(
            os.path.dirname(sys.executable),
            "asc", "data", "commands.txt")
    with open(path, encoding="utf8") as f:
        commands_str = f.read()
else:
    data = pkgutil.get_data('asc', os.path.join('data', 'commands.txt'))
    commands_str = data.decode("utf8")

exec(commands_str)

pkcommands_and_aliases = pkcommands.copy()
for alias in aliases:
    normal_name = aliases[alias]
    pkcommands_and_aliases[alias] = pkcommands[normal_name]

dec_pkcommands = {}

for command in pkcommands:
    if "hex" in pkcommands[command]:
        dec_pkcommands[pkcommands[command]["hex"]] = command

pkcommands = pkcommands_and_aliases
