'board:
' -> vars:
'    0x4001    0x4002    0x4003
'    0x4004    0x4005    0x4006
'    0x4007    0x4008    0x4009

'board2:
' -> vars:
'    0x4011    0x4012    0x4013
'    0x4014    0x4015    0x4016
'    0x4017    0x4018    0x4019

#define index1 0x4025
    
'player = 1  - look right
'pc = 2      - look left

#define user_winning 0x4020
#define pc_winning 0x4021
'someone_winning = 0x4024
'pc_pos = 0x4022 ' TODO: Buscar la manera d'aconseguir un numero de var a partir del valor d'una altra
              ' Sinó, farem servir un munt d'if's
'win = 0x4023

#define LASTRESULT 0x800D

#dyn 0x800000

' Minis (fitxes)
'------------------------------------------------------------------------------
#org @fitxa1
compare 0x4001 0
if != jump @quit
setvar 0x4001 1
jump @main

#org @fitxa2
compare 0x4002 0
if != jump @quit
setvar 0x4002 1
jump @main

#org @fitxa3
compare 0x4003 0
if != jump @quit
setvar 0x4003 1
jump @main

#org @fitxa4
compare 0x4004 0
if != jump @quit
setvar 0x4004 1
jump @main

#org @fitxa5
compare 0x4005 0
if != jump @quit
setvar 0x4005 1
jump @main

#org @fitxa6
compare 0x4006 0
if != jump @quit
setvar 0x4006 1
jump @main

#org @fitxa7
compare 0x4007 0
if != jump @quit
setvar 0x4007 1
jump @main

#org @fitxa8
compare 0x4008 0
if != jump @quit
setvar 0x4008 1
jump @main

#org @fitxa9
compare 0x4009 0
if != jump @quit
setvar 0x4009 1
jump @main


' Main
'------------------------------------------------------------------------------
#org @main
'msgbox @debug1
'callstd 6
jump @check_win_player


' Debug_messages
'------------------------------------------------------------------------------
#org @debug1
= lalalalala

#org @debug2
= lololololol

#org @debug3
= \v\h02

#org @byemsg
= Bye!

#org @debug4
= Dau dolent!

#org @debug5
= PC trying to move

#org @debug6
= Block!

' Binds
'------------------------------------------------------------------------------
#org @check_win_player
jump @win

#org @check_win_pc
'msgbox @debug2
'callstd 6
jump @winpc


#org @check_tie
compare 0x4001 0
if == jump @get_pc_pos
compare 0x4002 0
if == jump @get_pc_pos
compare 0x4003 0
if == jump @get_pc_pos
compare 0x4004 0
if == jump @get_pc_pos
compare 0x4005 0
if == jump @get_pc_pos
compare 0x4006 0
if == jump @get_pc_pos
compare 0x4007 0
if == jump @get_pc_pos
compare 0x4008 0
if == jump @get_pc_pos
compare 0x4009 0
if == jump @get_pc_pos
msgbox @tie
callstd 6
jump @apply


#org @tie
= Tie!

' PC' moves functions
'------------------------------------------------------------------------------
#org @get_pc_pos
'call @check_tie
random 9
storevar 0 LASTRESULT
'msgbox @debug3
'callstd 6
copyvar 0x4022 LASTRESULT
compare 0x4022 0
if == jump @get_pc_pos
jump @move_pc
'move(a, pc_pos)
'print_list(a)
'jump @check_end

#org @move_pc
'msgbox @debug5
'callstd 6
compare 0x4022 1
if == jump @move_pc_1
compare 0x4022 2
if == jump @move_pc_2
compare 0x4022 3
if == jump @move_pc_3
compare 0x4022 4
if == jump @move_pc_4
compare 0x4022 5
if == jump @move_pc_5
compare 0x4022 6
if == jump @move_pc_6
compare 0x4022 7
if == jump @move_pc_7
compare 0x4022 8
if == jump @move_pc_8
compare 0x4022 9
if == jump @move_pc_9
'msgbox @debug4
'callstd 6
'jump @quit
end

