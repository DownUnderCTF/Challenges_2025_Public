Yippee
============

From the challenge text: We were going through a stack of pictures and postcards that we found in the hope that we can put together a timeline of events. 
This one looks interesting, on the back of the photo there a hand drawn picture of what looks to be a waratah flower, but that's it.

Some background first; Writing OSINT challenges are harder than they first appear. You need to make a challenge that cannot be insta-solved by online services and
at the same time, not create a challenge that comes across as a guessy mess. I go into the creation process wanting to have enough information to start the process,
threads that the player can start going down. In this challenge, there's a few threads:

1. The challenge text mentions a waratah flower, which is the New South Wales state flower. This might bring the location down to the state of NSW, 
2. The sign is a warning sign to swimmers that there is a rip (dangerous current), these appear on patrolled beaches, so you know that it's patrolled
3. There's a large headland to the right, with rocks in the foreground, and
4. It's a postcard - does this mean a tourist location?

You can try to crop just that headland, and within Google Images also add the text "NSW Beach" or "NSW Patrolled Beach" you can start getting results that are close, enough that checking out some of these links should land you on Flynns Beach (which is the answer). This was the expected path, with some manually hunting.

Without uploading anything you can search manually for NSW beach headlands and try to match the look. If there was another method, I would love to hear about it in your writeups!

It is a medium challenge, the hope that this created various ways that people searched for NSW beaches that could match large rock and beach rocks shown in the photo.

Note that there was also some exif fun, a base64 rickroll and the LAT LONG is in the centre of the Bermuda Triangle.

DUCTF{Flynns Beach}
