# Proof of concept RPC service using h11 for HTTP/1.1 handling for ticket [TICKET-1337]
# Handles requests for internal service management and diagnostics, and has restricted access via an allowlist of IPs
# This service is not meant to be robust, but rather a proof of concept for the internal service management
# Future use cases will see this service as a control panel for all internal services after the last incident with poor service management
# This code was written in collaboration with Github Copilot, which resulted in extra time spent on debugging and fixing issues

import socket
import h11
import logging
import dotenv
import os
import datetime
import re

dotenv.load_dotenv("./.env")

# Logging configuration based on environment
FLAG = os.getenv("FLAG")
ENV = os.getenv("ENV", "production").lower()
LOG_LEVEL = logging.DEBUG if ENV == "debug" else logging.ERROR
LOG_FORMAT = '[%(asctime)s] %(levelname)s: %(message)s' if ENV == "debug" else '[%(asctime)s] %(message)s'
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, handlers=[ logging.FileHandler("debug.log"), logging.StreamHandler()])
logger = logging.getLogger("rpc_service")

class Config:
    def __init__(self):
        self.auth_key = os.getenv('AUTHENTICATION_KEY')
        self.service = 'RPC'
        self.requests = 0
        self.authorized_ips = ["127.0.0.1"]
    
    def __repr__(self):
        joined_ips = '</br>\n'.join(self.authorized_ips)
        repr_message = f"\nCurrent Server Time: {datetime.datetime.now().strftime('%Y %M %d %T')}"
        repr_message += f"\n</br>Authorized IPs:</br>{joined_ips}"
        repr_message += f"\n</br>Authentication Token: {self.auth_key[0:8]}..."
        repr_message += f"\n</br>Requests served: {self.requests}"
        return repr_message

config = Config()

def build_stats_page(get_log=False, get_config=True):
    """Provide analytics for the RPC Service, display configurations and display activity logs"""

    # Print logs
    if get_log == True:
        template = """
            <h1>Admin Stats Page</h1>
                {logs}
            """.format(logs=get_logs())
    else:
        template = """
            <h1>Admin Stats Page</h1>
            <p>Page to show logs or Configuration</p>
            """

    # Full config
    if get_config == True:
        template += """
                    <h2>Current Configuration</h2>
                    {config}
                    """
    else:
        template += """<p>{config.service} service health ok</p>"""

    template += "<p>Administrative Interface for RPC Server</p>"
    logger.error(template)
    return template.format(config=config)

def get_logs():
    """If debug logs are requested with for the stats page, can become noisy though"""
    debug_logs = open("debug.log", "r").readlines()
    logs = "\n<h2>Server Debug Logs</h2>"
    logs += "\n".join([line.rstrip() for line in debug_logs])
    return logs

def send_response(conn, conn_state, status_code, body, content_type="text/plain"):
    """Send a response back to the client."""
    if isinstance(body, str):
        body = body.encode()
    response = h11.Response(
        status_code=status_code,
        headers=[
            ("Content-Length", str(len(body))),
            ("Content-Type", content_type),
        ]
    )
    conn.send(conn_state.send(response))
    conn.send(conn_state.send(h11.Data(data=body)))
    conn.send(conn_state.send(h11.EndOfMessage()))
    config.requests += 1

