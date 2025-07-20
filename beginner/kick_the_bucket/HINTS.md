### Hint 1:
Look closely at the access policy of the bucket, which is what is preventing you from accessing the flag file when you browse to the URL provided. What condition must be met for successful access?

### Hint 2:
The access policy requires a specific `aws:UserAgent` value, which is that provided by the caller in the HTTP header of the request. In an AWS policy, `*` is a wildcard character that matches any values that come after it. How can you modify your web request to make the User Agent match the required value?

### Hint 3:
Take a look at the command line utility `curl`, which allows you to send a web request without a browser. The `--user-agent` parameter looks interesting, as it allows you to modify the User Agent HTTP header of the request.