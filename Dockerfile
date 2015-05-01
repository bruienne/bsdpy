# Minimal Dockerfile based on python:2-slim

FROM python:2-slim
MAINTAINER "Pepijn Bruienne" bruienne@gmail.com

ENV BSDPY_IFACE eth0
ENV BSDPY_IP 127.0.0.1
ENV BSDPY_PROTO http

RUN /bin/mkdir /bsdpy
RUN /bin/touch /var/log/bsdpserver.log

ADD start.sh /
ADD bsdpserver.py /bsdpy/
ADD __init__.py /bsdpy/
ADD pydhcplib /bsdpy/pydhcplib
ADD requirements.txt /

RUN pip install -r requirements.txt
RUN /bin/chmod +x /start.sh /bsdpy/bsdpserver.py

VOLUME /nbi

CMD /start.sh
