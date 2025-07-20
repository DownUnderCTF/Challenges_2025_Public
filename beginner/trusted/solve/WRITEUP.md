# Pix's Writeup

Assuming we've already solved Horoscopes, we know how to access the gemini capsule.

We can find the access port in the community hub which tells us the port is 30063.
It also tells us to use the daily code phrase, which we can find on on the survival page.

```
Today's authentication phrase: "Moonlight reflects twice on still water"
Response: "But+ripples+show=truth%in motion"
```

If we cannot to it, we get a failed handshake.. lets try netcat with -x to see the bytes.

```
00000000  32 30 20 74  65 78 74 2F  67 65 6D 69  6E 69 0D 0A  20 text/gemini..
00000010  23 20 41 64  6D 69 6E 20  50 61 6E 65  6C 0A 0A 54  # Admin Panel..T
00000020  68 69 73 20  70 61 67 65  20 69 73 20  75 6E 64 65  his page is unde
00000030  72 20 63 6F  6E 73 74 72  75 63 74 69  6F 6E 21 0A  r construction!.
00000040  0A 49 66 20  79 6F 75 20  61 72 65 20  74 68 65 20  .If you are the
00000050  61 64 6D 69  6E 2C 20 79  6F 75 20 73  68 6F 75 6C  admin, you shoul
00000060  64 20 6C 6F  67 69 6E 0A  3D 3E 20 70  61 73 73 77  d login.=> passw
00000070  6F 72 64 5F  70 72 6F 74  65 63 74 65  64 2E 67 6D  ord_protected.gm
00000080  69 20 4C 6F  67 69 6E 0A                            i Login.
```

Okay, so its an admin page! But without valid TLS, that makes it invalid Gemini so we'll have to do this by hand.

We can see a page in there => password_protected.gmi Login

If we connect to that...

```
00000000  31 31 31 31  20 4D 6F 6F  6E 6C 69 67  68 74 20 72  11 Moonlight r
00000010  65 66 6C 65  63 74 73 20  74 77 69 63  65 20 6F 6E  eflects twice on
00000020  20 73 74 69  6C 6C 20 77  61 74 65 72  0A 3A 0D 0A   still water.:..
```

Oh hey, looks like.. someone trying to get a SENSITIVE INPUT from us over Gemini.

Well given we cannot actually load the page, we can pass the parameter like on the web with ?<our param>

If we pass it directly, we'll get a 59 bad request.

That makes sense, this is expected to be client connecting, so we'll need to encode it like a URL

`/password_protected.gmi?But%2Bripples%2Bshow%3Dtruth%25in+motion`

Put that into our connection and BOOM we get a 20 response and the flag! :D

DUCTF{Cr1pPl3_Th3_1nFr4sTrUCtu53}
