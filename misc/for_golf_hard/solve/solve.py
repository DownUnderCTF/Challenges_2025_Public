import socket
import struct
from typing import List, Optional, Tuple


class NBDClient:
    """Simple NBD client for reading from a Network Block Device server."""

    # NBD protocol constants
    NBD_MAGIC = 0x4E42444D41474943  # "NBDMAGIC"
    NBD_OPTION_MAGIC = 0x49484156454F5054  # "IHAVEOPT"
    NBD_REQUEST_MAGIC = 0x25609513
    NBD_REPLY_MAGIC = 0x67446698

    # NBD commands
    NBD_CMD_READ = 0
    NBD_CMD_DISC = 2

    # NBD options
    NBD_OPT_EXPORT_NAME = 1
    NBD_OPT_GO = 7

    # NBD reply types
    NBD_REP_ACK = 1
    NBD_REP_INFO = 3

    # NBD info types
    NBD_INFO_EXPORT = 0

    def __init__(self, host: str = "localhost", port: int = 10809):
        """Initialize NBD client."""
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.export_size: int = 0
        self.handle_counter: int = 0

    def connect(self, export_name: str = "") -> None:
        """Connect to NBD server and perform handshake."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

        # Perform NBD handshake
        self._new_style_handshake(export_name)

    def _new_style_handshake(self, export_name: str) -> None:
        """Perform new-style NBD handshake."""
        # Read initial greeting (16 bytes)
        greeting = self.socket.recv(16)
        if len(greeting) != 16:
            raise RuntimeError(f"Short greeting: {len(greeting)} bytes")

        magic, option_magic = struct.unpack(">QQ", greeting)

        if magic != self.NBD_MAGIC:
            raise ValueError(f"Invalid NBD magic: 0x{magic:x}")

        if option_magic != self.NBD_OPTION_MAGIC:
            raise ValueError(f"Invalid option magic: 0x{option_magic:x}")

        # Read handshake flags (2 bytes)
        flags_data = self.socket.recv(2)
        if len(flags_data) != 2:
            raise RuntimeError(f"Short flags: {len(flags_data)} bytes")

        handshake_flags = struct.unpack(">H", flags_data)[0]

        # Send client flags (4 bytes) - no flags
        client_flags = struct.pack(">I", 0)
        self.socket.send(client_flags)

        # Send NBD_OPT_GO option
        export_name_bytes = export_name.encode("utf-8")

        # Option header: magic (8) + option_id (4) + length (4)
        option_length = (
            4 + len(export_name_bytes) + 2
        )  # export_name_len + export_name + info_request_count
        option_header = struct.pack(
            ">QII", self.NBD_OPTION_MAGIC, self.NBD_OPT_GO, option_length
        )

        # Option data: export_name_length (4) + export_name + info_request_count (2)
        option_data = struct.pack(">I", len(export_name_bytes))
        option_data += export_name_bytes
        option_data += struct.pack(">H", 0)  # No specific info requests

        self.socket.send(option_header + option_data)

        # Read replies until we get ACK
        while True:
            # Read reply header (20 bytes)
            reply_header = self.socket.recv(20)
            if len(reply_header) != 20:
                raise RuntimeError(f"Short reply header: {len(reply_header)} bytes")

            reply_magic, option_id, reply_type, reply_length = struct.unpack(
                ">QIII", reply_header
            )

            if reply_magic != 0x3E889045565A9:  # NBD reply magic
                raise ValueError(f"Invalid reply magic: 0x{reply_magic:x}")

            # Read reply data if any
            reply_data = b""
            if reply_length > 0:
                reply_data = self.socket.recv(reply_length)
                if len(reply_data) != reply_length:
                    raise RuntimeError(
                        f"Short reply data: {len(reply_data)}/{reply_length} bytes"
                    )

            if reply_type == self.NBD_REP_ACK:
                # Handshake complete
                break
            elif reply_type == self.NBD_REP_INFO:
                # Parse info reply
                if len(reply_data) >= 2:
                    info_type = struct.unpack(">H", reply_data[:2])[0]
                    if info_type == self.NBD_INFO_EXPORT and len(reply_data) >= 12:
                        # Extract export size (8 bytes after 2-byte info type)
                        self.export_size = struct.unpack(">Q", reply_data[2:10])[0]
            else:
                # Handle other reply types or errors
                if reply_type >= 0x80000000:  # Error reply
                    raise RuntimeError(f"Server error: {reply_type}")

    def read(self, offset: int, length: int) -> bytes:
        """Read data from the NBD device."""
        if not self.socket:
            raise RuntimeError("Not connected to NBD server")

        if self.export_size > 0 and offset + length > self.export_size:
            raise ValueError("Read beyond end of device")

        handle = self._get_handle()

        # Send read request - the Go server expects this exact format:
        # RequestMagic (4) + Flags (2) + Type (2) + Handle (8) + Offset (8) + Length (4)
        request = struct.pack(
            ">IHHQQI",  # Note: using HH for flags+type instead of IH
            self.NBD_REQUEST_MAGIC,  # 4 bytes
            0,  # 2 bytes flags
            self.NBD_CMD_READ,  # 2 bytes type
            handle,  # 8 bytes handle
            offset,  # 8 bytes offset
            length,  # 4 bytes length
        )

        self.socket.send(request)

        # Read reply header (16 bytes)
        reply_header = self.socket.recv(16)
        if len(reply_header) != 16:
            raise RuntimeError(
                f"Short reply header: {len(reply_header)} bytes, expected 16"
            )

        reply_magic, error, reply_handle = struct.unpack(">IIQ", reply_header)

        if reply_magic != self.NBD_REPLY_MAGIC:
            raise ValueError(f"Invalid NBD reply magic: 0x{reply_magic:x}")

        if error != 0:
            raise RuntimeError(f"NBD server returned error: {error}")

        # Some NBD servers don't properly echo handles, so let's be more lenient
        # Only check handle if it's non-zero (some servers return 0)
        if reply_handle != 0 and reply_handle != handle:
            print(f"Warning: Handle mismatch: sent {handle}, got {reply_handle}")
            # Don't raise an error, just warn

        # Read data
        data = b""
        remaining = length
        while remaining > 0:
            chunk = self.socket.recv(remaining)
            if not chunk:
                raise RuntimeError(
                    f"Connection closed unexpectedly. Got {len(data)} bytes, expected {length}"
                )
            data += chunk
            remaining -= len(chunk)

        return data

    def _get_handle(self) -> int:
        """Generate a unique handle for requests."""
        self.handle_counter += 1
        return self.handle_counter

    def get_size(self) -> int:
        """Get the size of the NBD export in bytes."""
        return self.export_size

    def disconnect(self) -> None:
        """Disconnect from the NBD server."""
        if self.socket:
            try:
                # Send disconnect command
                handle = self._get_handle()
                disconnect_request = struct.pack(
                    ">IHHQQI",
                    self.NBD_REQUEST_MAGIC,
                    0,  # flags
                    self.NBD_CMD_DISC,
                    handle,
                    0,  # offset
                    0,  # length
                )

                self.socket.send(disconnect_request)
            except:
                pass  # Ignore errors during disconnect
            finally:
                self.socket.close()
                self.socket = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


if __name__ == "__main__":
    import sys

    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 10809
    export = sys.argv[3] if len(sys.argv) > 3 else "root"

    with NBDClient(host, port) as nbd:
        nbd.connect(export)

        # read the ext4 superblock
        sb = nbd.read(1024, 128)

        # get the number of block groups
        block_size = 2 ** (struct.unpack_from("<I", sb, 24)[0] + 10)
        blocks_per_group = struct.unpack_from("<I", sb, 32)[0]
        block_groups = struct.unpack_from("<I", sb, 40)[0]
        num_block_groups = (block_groups + blocks_per_group - 1) // blocks_per_group
        inode_size = struct.unpack_from("<H", sb, 88)[0]
        print(f"Block size: {block_size} bytes")
        print(f"Blocks per group: {blocks_per_group}")
        print(f"Number of block groups: {num_block_groups}")
        print(f"Inode size: {inode_size} bytes")

        # read the block group
        bg_offset = block_size
        bg = nbd.read(bg_offset, 64)
        # get the inode start block
        inode_start_block = struct.unpack_from("<I", bg, 8)[0]
        print(f"Inode start block: {inode_start_block}")

        def read_inode(num: int) -> bytes:
            inode_offset = (inode_start_block * block_size) + (inode_size * (num - 1))
            print(f"Inode offset: {inode_offset}")
            inode = nbd.read(inode_offset, inode_size)
            return inode

        def read_inode_block_and_length(num: int) -> Tuple[int, int]:
            inode = read_inode(num)

            # assume we use the new tree style
            # validate the block magic at offset 40
            block_magic = struct.unpack_from("<H", inode, 40)[0]
            if block_magic != 0xF30A:
                raise ValueError(f"Invalid block magic: 0x{block_magic:x}")
            # get the number of entries at offset 42
            num_entries = struct.unpack_from("<H", inode, 42)[0]
            print(f"Number of entries in root inode: {num_entries}")
            if num_entries != 1:
                raise ValueError(
                    f"Unexpected number of entries in root inode: {num_entries}"
                )

            # get the low block number at offset 60
            low_block_number = struct.unpack_from("<I", inode, 60)[0]
            print(f"Low block number: {low_block_number}")
            # get the length at offset 56
            length = struct.unpack_from("<I", inode, 56)[0]
            print(f"Length: {length} blocks")
            return low_block_number, length

        def read_symlink(num: int) -> str:
            inode = read_inode(num)

            # assume the symlink target is from offset 40 to 100
            symlink_target = inode[40:100].decode("utf-8").rstrip("\x00")
            print(f"Symlink target: {symlink_target}")
            return symlink_target

        def read_inode_data(num: int) -> bytes:
            """Read the directory entries for a given inode number."""
            low_block, length = read_inode_block_and_length(num)
            print(f"Reading inode data from block {low_block} with length {length}")
            # read the directory data block
            data = nbd.read(low_block * block_size, length * block_size)
            return data

        def read_directory(num: int) -> List[Tuple[int, str]]:
            dir_data = read_inode_data(num)
            entries = []
            offset = 0
            while offset < len(dir_data):
                # read the inode number at offset 0
                inode = struct.unpack_from("<I", dir_data, offset)[0]
                rec_len = struct.unpack_from("<H", dir_data, offset + 4)[0]
                name_length = struct.unpack_from("<B", dir_data, offset + 6)[0]
                if name_length == 0:
                    break
                name = dir_data[offset + 8 : offset + 8 + name_length].decode("utf-8")
                entries.append((inode, name))
                offset += rec_len
            return entries

        # read the root directory
        root_entries = read_directory(2)
        print("Root directory entries:")
        for inode, name in root_entries:
            print(f"Inode: {inode}, Name: {name}")

        # find flag.jpg
        flag_inode = next(
            (inode for inode, name in root_entries if name == "flag.jpg"), None
        )
        if flag_inode is None:
            raise ValueError("flag.jpg not found in root directory")

        flag_symlink_target = read_symlink(flag_inode)

        segments = flag_symlink_target.split("/")

        current_dir_ents = root_entries

        last_segment = segments[-1]

        for seg in segments:
            seg_inode = next(
                (inode for inode, name in current_dir_ents if name == seg), None
            )

            if seg == last_segment:
                # This is the last segment, we should read the file
                if seg_inode is None:
                    raise ValueError(f"Segment '{seg}' not found in current directory")
                flag_data = read_inode_data(seg_inode)
                with open("flag.jpg", "wb") as f:
                    f.write(flag_data)
                print("Flag data written to flag.jpg")
                break
            else:
                if seg_inode is None:
                    raise ValueError(f"Segment '{seg}' not found in current directory")
                # Read the next directory
                current_dir_ents = read_directory(seg_inode)
                print(f"Changed to directory '{seg}', entries: {current_dir_ents}")
