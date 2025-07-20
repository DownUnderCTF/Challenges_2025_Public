1. If you are trying to extract the value of the comparison as characters, you might have some issues. Try bytes instead.
2. If you're stuck after extracting, try look at the library it's calling.
3. The value you've extracted is a password hash. If you give it the corresponding password, maybe it will give you a flag?