Pix
============

Wrap the macro in a vim file (comments optional for syntax highlighting etc)
```vim
" filename: solve.vim
" vim: set filetype=vim
let @q = '<macro_goes_here>'
```

You'll need to fix up the notation a little to be loadable, such as replacing `<CR>` with `` (CTRL-V + CTRL-M)
`:help key-notation` inside of vim/neovim will give you all the possible combos you might need to replace

Once they're fixed up, open up the large text file in vim/neovim and load the macro

:source solve.vim

Finally, run the macro with `@q`
But wait you say! Where is my flag?!

Welps, the end of macro does some funky stuff, but we can see it yanks a few things into registers.

So to find the flag, you can either:

```
:reg
```

And look through the registers, the flag will be in the `z` register.

Or you can print the `z` register direct by going to the buffer and using `"zp` and this will print
a string with the flag: `DUCTF{3Welc0me_.Tru3-VI-cult1s7!}`

