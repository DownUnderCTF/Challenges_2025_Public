key = "skippy_the_bush_ "
iv = "kangaroooooooooo "

def toC(hexString):
    out = "    uint8_t var[] = { "
    for i in range(0, len(hexString), 2):
        out += "0x" + hexString[i] + hexString[i+1] + ", "
    out = out[:-2]
    out += " };\n"
    return out

def toHex(s):
    return ''.join(format(ord(c), '02x') for c in s)

def fromHex(hex_str):
    return ''.join(chr(int(hex_str[i:i+2], 16)) for i in range(0, len(hex_str), 2))

def leftShiftHex(hex_str, shift_amount=1):
    return ''.join(format((int(hex_str[i:i+2], 16) << shift_amount) & 0xFF, '02x') for i in range(0, len(hex_str), 2))

def rightShiftHex(hex_str, shift_amount=1):
    return ''.join(format((int(hex_str[i:i+2], 16) >> shift_amount) & 0xFF, '02x') for i in range(0, len(hex_str), 2))


s = toHex(iv)
print(s)

s = leftShiftHex(s)
print(s)
print(fromHex(rightShiftHex(s)))

s = toC(s)
print(s)