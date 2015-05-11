#!/bin/sh -x

/usr/bin/env python /bsdpy/bsdpserver.py &

tail -f /var/log/bsdpserver.log
