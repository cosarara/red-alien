// A little demo of features

#include "stdlib/std.rbh"
#dyn 0x800000

#define THAT_GUY 2

#org @main
checkflag EM_BADGE1
if 0 jump :ya_noob // Wild PKSV/C-style labels appeared
msgbox @good 6 // Wild XSE compatibility appeared!
if (! EM_BADGE2 ) {
	msgbox :bg2_bad
	callstd 6
} else {
	msgbox :bg2_good
	callstd 6
}
jump :end

:ya_noob
msgbox :msg_nuv // yes, it's using a label for the msg
callstd 6
:end
disappear THAT_GUY // It's a PKSV command with a constant!
end

:msg_nuv // It's a multi-line string!
= So, man, are you a total nuv?\n
= You didn't even get the first\l
= medal kid.

#raw 0xFF // I won't eat your bytes, but you'll have to terminate your strings
          // Unless you use #org @whatever

:bg2_bad
= But you didn't get the 2nd\none...\xFF

:bg2_bad
= But you didn't get the 2nd\none...

// See? No terminating here, since it will be separated from the next one automagically

#org @good // It's an ugly-ass traditional string!
= You are good man\pYou are pretty good.\pI think we should go have something to drink

