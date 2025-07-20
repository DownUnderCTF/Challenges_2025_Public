# Some tips to get you started 

## How do I build the challenge from source?
Run the `./build.sh` script from the handout. This will checkout the latest version
of `mpc-lib`, apply the patch, and build the necessary binaries.

## Running as a client vs running as a server
Since MPC-CMP is symmetric between parties, the `challenge` binary can be run as
both a client and a server, with the only difference being what ID each party
identifies as.

By default, `my_id` is set to SERVER_ID. This is what's running on the remote.
To connect to a server as a client instead, run with `client` passed in `argv[1]`.
```cpp
  uint64_t my_id;
  if (argc > 1 && (strcmp(argv[1], "client") == 0)) {
    my_id = CLIENT_ID;
  } else {
    my_id = SERVER_ID;
  }
```

## How do I connect to a remote over TCP?
Wrap the challenge binary with `socat`. For example, to connect a client to a
remote running at `example.com:1337` you can do the following:
```sh
socat EXEC:"./challenge client" tcp:example.com:1337
```
Using the above, `stdout` and `stdin` will be connected to the socket, whilst
`stderr` will print to the terminal for any debugging and logging you want to
do.

## How do I setup a local server instance for testing?
To stand up a server, run the binary with no arguments, and wrap the command
with `socat` like this:
```sh
socat TCP-LISTEN:1337,bind=127.0.0.1 EXEC:"./challenge"
```

Then you can connect to the local instance with
```sh
socat EXEC:"./challenge client" tcp:127.0.0.1:1337
```

## How do I see what data is being transmitted by my client?
If you want to see what is being sent by your client or local server, swap EXEC
out for SYSTEM together with `tee` like this:

```
socat TCP-LISTEN:1337,bind=127.0.0.1 SYSTEM:"./challenge | tee /dev/tty"
socat SYSTEM:"./challenge client | tee /dev/tty" tcp:127.0.0.1:1337
```

