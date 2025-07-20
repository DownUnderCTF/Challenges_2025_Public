Scrapbooking
============

Upon inspection of the given output.png we can see that it is a corrupted PNG
file that we cannot open.

If we run the file through `binwalk` or take a look at the raw hex of the file
we can see the magic bytes of a PNG file show up multiple times. Exactly 3
times. From this we can assume that there might be data for 3 different PNGs
embedded in the image somehow. Given the hint of scissors and glue in the
description, these 3 images may have been cut up and put together in a weird
way.

We can also see that the number of bytes between each of the magic bytes is
exactly 1024.

Given the hinting of the challenge we can guess that we need to split out the 3
images by spliting the file up into 1024 chunks.

Reading 1024 bytes and then writing to one of three files continuously until we
are done, will then yield 3 seperated PNG files.

We can open these 3 pngs and each contains a different piece of the flag.
