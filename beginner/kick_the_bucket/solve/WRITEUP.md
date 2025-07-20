Kick the (S3) Bucket
============

The admins gave it a shot, but their logic was flawed! As you can see in
the resource policy, they have "locked down" access to the S3 bucket with a
condition that looks for user-agents that begin with "aws-sdk-go". This
matches the user-agent used when Terraform makes changes in AWS, because
it is written in Go using the AWS SDK (you'll usually see something like
`aws-sdk-go/1.1.0 (go1.5.2; darwin; amd64)`). This logic is flawed though,
since user-agents are trivial to change client side when making requests!

The solution here is simply to fetch the presigned URL for `flag.txt` with
any user agent starting with "aws-sdk-go".

```
curl `cat s3_presigned_url.txt` --user-agent aws-sdk-go-blah
```

### Learnings
- Never blindly trust values able to be manipulated client side. In this case
it's the User Agent, but this rule applies to any parameter.
- AWS S3 presigned URLs are bound to the user who generated them, so any access
this user has will apply to access via the presigned URL. If you access the URL
without specifying the custom UA, note that the error contains *"user/pipeline
is not authorized to perform s3:GetObject"*, since the pipeline user created the
URL.
- While presigned URLs are a good way to securely share access to files and
data in S3, this doesn't mean you don't have to be careful and make sure your
IAM polices are least privilege!