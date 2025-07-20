Rolling Around
============

First off - credits to chompie, the solution code is heavily based off of her PoC found [here](https://github.com/chompie1337/Linux_LPE_eBPF_CVE-2021-3490/tree/main), (which is itself I think derived from some code from manfredp).
It's generally a solid approach, I'd used it before, and didn't want to reinvent the wheel. I've mostly just retrofitted all the actual BPF code to be for the bug in the challenge, and adjust some offsets and such.

So, the kernal patch provided adds the `ROL` instruciton - that is, rotate left. We implement the actual instruction for the emulator, as well as the functions responsible for calculating the minimum/maximum values of a register when being modified by a `ROL`.

To calculate the new min/max vals, we take the current min/max vals, and apply the specified rotation onto these values. This, hopefully, is obviously incorrect. 


To see this, let's look at how the solution abuses this:
We load the value 0 from a map into a register. We know this value is 0, because we set it from userland, but the verifier cant make any assumptions about the register value.

Then, we add 4, so the register is equal to 4, but the verifier still has no hints about its value.

Then, we AND with the constant 7. The verifier knows then, that the top 61 bits are all 0, whilst the bottom 3 bits are still unknown.

So, the verifier knows that the maximum for this register will be 7, and the minimum will be 0.
We then, using a branch, exit if the register is less than 2. We don't care about the execution path that dies, just the one that continues on.
So the max is still 7, and the minimum is now 3. Bitwise, thats 0b111, and 0b010. Note that, the actual value of the register is still 4 (0b100).

If we apply a left-rotation of 62, the `maximum` becomes (1<<63 + 1<<62 + 1), the `minimum` becomes (1<<63), and the true value ends up being 1. 
The core thing to see here, is that we have the true value (4), and the minimum value (2). When a left-rotation of 62 is applied, 3rd bit rolls over to become the 1st bit, in effect (whereas the 2nd bit becomes the most-significant bit), and thus there is now a difference between what is the perceived minimum value, and the actual minimum value.


This sort of confusion can then be used to gain stronger primitives. 
First, we want some information leaks, given we have kaslr enabled. We can leak a map pointer simply by loading the map-pointer into the bpf-prog, then adding a register with invalid bounds to it (which ours is, given our bug), which has the verifier mark it as an unknown scalar. Then we can store this "unknown scalar" back into a map, and read it out from userland.

Better yet though, is a leak from the kernel text. To do this, we wish to load in a map-pointer into a program, then read before it - because the "map-ptr" loaded points to the map's contents, but in the `bpf_map` struct, before the contents lie fields like function-table pointers.

Originally, you could use this range-confusion bug with ROL to have a register be say, 1, but be considered 0, and use that to add/subtract pointers, with the verifier being happy because it see's them as no-ops. However, the verifier will actually rewrite cases where arithmetic instructions use such "constant registers" with arithmetic instructions that actually use those constants instead. So this is a no-go.

Instead, we could have a register be considered to be, say, (0, 1) (where 0 is the min, 1 is the max), but have a true value of 2, and use that to achieve OoB accesses. Unfortunately, the verifier also rewrites arithmetic operations on maps, adding instructions to sanitise such cases, to bound the value to the perceived "max".

Then, we come to the case of having a register by say, (2, 3), but having a true value of 1. This passes the sanitisation checks, and so we go with this.
Note that, I've weakened the speculative-execution branch exploraiton done by the verifier, because in actuality, with the strategy we use, when you perform an arithmetic operation on a map, it splits the program-analysis into two branches of analysis, one with the "authentic" case, and another with a perceived "speculative" case, where it treats the map as having no 'offset', which causes it to fail our exploits. So, this challenge is different to reality unfortunately. I failed to find a bypass for the full speculative-exeuction mitifations of the verifier :(. 
Of course, after submitting the challenge, my friend mentions a writeup that shows that, calls to BPF helper functions are not sanitised with the same constant re-writing as map operations are, and thus give a much easier manner of exploitation. So I recommend going down that path.

So, to leak those function-table pointers we:
Load in a map (of size 0x1000)
Using the ROL bug, add a value of (0x800, 0cx00) (but has a true value of 0x400) to the map.
We can then subtract 0x500 from the map, which the verifier OKs, and read `array_map_ops`, giving us a kernel text leak.

Next, having achieved our infoleaks, we want to then get arbitrary read/write.
For arbitrary read, we use the same technique Chompie did, of overwriting the bpf\_map's `btf` address to the address we want to leak, and using the `BPF_OBJ_GET_INFO_BY_FD` syscall to leak values from the address - particularly the `id` field. This corruption of the `btf` field, is done similarly to leaking `array_map_ops`, by first adding an inflated range of values, (0x800, 0xc00_, then subtracting from the pointer so that we point to the   btf` field, and overwriting it.

Using this arbitrary read, and our earlier infoleak, we traverse through the `task\_struct` list, starting at `init\_task`, until we find our task, recognised by the `comm` field.

Then, we setup our kernel write:
We already know map addresses, from our earlier leaks.
For our map, we overwrite it's `ops` pointer, and point to the start of the actual map data.
We corrupt some other fields, notably inducing a type confusion by setting `bpf\_map-\>map\_type` to be a stack instead of an array. 
Then we set where the `PUSH\_ELEM` function pointer for a stack map would be, instead with the `get\_next\_key` function of array maps. This pretty easily gives us a WWW, given we control `key` and `next\_key`. 

Using the arb_write, we simply overwrite our `cred` pointer for our struct to `init\_cred`, and we're done!

If you have questions/wanted more details on a given point, feel free to reach out over discord (@ItsIronicIInsist)