#org @move_pc_1
compare 0x4001 0
if != jump @get_pc_pos
setvar 0x4001 2
jump @play4
'jump @apply

#org @move_pc_2
compare 0x4002 0
if != jump @get_pc_pos
setvar 0x4002 2
jump @play4
'jump @apply

#org @move_pc_3
compare 0x4003 0
if != jump @get_pc_pos
setvar 0x4003 2
jump @play4
'jump @apply

#org @move_pc_4
compare 0x4004 0
if != jump @get_pc_pos
setvar 0x4004 2
jump @play4
'jump @apply

#org @move_pc_5
compare 0x4005 0
if != jump @get_pc_pos
setvar 0x4005 2
jump @play4
'jump @apply

#org @move_pc_6
compare 0x4006 0
if != jump @get_pc_pos
setvar 0x4006 2
jump @play4
'jump @apply

#org @move_pc_7
compare 0x4007 0
if != jump @get_pc_pos
setvar 0x4007 2
jump @play4
'jump @apply

#org @move_pc_8
compare 0x4008 0
if != jump @get_pc_pos
setvar 0x4008 2
jump @play4
'jump @apply

#org @move_pc_9
compare 0x4009 0
if != jump @get_pc_pos
setvar 0x4009 2
jump @play4
'jump @apply


' Apply movements
'------------------------------------------------------------------------------
#org @apply
'msgbox @debug2
'callstd 6
compare 0x4001 1
if == call @apply_1_1
if > call @apply_1_2
compare 0x4002 1
if == call @apply_2_1
if > call @apply_2_2
compare 0x4003 1
if == call @apply_3_1
if > call @apply_3_2
compare 0x4004 1
if == call @apply_4_1
if > call @apply_4_2
compare 0x4005 1
if == call @apply_5_1
if > call @apply_5_2
compare 0x4006 1
if == call @apply_6_1
if > call @apply_6_2
compare 0x4007 1
if == call @apply_7_1
if > call @apply_7_2
compare 0x4008 1
if == call @apply_8_1
if > call @apply_8_2
compare 0x4009 1
if == call @apply_9_1
if > call @apply_9_2
'jump @quit
end

#org @apply_1_1
applymovement 1 @l_r
waitmovement 0x0
return

#org @apply_2_1
applymovement 2 @l_r
waitmovement 0x0
return

#org @apply_3_1
applymovement 3 @l_r
waitmovement 0x0
return

#org @apply_4_1
applymovement 4 @l_r
waitmovement 0x0
return

#org @apply_5_1
applymovement 5 @l_r
waitmovement 0x0
return

#org @apply_6_1
applymovement 6 @l_r
waitmovement 0x0
return

#org @apply_7_1
applymovement 7 @l_r
waitmovement 0x0
return

#org @apply_8_1
applymovement 8 @l_r
waitmovement 0x0
return

#org @apply_9_1
applymovement 9 @l_r
waitmovement 0x0
return

#org @apply_1_2
applymovement 1 @l_d
waitmovement 0x0
return

#org @apply_2_2
applymovement 2 @l_d
waitmovement 0x0
return

#org @apply_3_2
applymovement 3 @l_d
waitmovement 0x0
return

#org @apply_4_2
applymovement 4 @l_d
waitmovement 0x0
return

#org @apply_5_2
applymovement 5 @l_d
waitmovement 0x0
return

#org @apply_6_2
applymovement 6 @l_d
waitmovement 0x0
return

#org @apply_7_2
applymovement 7 @l_d
waitmovement 0x0
return

#org @apply_8_2
applymovement 8 @l_d
waitmovement 0x0
return

#org @apply_9_2
applymovement 9 @l_d
waitmovement 0x0
return

