// This example shows how awesome having :labels is.
// No dyn needed, everything's beautiful

#org 0x800000
checkflag 0x3000
if 5 jump :a
msgbox :msg_set
callstd 6
end
:a
msgbox :msg_clear
callstd 6
end
:msg_clear
= its clear man
#raw 0xff
:msg_set
= its set man
#raw 0xff

#org 0x900000
checkflag 0x3000
if 1 jump :b
setflag 0x3000
end
:b
clearflag 0x3000
end