def handle_request(conn, conn_state, request):
    """Handle incoming requests and route them to the appropriate handler based on the request target."""
    target = request.target.decode()
    headers = {k.decode().lower(): v.decode() for k, v in request.headers}

    # Allowlist check
    forwarded_for = headers.get("x-forwarded-for", "").strip()
    auth_key = headers.get("auth-key")
    
    if config.authorized_ips and forwarded_for not in config.authorized_ips:
        logger.warning(f"Blocked access from unauthorized IP: {forwarded_for}")
        body = f"Access denied: You are not allowed to access this service. Only {', '.join(config.authorized_ips)} are allowed access.".encode()
        body += f". \nThe IP recieved was: {forwarded_for}".encode()
        send_response(conn, conn_state, 403, body)
        return

    # Simple auth check for endpoints that require authentication
    elif auth_key != config.auth_key:
        logger.warning("Unauthorized access attempt to /stats")
        send_response(conn, conn_state, 403, "Unauthorized: Invalid Auth-Key")
        return

    # /stats endpoint
    if target.startswith("/stats"):
        try:
            params = {}
            for param in re.search(r".*\?(.*)", target).groups()[0].split("&"):
                logger.error(param)
                params[param.split("=")[0]] = bool(param.split("=")[1])
            body = build_stats_page(**params).encode()
        except Exception as e:
            logger.error(f"[!] Error while fetching stats. Request made to: {target} with error: {e}")
            send_response(conn, conn_state, 500, e)
            return
        send_response(conn, conn_state, 200, body)
        return

    # /ping endpoint
    elif target == "/ping":
        send_response(conn, conn_state, 200, "Pong!")
        return

    # /update_allowlist endpoint, instead of hardcoding IP's manually, just make it easier to update the config on the fly.
    # DB driven in the future
    elif target.startswith("/update_allowlist"):
        ip_address = target.split('=')[-1]
        if ip_address:
            if ip_address not in config.authorized_ips and re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$").findall(ip_address):
                config.authorized_ips.append(ip_address)
                logger.info(f"Added {ip_address} to allowlist.")
                send_response(conn, conn_state, 200, f"IP {ip_address} added to allowlist.")
            else:
                logger.warning(f"IP {ip_address} is already in the allowlist or Invalid Input Provided.")
                send_response(conn, conn_state, 200, f"IP {ip_address} is already allowed.")
        return

    # TODO: Add more endpoints for internal service management. Final version will act like a control 
    # panel for all the internal services custom built for our needs, possibly could be done using an internal scan
    else:
        send_response(conn, conn_state, 404, "Invalid endpoint or missing key")
        return

def serve():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", 8081))
    sock.listen(5)
    logger.info("[*] RPC backend listening on port 8081")

    while True:
        conn, _ = sock.accept()
        conn.settimeout(10)
        conn_state = h11.Connection(h11.SERVER)
        buffer = b""
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break

                conn_state.receive_data(data)

                while True:
                    try:
                        event = conn_state.next_event()
                    except Exception as e:
                        logger.error(f"[!] State transition error: {e}")
                        raise

                    if isinstance(event, h11.Request):
                        handle_request(conn, conn_state, event)

                    elif isinstance(event, h11.EndOfMessage):
                        try:
                            conn_state.start_next_cycle()
                            logger.debug("[*] Started next cycle")
                        except Exception as e:
                            logger.error(f"[!] Could not reset connection: {e}")
                            raise

                    elif isinstance(event, h11.NEED_DATA):
                        break

                    elif isinstance(event, h11.PAUSED):
                        logger.debug("[*] Connection is paused.")
                        break
                    else:
                        logger.warning(f"[!] Unexpected event: {event}")

        except h11.RemoteProtocolError as e:
            logger.error(f"[!] RemoteProtocolError: {e}")
        except Exception as e:
            logger.error(f"[!] General error: {e}")
        finally:
            try:
                conn.close()
                logger.debug("[*] Connection closed")
            except Exception as e:
                logger.error(f"[!] Error closing connection: {e}")

if __name__ == "__main__":
    serve()












# Jonathon will never read this, but this is stupid
# and although their fear of "Supply Chain Attacks" on management services isn't completely unfounded --
# this service is simply not the solution to that problem
# Although I do understand the need for a simple RPC service to manage internal services and diagnostics, using an "obscure" tech stack is rarely a deterrent for committed attackers.
# The fact that we are not using open source solutions like Consul or etcd is beyond me, but I am not the one making the decisions here
# and I just want to feed my 3 cats and the stray rats living in my basement
# Any documentation regarding this service will be added to the README.md file in the root of the project in the future, if this MVP somehow gets approved
# Karl - Please, for the sake of all that is good, do not approve this MVP
