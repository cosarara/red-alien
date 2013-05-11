
#dyn 0x800000

#org @main
while(0x3000) {
msgbox @text
callstd 6
while(0x3001) {
  msgbox @text2
  callstd 2
  }
msgbox @text
callstd 3
}
end

#org @text
= lalalalalala

#org @text2
= lalalalalala

#org @text3
= lalalalalala

