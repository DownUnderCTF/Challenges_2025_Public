#!/bin/sh

terraform destroy -auto-approve \
    -var challenge_name="`yq eval '.name' ../ctfcli.yaml`" \
    -var flag="`yq eval '.flags[0]' ../ctfcli.yaml`"