#org @l_r
#raw 0x03 ' Face Right
#raw 0xFE 'End
'M look_right end

#org @l_d
#raw 0x01 ' Face Up
#raw 0xFE 'End
'M look_left end

' We come here after setting the appropiate var for moving player's and checking
' if he won
#org @play
jump @check_about_to_win_pc

#org @play2
jump @check_about_to_win_player

#org @play3
'jump @get_pc_pos
jump @check_tie

#org @play4
jump @check_win_pc

#org @play5
jump @apply

#org @reset_temp_board
copyvar 0x4011 0x4001
copyvar 0x4012 0x4002
copyvar 0x4013 0x4003
copyvar 0x4014 0x4004
copyvar 0x4015 0x4005
copyvar 0x4016 0x4006
copyvar 0x4017 0x4007
copyvar 0x4018 0x4008
copyvar 0x4019 0x4009
return

#org @check_about_to_win_pc
'setvar index1 1
call @reset_temp_board
setvar 0x4011 0x2  ' posem la primera, comprovem, la segona, comprovem, etc.
                   ' TODO: If en la real == 1, saltar a la següent
setvar index1 0x2
compare 0x4002 0
if != jump @next
'msgbox @debug1
'callstd 6
jump @twinpc

#org @check_about_to_win_pc2
call @reset_temp_board
setvar 0x4012 0x2
setvar index1 0x3
compare 0x4002 0
if != jump @next
'msgbox @debug1
'callstd 6
jump @twinpc

#org @check_about_to_win_pc3
call @reset_temp_board
setvar 0x4013 0x2
setvar index1 0x4
compare 0x4003 0
if != jump @next
'msgbox @debug1
'callstd 6
jump @twinpc

#org @check_about_to_win_pc4
call @reset_temp_board
setvar 0x4014 0x2
setvar index1 0x5
compare 0x4004 0
if != jump @next
'msgbox @debug1
'callstd 6
jump @twinpc

#org @check_about_to_win_pc5
call @reset_temp_board
setvar 0x4015 0x2
setvar index1 0x6
compare 0x4005 0
if != jump @next
'msgbox @debug1
'callstd 6
jump @twinpc

#org @check_about_to_win_pc6
call @reset_temp_board
setvar 0x4016 0x2
setvar index1 0x7
compare 0x4006 0
if != jump @next
'msgbox @debug1
'callstd 6
jump @twinpc

#org @check_about_to_win_pc7
call @reset_temp_board
setvar 0x4017 0x2
setvar index1 0x8
compare 0x4007 0
if != jump @next
'msgbox @debug1
'callstd 6
jump @twinpc

#org @check_about_to_win_pc8
call @reset_temp_board
setvar 0x4018 0x2
setvar index1 0x9
compare 0x4008 0
if != jump @next
'msgbox @debug1
'callstd 6
jump @twinpc

#org @check_about_to_win_pc9
call @reset_temp_board
setvar 0x4019 0x2
setvar index1 0xA
compare 0x4009 0
if != jump @next
'msgbox @debug1
'callstd 6
jump @twinpc

#org @next
'storevar 0 index1
'msgbox @debug3
'callstd 6
compare index1 2
if == jump @check_about_to_win_pc2
compare index1 3
if == jump @check_about_to_win_pc3
compare index1 4
if == jump @check_about_to_win_pc4
compare index1 5
if == jump @check_about_to_win_pc5
compare index1 6
if == jump @check_about_to_win_pc6
compare index1 7
if == jump @check_about_to_win_pc7
compare index1 8
if == jump @check_about_to_win_pc8
compare index1 9
if == jump @check_about_to_win_pc9
compare index1 10
if == jump @play2
jump @play2

#org @check_about_to_win_player
'setvar index1 1
'msgbox @debug1
'callstd 6
call @reset_temp_board
setvar 0x4011 1
setvar index1 0x2
compare 0x4001 0
if != jump @next_player
'msgbox @debug2
'callstd 6
jump @twinplayer

