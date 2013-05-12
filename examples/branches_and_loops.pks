
#dyn 0x800000

#org @main
if(0x3000) {
	while(0x4000 < 3) {
		msgbox @text
		callstd 6
		addvar 0x4000 1
	}
} else {
	msgbox @text2
	callstd 6
}
end

#org @text
= lalalalalala

#org @text2
= lelelelelele


