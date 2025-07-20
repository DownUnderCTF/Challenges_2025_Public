import struct
import hashlib
import sys
from datetime import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def read_file_structure(filename):
    with open(filename, "rb") as f:
        data = f.read()

    offset = 0

    magic = struct.unpack("<I", data[offset : offset + 4])[0]
    if magic != 0x314D5053:
        print(f"Error: Invalid magic number: 0x{magic:08X}")
        return None
    offset += 4

    _ = struct.unpack("<H", data[offset : offset + 2])[0]
    offset += 2

    _ = struct.unpack("<H", data[offset : offset + 2])[0]
    offset += 2

    salt_size = struct.unpack("<H", data[offset : offset + 2])[0]
    offset += 2
    salt = data[offset : offset + salt_size]
    offset += salt_size

    nonce_size = struct.unpack("<H", data[offset : offset + 2])[0]
    offset += 2
    nonce = data[offset : offset + nonce_size]
    offset += nonce_size

    tag_size = struct.unpack("<H", data[offset : offset + 2])[0]
    offset += 2
    tag = data[offset : offset + tag_size]
    offset += tag_size

    data_size = struct.unpack("<I", data[offset : offset + 4])[0]
    offset += 4
    ciphertext = data[offset : offset + data_size]

    return {"salt": salt, "nonce": nonce, "tag": tag, "ciphertext": ciphertext}


def derive_key(password, salt, iterations=0xAAAA):
    key = password.encode("utf-8")
    for _ in range(iterations):
        key = hashlib.sha256(key + salt).digest()
    return key


def decrypt_data(ciphertext, key, nonce, tag):
    aesgcm = AESGCM(key)
    try:
        decrypted = aesgcm.decrypt(nonce, ciphertext + tag, None)
        return decrypted
    except Exception as e:
        print(f"Decryption failed: {e}")
        return None


def read_length_prefixed_string(data, offset):
    if offset + 4 > len(data):
        return None, offset

    length = struct.unpack("<I", data[offset : offset + 4])[0]
    offset += 4

    if offset + length > len(data):
        return None, offset

    string_data = data[offset : offset + length]
    offset += length

    return string_data.decode("utf-8"), offset


def parse_uuid(data, offset):
    if offset + 16 > len(data):
        return None, offset

    uuid_bytes = data[offset : offset + 16]
    offset += 16

    uuid_hex = uuid_bytes.hex()
    uuid_str = f"{uuid_hex[:8]}-{uuid_hex[8:12]}-{uuid_hex[12:16]}-{uuid_hex[16:20]}-{uuid_hex[20:32]}"

    return uuid_str, offset


def parse_entry(data, offset):
    uuid, offset = parse_uuid(data, offset)
    if uuid is None:
        return None, offset

    title, offset = read_length_prefixed_string(data, offset)
    if title is None:
        return None, offset

    username, offset = read_length_prefixed_string(data, offset)
    if username is None:
        return None, offset

    password, offset = read_length_prefixed_string(data, offset)
    if password is None:
        return None, offset

    notes, offset = read_length_prefixed_string(data, offset)
    if notes is None:
        return None, offset

    if offset + 16 > len(data):
        return None, offset

    created = struct.unpack("<q", data[offset : offset + 8])[0]
    offset += 8
    modified = struct.unpack("<q", data[offset : offset + 8])[0]
    offset += 8

    return {
        "id": uuid,
        "title": title,
        "username": username,
        "password": password,
        "notes": notes,
        "created": datetime.fromtimestamp(created),
        "modified": datetime.fromtimestamp(modified),
    }, offset


def parse_entries(data):
    offset = 0

    if len(data) < 4:
        print("Error: Data too short to contain entry count")
        return []

    entry_count = struct.unpack("<I", data[offset : offset + 4])[0]
    offset += 4
    print(f"\nFound {entry_count} entries:")

    entries = []
    for i in range(entry_count):
        entry, offset = parse_entry(data, offset)
        if entry is None:
            print(f"Error: Failed to parse entry {i + 1}")
            break
        entries.append(entry)

    return entries


def print_entry(entry, index):
    print(f"\n{'=' * 60}")
    print(f"Entry {index}:")
    print(f"{'=' * 60}")
    print(f"Title:    {entry['title']}")
    print(f"Username: {entry['username']}")
    print(f"Password: {entry['password']}")
    print(f"Notes:    {entry['notes']}")
    print(f"Created:  {entry['created']}")
    print(f"Modified: {entry['modified']}")
    print(f"ID:       {entry['id']}")


def main():
    file_data = read_file_structure("../publish/passwords.spm")
    if not file_data:
        sys.exit(1)

    password = "DUCTF2025!"

    key = derive_key(password, file_data["salt"])
    decrypted = decrypt_data(
        file_data["ciphertext"], key, file_data["nonce"], file_data["tag"]
    )

    if decrypted:
        entries = parse_entries(decrypted)
        for i, entry in enumerate(entries, 1):
            print_entry(entry, i)


main()
