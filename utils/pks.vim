" Vim syntax file
" Language:	Pokemon ASC script file
" Maintainer:	Jaume Delclòs <cosa.rara97@gmail.com>
" Filenames:    *.pks
" Last Change:	23rd December 2012
" Web Page:     http://cosarara97.blogspot.com
"

if exists("b:current_syntax")
  finish
endif

syn keyword pksTodo contained	TODO

syn keyword pksStatement	jump goto call end return jumpif callif
syn keyword pksConditional	if
syn keyword pksLoop		while

syn match pksOperator      	"[=<>!]="
syn match pksString		"^= .*$"
syn match pksDefine		"^#define .\+$"

syn match pksInteger       	"\<\d\+"
syn match pksHex		"\<0x\x\+"
syn cluster pksNumber      	contains=pksInteger,pksHex

" syn match pksLabel		"^:\w*\>"
syn match pksLabel		":\w\+\>"
syn match pksDynLabel		"@\w\+\>"

" Comments - usual rem but also two colons as first non-space is an idiom
syn match pksComment		"'\(.*\)$" contains=pksTodo

" TODO
syn keyword pksCommand    #org #dyn #dynamic #raw
syn keyword pksCommand    nop0 nop1 jumpstd callstd jumpstdif callstdif
syn keyword pksCommand    jumpram killscript setbyte msgbox setbyte2
syn keyword pksCommand    writebytetooffset loadbytefrompointer
syn keyword pksCommand    setfarbyte copyscriptbanks copybyte
syn keyword pksCommand    setvar addvar subtractvar copyvar
syn keyword pksCommand    copyvarifnotzero comparebuffers comparevartobyte
syn keyword pksCommand    comparevartofarbyte comparefarbytetovar
syn keyword pksCommand    comparefarbytetobyte comparefarbytetofarbyte
syn keyword pksCommand    compare comparevars callasm callasm2
syn keyword pksCommand    special special2 waitspecial pause setflag
syn keyword pksCommand    clearflag checkflag resetvars sound cry
syn keyword pksCommand    fanfare waitfanfare playsound playsong
syn keyword pksCommand    fadedefault fadesong fadeout fadein warp
syn keyword pksCommand    warpmutted warpwalking falldownhole
syn keyword pksCommand    warpteleport warp3 warpelevator warp4 warp5
syn keyword pksCommand    getplayerxy countpokemon additem removeitem
syn keyword pksCommand    checkitemspaceinbag checkitem checkitemtype
syn keyword pksCommand    giveitemtopc checkiteminpc addfurniture
syn keyword pksCommand    takefurniture checkifroomforfurniture
syn keyword pksCommand    checkfurniture applymovement
syn keyword pksCommand    applymovementfinishat pauseevent disappear
syn keyword pksCommand    disappearat reappear reappearat movesprite
syn keyword pksCommand    farreappear fardisappear faceplayer spriteface
syn keyword pksCommand    trainerbattle lasttrainerbattle endtrainerbattle
syn keyword pksCommand    endtrainerbattle2 checktrainerflag
syn keyword pksCommand    cleartrainerflag settrainerflag movesprite2
syn keyword pksCommand    moveoffscreen spritebehave showmsg message
syn keyword pksCommand    closemsg lock lockall release releaseall
syn keyword pksCommand    waitbutton showyesno multichoice multichoice2
syn keyword pksCommand    multichoice3 showbox hidebox clearbox
syn keyword pksCommand    showpokepic hidepokepic picture braille
syn keyword pksCommand    addpokemon giveeg setpokemonpp checkattack
syn keyword pksCommand    storepokemon storefistpokemon storepartypokemon
syn keyword pksCommand    storeitem storefurniture storeattack storevar
syn keyword pksCommand    storecomp storetext pokemart pokemart2
syn keyword pksCommand    fakejumpstd pokemart3

" Define the default highlight linking.

highlight link pksTodo			Todo
highlight link pksStatement		Statement
highlight link pksCommand		Function
highlight link pksLabel			Label
highlight link pksDynLabel		Label
highlight link pksConditional		Conditional
highlight link pksOperator		Operator
highlight link pksString		String
highlight link pksDefine		Define
highlight link pksNumber		Number
highlight link pksInteger		pksNumber
highlight link pksHex			pksNumber
highlight link pksComment		Comment

let b:current_syntax = "pks"

" vim: ts=8
