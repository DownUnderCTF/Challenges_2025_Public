Godot
============

# Premise
The goal was to show everyone how easy it is to reverse a game! There's a lot of open source tools already available, and something like https://github.com/GDRETools/gdsdecomp easily does the trick for this CTF, as long as you dump the AES key from memory.

This game contains dialogue from and is an overly overt reference to the 1953 tragicomedy "Waiting for Godot" by Samuel Beckett. The theme is post-war existentialism, where you are waiting in anticipation for something that never (or perhaps can never) arrive...

# Reversing
The hard part of this CTF is right at the start - you will need to open the game and dump the AES encryption key from memory. From there, you can open up the game in something like GDRE by supplying the correct key.

Opening up the file in GDRE shows that the player seems to need to activate the flags "lucky" and "godot".

Lucky looks like it's easy - just platform until you meet Pozzo, and talk to him.

Godot, however, looks like it's initialised... oddly. Long story short, a bit of digging will show you that Godot will spawn at the Shop (with Estragon) when you manage to reach -1 days of time.

To spawn Godot, you can open the game, set your time to 1 day (plus a minute or so) prior and wait for the time to pass. Alternatively, you could have extracted the entire game's files and opened it in Godot yourself. This way, you can just edit "lucky" and "godot" to true, and run the game in debug mode :)