#org @check_about_to_win_player2
call @reset_temp_board
setvar 0x4012 1
setvar index1 0x3
compare 0x4002 0
if != jump @next_player
'msgbox @debug2
'callstd 6
jump @twinplayer

#org @check_about_to_win_player3
call @reset_temp_board
setvar 0x4013 1
setvar index1 0x4
compare 0x4003 0
if != jump @next_player
'msgbox @debug2
'callstd 6
jump @twinplayer

#org @check_about_to_win_player4
call @reset_temp_board
setvar 0x4014 1
setvar index1 0x5
compare 0x4004 0
if != jump @next_player
'msgbox @debug2
'callstd 6
jump @twinplayer

#org @check_about_to_win_player5
call @reset_temp_board
setvar 0x4015 1
setvar index1 0x6
compare 0x4005 0
if != jump @next_player
'msgbox @debug2
'callstd 6
jump @twinplayer

#org @check_about_to_win_player6
call @reset_temp_board
setvar 0x4016 1
setvar index1 0x7
compare 0x4006 0
if != jump @next_player
'msgbox @debug2
'callstd 6
jump @twinplayer

#org @check_about_to_win_player7
call @reset_temp_board
setvar 0x4017 1
setvar index1 0x8
compare 0x4007 0
if != jump @next_player
'msgbox @debug2
'callstd 6
jump @twinplayer

#org @check_about_to_win_player8
call @reset_temp_board
setvar 0x4018 1
setvar index1 0x9
compare 0x4008 0
if != jump @next_player
'msgbox @debug2
'callstd 6
jump @twinplayer

#org @check_about_to_win_player9
call @reset_temp_board
setvar 0x4019 1
setvar index1 0xA
compare 0x4009 0
if != jump @next_player
'msgbox @debug2
'callstd 6
jump @twinplayer

#org @next_player
'storevar 0 index1
'msgbox @debug3
'callstd 6
compare index1 2
if == jump @check_about_to_win_player2
compare index1 3
if == jump @check_about_to_win_player3
compare index1 4
if == jump @check_about_to_win_player4
compare index1 5
if == jump @check_about_to_win_player5
compare index1 6
if == jump @check_about_to_win_player6
compare index1 7
if == jump @check_about_to_win_player7
compare index1 8
if == jump @check_about_to_win_player8
compare index1 9
if == jump @check_about_to_win_player9
compare index1 10
if == jump @play3
jump @play3

#org @apply_tmp
'msgbox @debug1
'callstd 6
copyvar 0x4001 0x4011
'storevar 0 0x4001
'msgbox @debug3
'callstd 6
copyvar 0x4002 0x4012
'storevar 0 0x4001
'msgbox @debug3
'callstd 6
copyvar 0x4003 0x4013
'storevar 0 0x4001
'msgbox @debug3
'callstd 6
copyvar 0x4004 0x4014
'storevar 0 0x4001
'msgbox @debug3
'callstd 6
copyvar 0x4005 0x4015
'storevar 0 0x4001
'msgbox @debug3
'callstd 6
copyvar 0x4006 0x4016
'storevar 0 0x4001
'msgbox @debug3
'callstd 6
copyvar 0x4007 0x4017
'storevar 0 0x4001
'msgbox @debug3
'callstd 6
copyvar 0x4008 0x4018
'storevar 0 0x4001
'msgbox @debug3
'callstd 6
copyvar 0x4009 0x4019
'storevar 0 0x4001
'msgbox @debug3
'callstd 6
jump @end_pc_won

