Fishy Website
============

From the given website, we can infer that it is a phishing website that tries to make the user to run a PowerShell script. The PowerShell script is stored on the `/verify/script` endpoint.

After deobfuscation, we can identify that the PowerShell script will start up a C2 client that uses fake TLS headers to hide communication. C2 communications are also encrypted using RC4 using the key `f16ecdc6794c66d102f833c486e7a4358d69bdd21d50f5fbdfecaf0b9e53a4d3`. When the C2 client is sending data to the server, it will prepend `0x02,0x04,0x06,0x08` to mark the end of the data.

To find the TLS communications, we can find any packets that contains the endpoint of the PowerShell script by using this Wireshark filter.

```
_ws.col contains "/verify/script"
```

From that filter, we can find the attacker IP of `20.5.48.200`.

To decrypt the C2 communications, we need to filter out TLS packets between the attacker IP and the victim and decrypt those packets using RC4.

```py
# decrypt_traffic.py

from pyshark import *
from binascii import unhexlify
from Crypto.Cipher import ARC4

SECRET = b"\xf1n\xcd\xc6yLf\xd1\x02\xf83\xc4\x86\xe7\xa45\x8di\xbd\xd2\x1dP\xf5\xfb\xdf\xec\xaf\x0b\x9eS\xa4\xd3"

packets = FileCapture("../publish/capture.pcapng", display_filter="ip.addr == 20.5.48.200 && tls.app_data")

for packet in packets:
    rc4 = ARC4.new(SECRET)
    packet_bytes = unhexlify(packet.tls.app_data.replace(":", ""))
    if packet.ip.dst == "20.5.48.200":
        packet_bytes = packet_bytes[:-4]
    payload = rc4.decrypt(packet_bytes).decode()
    if packet.ip.dst == "20.5.48.200":
        print(payload)
    else:
        print(f"> {payload}")
```

From the decrypted traffic, we can see that the attacker ran the usual recon commands and also exfiltrated a file named `keys_backup.tar.gz`.

```
❯ python decrypt_traffic.py
> $env:COMPUTERNAME
DESKTOP-PIVSTG0
> $env:USERNAME
jdoe
> [System.Net.Dns]::GetHostByName($env:COMPUTERNAME)
HostName        Aliases AddressList
--------        ------- -----------
DESKTOP-PIVSTG0 {}      {192.168.190.128}
> (Get-CimInstance Win32_OperatingSystem).Caption
Microsoft Windows 10 Home
> whoami /priv
PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                          State
============================= ==================================== ========
SeShutdownPrivilege           Shut down the system                 Disabled
SeChangeNotifyPrivilege       Bypass traverse checking             Enabled
SeUndockPrivilege             Remove computer from docking station Disabled
SeIncreaseWorkingSetPrivilege Increase a process working set       Disabled
SeTimeZonePrivilege           Change the time zone                 Disabled
> net session 2>&1 | Out-Null; if ($LASTEXITCODE -eq 0) {"Admin"} else {"Standard User"}
Standard User
> ls $HOME
Directory: C:\Users\jdoe


Mode                 LastWriteTime         Length Name                             
----                 -------------         ------ ----                             
d-r---          6/6/2025   7:31 PM                3D Objects                       
d-r---          6/6/2025   7:31 PM                Contacts                         
d-r---          6/6/2025   7:31 PM                Desktop                          
d-r---          7/9/2025   8:39 PM                Documents                        
d-r---          7/9/2025   8:33 PM                Downloads                        
d-r---          6/6/2025   7:31 PM                Favorites                        
d-r---          6/6/2025   7:31 PM                Links                            
d-r---          6/6/2025   7:31 PM                Music                            
d-r---          6/6/2025   7:38 PM                OneDrive                         
d-r---          6/6/2025   7:34 PM                Pictures                         
d-r---          6/6/2025   7:31 PM                Saved Games                      
d-r---          6/6/2025   7:34 PM                Searches                         
d-r---          6/6/2025   7:31 PM                Videos
> ls $HOME\Documents
Directory: C:\Users\jdoe\Documents


Mode                 LastWriteTime         Length Name                             
----                 -------------         ------ ----                             
-a----          7/9/2025   8:38 PM            157 keys_backup.tar.gz
> [Convert]::ToBase64String([System.IO.File]::ReadAllBytes("C:\Users\jdoe\Documents\keys_backup.tar.gz"))
H4sIAAAAAAAAA+3OMQrCQBSE4dSeIieQt3m78QCKlYVorBdZjYVgkeyCQby7iyCIfdTi/5qBaWbOx6GfxmssRiRZbe0zs88UcVoYJ6q1VlJp7mc2V6WMeeol9XHfleU3pv7RYjdvljfjT0md84MkH+zFHzRshnXjm9XWx862rQn3ya+vAgAAAAAAAAAAAAAAAADePAC9uw8vACgAAA==
> exit
```

After extracting the `keys_backup.tar.gz` file, we will find a file called `keys.txt` which contains the flag.
