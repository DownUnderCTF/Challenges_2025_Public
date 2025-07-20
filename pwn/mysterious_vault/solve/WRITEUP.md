Mysterious Vault
============

The challenge is given as three binaries. After a little bit of reversing, it should be easy to see that `mysterious_vault` sets up some shared memory, and then forks and runs both `password_checker_3000` and `password_checker_3001`. Both of these map in the same shared memory, and read in the 'password' entered by the user.

The password-checkers do do some setup before reading in the input. They of course setup the shared memory, then close the file descriptos for stdin/stdout/stderr. 
Then, they run a `seccomp` script that only allows the `read`, `write`, `open`, and `exit` syscalls. If you didn't find it during the CTF, I strongly recommend the github repo from david942j, found [here](https://github.com/david942j/seccomp-tools), for dumping seccomp programs into a human readible format. 

After that, they read in the the users password from shared memory. There is a very obvious buffer overflow, and no stack canary or PIE. Additionally, the password-checker binaries are statically compiled, so the libc code is also included. This means we can ROP extremely easily.

One thing is that before we return from `main`, we call `strcspn` on the password and check it doesn't contain any of the characters in "password". However, this check is trivially bypassed by inserting a NULL byte at the start of the user's password, given we're allowed to enter in binary data.

Now: ROP. The end goal is to copy in the contents of the `password` file from each of the `trusted-env` folders back into the shared memory, concatenated. Additionally, we must exit our ROP chain gracefully, as `mysterious_vault` checks that its children exit succesfully. Finally, we must use the same ROP chain for both `password_checker_3000` and `password_checker_3001`.

First, we use a ROP-gadget tool (I recommend `ropr`, but often use several in case one misses important gadgets). I generated the ROP-gadget list for both `password-checker` binaries, then wrote a small python script to take both lists and find addresses where both had valid gadgets. 




Now, I'll run through the ROP chain.
The first byte is a 0 - as previously mentioned, to make the `strcspn` a no-op.
Then, `password_checker_3001` uses 0x10 bytes less stack space than `3000`, so we have two gadgets worth of space that will only be executed on `3001`. - so we do
`pop rdi; PASSWORD_ADDR`
That is, we pop the address of the string constant "password" into `rdi`. 

Then, at offset 0xe8, both binaries are now executing the ROP chain. To simplify this, we're looking for a gadget that can allow us to diverge executions between the two binaries.

Here's what I used: 
```
427ae6:
	3000 gadg: pop rbx; pop rbp; ret
	3001 gadg: add rsp, 0x70; pop rbp; ret;
```

This gadget just pop's rbx+rbp for `password-checker-3000`, but adds to rsp in `password-checker-3001`. This means that for the 0x70 bytes of stack space, we can just put normal gadgets for `password-checker-3000` without worrying about if. they're valid for `password-checker-3001`.

We pop '0' into rbx, as we don't use it. We do pop the address of a ROP gadget into rbp, for use later.
This gadget is: `syscall ; pop rbx ; ret`.
We then pop the addr of 'password' into rdi, and '2' into rax, and then execute the gadget: `xor esi, esi ; call rbp`.
With esi zeroed out, we issue the syscall: `open("password", O_RDONLY)`.

The fd will be returned into rax. `call` pushes a saved-rip onto the stack, but since rbp=`syscall; pop rbx ; ret`, rbx absorbs that saved-rip and lets us continue normally executing.

We then pop 0 into rdi (the file-descriptor), and `SHARED_ADDR` into rsi, before issueing another syscall. rax was set to 0 by the last syscall, so this becomes: `read(password_fd, SHARED_ADDR, _)`, where `rdx` happened to be a valid number of bytes.

Lastly, we pop 60 into rax and exit.

For `3001`, we do similarly. Notably, the syscall gadget used requires that `rbp-0x28` is writeable, and pops rbp after.
We pop rbp to a value that satisfies those constraints, open the file, then pop a value into rbp that has a valid read-count at offset -0x20. We then read the file contents, using `mov rdx, [rbp-0x20];syscall`, before exiting.


If all this goes succesfully, we've read both passwords into the correct addresses, exiting without dying to a SIGSEGV or similar, and the vault should be open!