#org @block
'msgbox @debug6
'callstd 6
'storevar 0 0x4003
'msgbox @debug3
'callstd 6
'storevar 0 0x4013
'msgbox @debug3
'callstd 6
comparevars 0x4001 0x4011
if != jump @block_1
comparevars 0x4002 0x4012
if != jump @block_2
comparevars 0x4003 0x4013
if != jump @block_3
comparevars 0x4004 0x4014
if != jump @block_4
comparevars 0x4005 0x4015
if != jump @block_5
comparevars 0x4006 0x4016
if != jump @block_6
comparevars 0x4007 0x4017
if != jump @block_7
comparevars 0x4008 0x4018
if != jump @block_8
comparevars 0x4009 0x4019
if != jump @block_9
'msgbox @debug1
'callstd 6
end

#org @block_1
'msgbox @debug1
'callstd 6
setvar 0x4001 2
jump @check_win_pc

#org @block_2
setvar 0x4002 2
jump @check_win_pc

#org @block_3
setvar 0x4003 2
jump @check_win_pc

#org @block_4
setvar 0x4004 2
jump @check_win_pc

#org @block_5
setvar 0x4005 2
jump @check_win_pc

#org @block_6
setvar 0x4006 2
jump @check_win_pc

#org @block_7
setvar 0x4007 2
jump @check_win_pc

#org @block_8
setvar 0x4008 2
jump @check_win_pc

#org @block_9
setvar 0x4009 2
jump @check_win_pc



'-------------------
#org @win
compare 0x4001 1
if != jump @win2
compare 0x4002 1
if != jump @win2
compare 0x4003 1
if != jump @win2
jump @end_player_won


#org @win2
compare 0x4004 1
if != jump @win3
compare 0x4005 1
if != jump @win3
compare 0x4006 1
if != jump @win3
jump @end_player_won


#org @win3
compare 0x4007 1
if != jump @win4
compare 0x4008 1
if != jump @win4
compare 0x4009 1
if != jump @win4
jump @end_player_won


#org @win4
compare 0x4001 1
if != jump @win5
compare 0x4004 1
if != jump @win5
compare 0x4007 1
if != jump @win5
jump @end_player_won


#org @win5
compare 0x4002 1
if != jump @win6
compare 0x4005 1
if != jump @win6
compare 0x4008 1
if != jump @win6
jump @end_player_won


#org @win6
compare 0x4003 1
if != jump @win7
compare 0x4006 1
if != jump @win7
compare 0x4009 1
if != jump @win7
jump @end_player_won


#org @win7
compare 0x4001 1
if != jump @win8
compare 0x4005 1
if != jump @win8
compare 0x4009 1
if != jump @win8
jump @end_player_won


#org @win8
compare 0x4003 1
if != jump @play
compare 0x4005 1
if != jump @play
compare 0x4007 1
if != jump @play
jump @end_player_won

'-----------------------

#org @winpc
compare 0x4001 2
if != jump @winpc2
compare 0x4002 2
if != jump @winpc2
compare 0x4003 2
if != jump @winpc2
jump @end_pc_won


#org @winpc2
compare 0x4004 2
if != jump @winpc3
compare 0x4005 2
if != jump @winpc3
compare 0x4006 2
if != jump @winpc3
jump @end_pc_won


#org @winpc3
compare 0x4007 2
if != jump @winpc4
compare 0x4008 2
if != jump @winpc4
compare 0x4009 2
if != jump @winpc4
jump @end_pc_won


#org @winpc4
compare 0x4001 2
if != jump @winpc5
compare 0x4004 2
if != jump @winpc5
compare 0x4007 2
if != jump @winpc5
jump @end_pc_won


#org @winpc5
compare 0x4002 2
if != jump @winpc6
compare 0x4005 2
if != jump @winpc6
compare 0x4008 2
if != jump @winpc6
jump @end_pc_won


#org @winpc6
compare 0x4003 2
if != jump @winpc7
compare 0x4006 2
if != jump @winpc7
compare 0x4009 2
if != jump @winpc7
jump @end_pc_won


#org @winpc7
compare 0x4001 2
if != jump @winpc8
compare 0x4005 2
if != jump @winpc8
compare 0x4009 2
if != jump @winpc8
jump @end_pc_won


