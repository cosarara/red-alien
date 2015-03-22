#define LASTRESULT 0x8000
#dynamic 0x800000
#org @main
lock
faceplayer
:pregunta
msgbox @msg_pregunta 5
compare LASTRESULT 1
if 1 goto :yes
msgbox @respuesta_no 6
goto :pregunta
:yes
msgbox @respuesta_si 6
release
end

#org @msg_pregunta
= ¿Quieres una hamburguesa?

#org @respuesta_no
= ¿¡Pero que me dices!?

#org @respuesta_si
= Yo también.
