#!/bin/bash

redis-cli SET admin "${ADMIN_TOKEN}";
unset ADMIN_TOKEN;