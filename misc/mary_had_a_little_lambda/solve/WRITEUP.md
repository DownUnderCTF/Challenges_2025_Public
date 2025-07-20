M.A.R.Y Had A Little Lambda
============

As is often the case with Cloud, excessively permissive permissions are in place here, and lead to security issues.

The architecture here is pretty simple; we have a single Lambda function written in Python, which simply connects to a
MySQL database (that doesn't actually exist for this challenge). The credentials required for this connection are securely
stored in an encrypted SSM Parameter.  In order to use Lamdbas you need a role that the function will assume to do it's
thing, which in this case really only needs to basic permissions to access the param.

However, this role has been opened up to allow the admin user to assume it, which is the main issue to exploit here.

The main challenge is to find where the flag is hidden, which requires discovering the environment. Unfortunately, the permissions you need to do this successfully are split between the admin user and the lambda role, so this adds a bit of complexity.

See `solve.sh` for the full solution, but in summary you'll need to:

- Configure the AWS CLI to use the provided devopsadmin user creds
- Use [GetFunction](https://docs.aws.amazon.com/cli/latest/reference/lambda/get-function.html
) to pull the source code for the Lambda function
- Examine the code to find the name of the SSM param that contains the password
- Assume the lamdba role
- Fetch the param, requesting decryption. The param value is the flag.

### Learnings
- Always use least privilege for users and roles. Avoid overloading permissions for 
multiple uses. In this case, MARY added permissions to the `lambda_role` to allow for
administration - this should have been setup as a different role with the least amount
of privilege.
- Avoid using long-term credentials like AWS access keys. For administration, use
[short-term credentials](https://docs.aws.amazon.com/IAM/latest/UserGuide/security-creds-programmatic-access.html) tied to a least privilege role. Don't leak creds publicly, but if some goose does and they're short term ones, you have a smaller window of exposure.
- Consider using customer managed KMS keys to encrypt secrets. MARY set the SSM param as type `SecureString` which encrypts the value, but used the default [AWS managed key](https://docs.aws.amazon.com/systems-manager/latest/userguide/secure-string-parameter-kms-encryption.html) `aws/ssm` rather than their own. This key is accessible by all principals within the account that the key exists, does not log usage, and is not able to be rotated adhoc if needed ([reference](https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html)). By using a custom key, you have to pay for it (though not much), but you get to provide finer grain access policies, an audit trail if things go wrong, and the ability to rotate it if and when needed.
- At least for the challenge author, [lots of things about yaks](https://en.wikipedia.org/wiki/Yak). 🐂 
