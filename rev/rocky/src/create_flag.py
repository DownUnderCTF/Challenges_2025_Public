from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

flag = b'DUCTF{In_the_land_of_cubicles_lined_in_gray_Where_the_clock_ticks_loud_by_the_light_of_day}     '

key, iv = b'emergencycall911', b'119llacycnegreme'
cipher = AES.new(key, AES.MODE_CBC, iv=iv)
cipherText = cipher.encrypt(pad(flag, AES.block_size))

def toC(hexString):
    out = "    uint8_t flag[] = { "
    for i in range(0, len(hexString), 2):
        out += "0x" + hexString[i] + hexString[i+1] + ", "
    out = out[:-2]
    out += " };\n"
    return out

cipherHex = cipherText.hex()
cCipherHex = toC(cipherHex)
#temphexstr = "70924d0cf669f9d23ccabd561202351f"
#cCipherHex = toC(temphexstr)
print(cCipherHex)

cipher2 = AES.new(key, AES.MODE_CBC, iv=iv)
print(cipher2.decrypt(cipherText))
print(cipherHex)