#include "stdlib/std.rbh"

#dynamic 0x800000

#org @start
lock
faceplayer
checkflag 0x200
if 0x1 goto @done
msgbox @1 0x6
setflag 0x200
release
end

#org @done
msgbox @2 0x6
clearflag 0x200
release
end

#org @1
= sup1

#org @2
= sup2
