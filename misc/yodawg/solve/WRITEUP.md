Yo Dawg
============

Two ways to solve; the rev "I'm not booting up Windows" way that definitely earns the medium flag, and the "Run Windows executables? What could go wrong?" method. I'm only going to go through the later as there was as much code dedicated to making rev painful as it was coding up the challenge.

The first 8 challenges in the Yo Dawg CTF are baby/super easy. There's a Caeser Cipher (Salads), simple password hash (crackstation.net for this instantly, though feel free to john/hashcat with rockyou.txt), Rot Cipher (dcode.fr is great here), Hidden (you can either drag the window down to see the morse or view this in the DLL) and RSA (RSA, dcode.fr again for a quick solve).

Then there's Vaas (simple google search of who is the voice actor), did you notice it made you enter it in twice? :D

Once that's done it's off to the 1995 version, which you'll be grateful to know that I cut this down from several challenges to just three. A DES cipher (flag{des4eva}), DEFCON 3 quiz (Tropicana) and the the best quote from Hackers (1995) that has three works: Hack the Planet!

Then the flag is presented as DES again, time to decrypt to finally get the flag: DUCTF{1995_to_2025}

For those that attempted rev, you might have seen 4 fake AES functions, 1 fake getflag() function, lots of random variables, fake base64 and half of the flags visible and half AES encrypted. If you were still successful, awesome job :)
