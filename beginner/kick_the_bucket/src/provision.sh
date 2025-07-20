#!/bin/sh
set -e

log () {
    printf "\n[`date "+%Y/%m/%d %H:%M:%S"`] #--> \033[0;38;5;214m$1"
}

logdone () {
    printf " Done!\033[0m\n"
}

log "Creating/updating TF stack...\n"
terraform apply -auto-approve \
    -var challenge_name="`yq eval '.name' ../ctfcli.yaml`" \
    -var flag="`yq eval '.flags[0]' ../ctfcli.yaml`"
logdone

log "Exporting S3 resource policy to share with challengers..."
terraform output | tail -n+2 | sed -e '$d' > ../publish/s3_resource_policy.txt
logdone