# NOTE: Comments and __debug__ sections are removed at build time
import argparse
import base64
import ctypes
import zlib
import pathlib
import sys

PASSWORD = "cheese"

# https://gchq.github.io/CyberChef/#recipe=RC4(%7B'option':'UTF8','string':'Hydr0ph11na3'%7D,'Latin1','Base64')&input=dGhlX3Byb2JsZW1fd2l0aF9keW5hbWljX2xhbmd1YWdlc19pc195b3VfY2FudF9jX3R5cGVz&oeol=VT
FLAG = "jqsD0um75+TyJR3z0GbHwBQ+PLIdSJ+rojVscEL4IYkCOZ6+a5H1duhcq+Ub9Oa+ZWKuL703"

# Random blob used by some calculations in the C library
KEY = "68592cb91784620be98eca41f825260c"
HELPER = None


# Call into the DLL to decrypt the flag
def decrypt_flag(password: str) -> str:
    flag = bytearray(base64.b64decode(FLAG))
    buffer = (ctypes.c_byte * len(flag)).from_buffer(flag)

    key = ctypes.create_string_buffer(password.encode("utf-8"))
    result = get_helper().Decrypt(key, len(key) - 1, buffer, len(buffer))
    assert result == 3

    return flag.decode("utf-8")


# Drop the DLL to disk and load it
def get_helper():

    global HELPER
    if HELPER:
        return HELPER

    data = globals().get("DATA")
    if data:
        dll_path = pathlib.Path(__file__).parent / "hello.bin"
        if not dll_path.is_file():
            with open(dll_path, "wb") as dll_file:
                dll_file.write(zlib.decompress(base64.b64decode(data)))
        HELPER = ctypes.cdll.LoadLibrary(dll_path)
    else:
        if __debug__:
            # hack for debugging
            dll_path = "build\\Debug\\helper.dll"
            print(f"Loading DLL from: {dll_path}")
            HELPER = ctypes.cdll.LoadLibrary(dll_path)
        else:
            raise NotImplementedError()
    return HELPER


def check_three(password: str):
    return check_ex(password, "Check3")


def check_four(password: str):
    return check_ex(password, "Check4")


# Call a function the helper DLL with a structure containing callbacks
def check_ex(password: str, func: str):

    GetIntCallbackFn = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_wchar_p)

    class CallbackTable(ctypes.Structure):
        _fields_ = [("E", GetIntCallbackFn)]

    @GetIntCallbackFn
    def eval_int(v: str) -> int:
        # Evaluate a Python string and return an integer
        if __debug__:
            print(f"DEBUG: EVAL -{v}-")
        return int(eval(v))

    table = CallbackTable(
        E=eval_int,
    )

    helper = get_helper()
    helper[func].argtypes = [ctypes.POINTER(CallbackTable)]
    helper[func].restype = ctypes.c_int

    return helper[func](ctypes.byref(table))


def check_two(password: str):
    @ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int)
    def callback(i):
        return ord(password[i - 3]) + 3

    return get_helper().Check2(callback)


def check_one(password: str):
    if len(password) != 12:
        return False
    return get_helper().Check1(password) != 0


def check_password(password: str):
    global PASSWORD
    PASSWORD = password

    checks = [check_one, check_two, check_three, check_four]

    result = True
    for check in checks:
        result = result and check(password)
        if __debug__:
            print(f"DEBUG: {check=} {result=}")
    return result


def main():
    parser = argparse.ArgumentParser(description="CTF Challenge")
    parser.add_argument("password", help="Enter the password")

    args = parser.parse_args()

    if check_password(args.password):
        flag = decrypt_flag(args.password)
        print("Correct! The flag is DUCTF{%s}" % flag)
        return 0
    else:
        print("That is not correct")
        return 1


if __name__ == "__main__":
    sys.exit(main())
