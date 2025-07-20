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

log "Creating credentials file to share with challengers..."
echo "[devopsadmin]" > ../publish/access_key.txt
cat terraform.tfstate | jq -r '.resources | map(select(.type == "aws_iam_access_key")) | .[].instances.[].attributes | {aws_access_key_id: .id, aws_secret_access_key: .secret} | to_entries | map("\(.key)=\(.value)")[]' >> ../publish/access_key.txt
echo "region="`grep "aws_region" terraform.tfvars | cut -f2 -d\"` >> ../publish/access_key.txt
logdone
