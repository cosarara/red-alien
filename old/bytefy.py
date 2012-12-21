# -*- coding: utf-8 *-*

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

"""module to work with hex byte strings"""


def num_to_bytes(numstr):
    if len(numstr) % 2 == 1:
        numstr = "0" + numstr
    return numstr


def permutate(bytes):
    if len(bytes) > 8:  # 32bits = 4 bytes = 4 hex digits
        print("ERROR: Too many bytes for a 32 bit int")
        return
    bytes_rev = ""
    for i in range(len(bytes) // 2):
        pos = i * 2
        bytes_rev = bytes[pos:pos + 2] + bytes_rev
    #print bytes_rev
    return bytes_rev


def bytes_to_num(bytes):
    if bytes != "0":
#        numstr = bytes.lstrip("0")
        numstr = bytes
    else:
        numstr = bytes
    return numstr
