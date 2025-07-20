The Flag button is disabled through the call to `View.disabled()`. We can hook
this function to change its behaviour to prevent the button from being
disabled.

```
$ nm -gU swiftpasswordmanager  | rg -i disabled
00000000002a28e0 T $s12SwiftCrossUI4ViewPAAE8disabledyQrSbF
00000000005ddc2c D $s12SwiftCrossUI4ViewPAAE8disabledyQrSbFQOMQ
```

Running the binary under gdb using the `hook.gdb` script will disable the
disabling of the button and make it clickable. Clicking the Flag button reveals
the flag in a popup.

`hook.gdb`:

```
break $s12SwiftCrossUI4ViewPAAE8disabledyQrSbF
commands
    set $rdi = 0
    continue
end
run
```
