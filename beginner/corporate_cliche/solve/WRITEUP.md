Corporate Cliche
============

This is an example of a classic buffer overflow. 

We cannot use `admin` as a username, but we need to login as admin to call the `open_admin_session()` function to get the flag. 

Since the password is read in using `gets()` this reads an unlimited amount of data until `\n` is reached. This means that we can write outside the bounds of the password variable which has a length of 32 bytes.

Since the username is defined directly after the password, it will be stored directly next to it in memory as well in a futher 32 bytes. 

So it looks something like this.


| 32 bytes  |  32 bytes |
| PASSWORD  |  USERNAME |

We can overflow the password to overwrite the username value to be `admin` to bypass the initial check. 

Then we need to make sure the original password is still for the admin account which is `🇦🇩🇲🇮🇳`.

`strcmp()` checks for a \x00 byte to mark the end of the string so we need to make sure we append that to the end of our values. 

Our final payload looks like:


```python
# {admin_password}{\x00}{padding}{admin_username}{\x00}
payload = "🇦🇩🇲🇮🇳".encode('utf-8') + b"\x00"
payload += b"A" * (32 - len("🇦🇩🇲🇮🇳".encode('utf-8') + b"\x00"))
payload += b"admin\x00"
```

Sending this value when prompted for the password gives us an admin session and we can read the flag!