#org @winpc8
compare 0x4003 2
if != jump @play5
compare 0x4005 2
if != jump @play5
compare 0x4007 2
if != jump @play5
jump @end_pc_won

' ---------------------------

#org @twinpc
compare 0x4011 2
if != jump @twinpc2
compare 0x4012 2
if != jump @twinpc2
compare 0x4013 2
if != jump @twinpc2
jump @apply_tmp


#org @twinpc2
compare 0x4014 2
if != jump @twinpc3
compare 0x4015 2
if != jump @twinpc3
compare 0x4016 2
if != jump @twinpc3
jump @apply_tmp


#org @twinpc3
compare 0x4017 2
if != jump @twinpc4
compare 0x4018 2
if != jump @twinpc4
compare 0x4019 2
if != jump @twinpc4
jump @apply_tmp


#org @twinpc4
compare 0x4011 2
if != jump @twinpc5
compare 0x4014 2
if != jump @twinpc5
compare 0x4017 2
if != jump @twinpc5
jump @apply_tmp


#org @twinpc5
compare 0x4012 2
if != jump @twinpc6
compare 0x4015 2
if != jump @twinpc6
compare 0x4018 2
if != jump @twinpc6
jump @apply_tmp


#org @twinpc6
compare 0x4013 2
if != jump @twinpc7
compare 0x4016 2
if != jump @twinpc7
compare 0x4019 2
if != jump @twinpc7
jump @apply_tmp


#org @twinpc7
compare 0x4011 2
if != jump @twinpc8
compare 0x4015 2
if != jump @twinpc8
compare 0x4019 2
if != jump @twinpc8
jump @apply_tmp


#org @twinpc8
compare 0x4013 2
if != jump @next
compare 0x4015 2
if != jump @next
compare 0x4017 2
if != jump @next
jump @apply_tmp

' ---------------------------

#org @twinplayer
compare 0x4011 1
if != jump @twinplayer2
compare 0x4012 1
if != jump @twinplayer2
compare 0x4013 1
if != jump @twinplayer2
jump @block


#org @twinplayer2
compare 0x4014 1
if != jump @twinplayer3
compare 0x4015 1
if != jump @twinplayer3
compare 0x4016 1
if != jump @twinplayer3
jump @block


#org @twinplayer3
compare 0x4017 1
if != jump @twinplayer4
compare 0x4018 1
if != jump @twinplayer4
compare 0x4019 1
if != jump @twinplayer4
jump @block


#org @twinplayer4
compare 0x4011 1
if != jump @twinplayer5
compare 0x4014 1
if != jump @twinplayer5
compare 0x4017 1
if != jump @twinplayer5
jump @block


#org @twinplayer5
compare 0x4012 1
if != jump @twinplayer6
compare 0x4015 1
if != jump @twinplayer6
compare 0x4018 1
if != jump @twinplayer6
jump @block


#org @twinplayer6
compare 0x4013 1
if != jump @twinplayer7
compare 0x4016 1
if != jump @twinplayer7
compare 0x4019 1
if != jump @twinplayer7
jump @block


#org @twinplayer7
compare 0x4011 1
if != jump @twinplayer8
compare 0x4015 1
if != jump @twinplayer8
compare 0x4019 1
if != jump @twinplayer8
jump @block


#org @twinplayer8
compare 0x4013 1
if != jump @next_player
compare 0x4015 1
if != jump @next_player
compare 0x4017 1
if != jump @next_player
jump @block

' ---------------------------

#org @end_pc_won
msgbox @msg_pc_won
callstd 0x6
jump @apply

#org @msg_pc_won
= You loose!

#org @end_player_won
msgbox @msg_player_won
callstd 0x6
jump @apply

#org @msg_player_won
= You win!

#org @quit
'msgbox @byemsg
'callstd 0x6
end
