#include "stdlib/std.rbh"

#dynamic 0x800000
#org @main
lock
faceplayer
goto @pregunta

#org @pregunta
msgbox @msg_pregunta 5
compare LASTRESULT 1
if 0 goto @no
msgbox @respuesta_si 6
release
end

#org @no
msgbox @respuesta_no 6
goto @pregunta

#org @msg_pregunta
= ¿Quieres una hamburguesa?

#org @respuesta_no
= Pero que me dices!

#org @respuesta_si
= Yo también.
