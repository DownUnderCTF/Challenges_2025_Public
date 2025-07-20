
If completely clueless
1. Look at how the authentication token is created, does anything look sus?

If still stuck
2. How long can an email be? could there be an issue if it’s too long.

NOTE FOR DUNDERS: above hint is supposed to make them spot the int overflow reading the email length and realising when that occurs you can overwrite the rest of the authentication token.

if noticed the overflow, but struggling with exploitation
3. Use the provided unit tests to help build your exploit or try testing your payload locally while using a debugger. Be aware that if you provide invalid characters the `golang` JSON unmarshalling will cause additional bytes being inadvertently added to the email.