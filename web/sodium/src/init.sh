#!/bin/bash
service nginx start
# Start pound in background
/usr/local/sbin/pound -f /usr/local/etc/pound.cfg &

# Start the RPC backend as the correct user
su - rpcservice -c "cd /home/rpcservice/rpc_service && /usr/local/bin/python3 server.py &"

# Start customer app
su - customerapp -c "cd /home/customerapp/customer_app && /usr/local/bin/python3 run.py"