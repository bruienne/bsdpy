#!/bin/bash
service nginx start
/usr/sbin/in.tftpd -l --permissive /nbi
cd /bsdpy
git pull
./bsdpserver.py -i ${BSDPY_IFACE} -r ${BSDPY_PROTO} &
sleep 2
tail -f /var/log/bsdpserver.log
