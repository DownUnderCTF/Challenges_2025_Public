{name}
============

Short writeup for backdoor:
- Read the LSTAR MSR to leak entry_SYSCALL_64.
- calculate kernel base from this leak.
- get init_task, and iterate the task list until we find out current process
- read its cred struct out of its task struct and write the uid/gid/etc to 0
- return to userland
- signal handler is setup to unscrew the pagetables etc
- read flag
