' Test script - copyright cosarara97
' Licenced under the WTFPL
#define MAL1 4
#define MAL2 5
#define MON 6
#define BOTIGUER 1
#define NEN 2
#define NENA 3

#define CAMERA 0x7F
#define PLAYER 0xFF

#define CAMERA_START 0x113
#define CAMERA_END 0x114

#dyn 0x800000

#org @main
lockall
faceplayer
msgbox @msg_nena_1 'bla bla bla
callstd 6
' entren els chungos
special CAMERA_START
applymovement CAMERA @mov_camera_1
pauseevent 0
special CAMERA_END
reappear MAL1
applymovement MAL1 @mov_mal_1_1 ' hide walk_right walk_up end
pauseevent MAL1
applymovement MAL1 @show
pauseevent MAL1
applymovement MAL1 @mov_mal_1_2 ' walk_up walk_up walk_up end
pauseevent MAL1
reappear MAL2
applymovement MAL2 @mov_mal_2 ' hide walk_right walk_right walk_up end
pauseevent MAL2
applymovement MAL2 @show
'reappear MAL2
applymovement PLAYER @mov_exclamacio    ' !
applymovement BOTIGUER @mov_exclamacio    ' !
applymovement NEN @mov_exclamacio    ' !
applymovement NENA @mov_exclamacio    ' !
pauseevent PLAYER
pauseevent NENA
applymovement PLAYER @mov_look_left
applymovement NENA @mov_look_left
applymovement MAL1 @mov_jump_in_place_down
msgbox @msg_mal_1 'Desconocido 1: Esto es un puto atraco y asdf
callstd 6
reappear MON ' Surt el monstruo
msgbox @msg_monstruo_1 ' grawr
callstd 6
' TODO: Posar crit monstre
msgbox @msg_nena_2 ' AAAAAAAH!
callstd 6
applymovement MON @mov_mon_1
pauseevent MON
applymovement NENA @mov_look_down
pauseevent NENA
msgbox @msg_nena_2 ' AAAAAAAH!
callstd 6
applymovement MAL2 @mov_jump_in_place_right
pauseevent MAL2
msgbox @msg_mal_2 ' Calla, nena
callstd 6
pauseevent 0
msgbox @msg_monstruo_2 ' grrrr
callstd 6
applymovement MAL1 @mov_mal_3
msgbox @msg_mal_3 ' la pasta!, no us mogueu i que puc fer
callstd 6
pauseevent 0
special CAMERA_START
applymovement CAMERA @mov_camera_2
pauseevent 0
special CAMERA_END
releaseall
end

#org @msg_nena_1
= \c\h01\h08Laura: Eh, \v\h01!\pCuanto tiempo, no?\nQu\h1B est\h17s haciendo aqu\h20?\c\h01\h05\p\v\h01: Pues mira,\nresulta que estoy...
'= Laura: Eh, \v\h01!\pCuanto tiempo, no?\nQué estás haciendo aquí?\p\v\h01: Pues mira,\nresulta que estoy...

#org @msg_mal_1
= \c\h01\h06Desconocido 1: Esto es un\nputo atraco, joder, que estoy\lto' loco!\pQue nadie se mueva o le mato!

#org @msg_monstruo_1
= \c\h01\h06Animal raro: Groaaaawrrrr!

#org @msg_nena_2
= \c\h01\h08Laura: AAAAAAAh! Socorroooo!

#org @msg_mal_2
= \c\h01\h06Atracador 1: C\h17llate, ni\h29ata,\ny no te pasar\h17 nada...
'= Desconocido 1: Cállate, niñata,\ny no te pasará nada...

#org @msg_monstruo_2
= \c\h01\h06Grrrrr...

#org @msg_mal_3
= \c\h01\h06Atracador 1: La pasta,\nr\h17pido!\pAtracador 2: Que a nadie\nse le ocurra moverse!\p\c\h01\h05-piensa-: Oh, mierda, qu\h1B\nvoy a hacer?
'= Desconocido 1: La pasta,\nrápido!\pAtracador 2: Que a nadie\nse le ocurra moverse!\p(piensa): Oh, mierda, qué\nvoy a hacer?

#org @mov_mal_1_1
#raw 0x60 'hide
#raw 0x13 ' Step Right (Normal)
#raw 0x11 ' Step Up (Normal)
#raw 0xFE 'End

#org @mov_mal_1_2
#raw 0x11 ' Step Up (Normal)
#raw 0x11 ' Step Up (Normal)
#raw 0x11 ' Step Up (Normal)
#raw 0x11 ' Step Up (Normal)
#raw 0x0 'Mirar abajo
#raw 0xFE 'End

#org @mov_mal_2
#raw 0x60 'hide
#raw 0x13 ' Step Right (Normal)
#raw 0x13 ' Step Right (Normal)
#raw 0x11 ' Step Up (Normal)
#raw 0xFE 'End

#org @mov_exclamacio
#raw 0x62 ' '!' box popup
#raw 0xFE 'End

#org @mov_mon_1
#raw 0x20 ' Step Right (Fast)
#raw 0x1D ' Step Down (Fast)
#raw 0x1D ' Step Down (Fast)
#raw 0x20 ' Step Right (Fast)
#raw 0x20 ' Step Right (Fast)
#raw 0x17 ' Jump Right 2 Squares
#raw 0x01 ' Face Up
#raw 0xFE 'End


#org @mov_camera_1
#raw 0x1D ' Step Down (Fast)
#raw 0x1D ' Step Down (Fast)
#raw 0x1F ' Step Left (Fast)
#raw 0xFE 'End

#org @mov_camera_2
#raw 0x1E ' Step Up (Fast)
#raw 0x1E ' Step Up (Fast)
#raw 0x20 ' Step Right (Fast)
#raw 0xFE 'End

#org @show
#raw 0x61
#raw 0xFE

#org @mov_mal_3
#raw 0x2 'Mirar izquierda
#raw 0xFE 'End

#org @mov_look_down
#raw 0x00 ' Face Down
#raw 0xFE 'End

#org @mov_look_left
#raw 0x02 ' Face Left
#raw 0xFE 'End

#org @mov_look_right
#raw 0x03 ' Face Right
#raw 0xFE 'End

#org @mov_jump_in_place_left
#raw 0x02 ' Face Left
#raw 0x54 ' Jump in Place (Facing Left)
#raw 0xFE 'End

#org @mov_jump_in_place_right
#raw 0x03 ' Face Right
#raw 0x55 ' Jump in Place (Facing Right)
#raw 0xFE 'End

#org @mov_jump_in_place_down
#raw 0x00 ' Face Down
#raw 0x52 ' Jump in Place (Facing Down)
#raw 0xFE 'End




