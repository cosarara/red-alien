#include "stdlib/std.rbh"
#include "stdlib/stdpoke.rbh"

#dynamic 0x740000
#org @main
lock
faceplayer
checkflag 0x200
if 0x1 jump @haveit
message @want
callstd MSG_YESNO
if 0x1 jump @pushedyes
jump @pushedno

#org @haveit
message @howsit
callstd MSG_NORMAL
release
end

#org @pushedyes
setflag 0x200
giveegg PKMN_PICHU
message @herego
callstd MSG_NORMAL
release
end

#org @pushedno
message @dontwant
callstd MSG_NORMAL
release
end

#org @want
= Hey, do you want this Pichu egg?

#org @herego
= Here you go!\nPlease raise it well.

#org @howsit
= I hope Pichu is doing well!

#org @dontwant
= Oh, ok. Maybe someone else will take it.
