<?php
echo hash_hmac('sha256', urldecode(urldecode($argv[2])), $argv[1]);