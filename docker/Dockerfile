# BSDPy Dockerfile
# Installs and prepares BSDPy to run inside a Docker container
# Project home: https://bitbucket.org/bruienne/bsdpy
# Version 0.1

FROM douglasmiranda/python-base
MAINTAINER Pepijn Bruienne "bruienne@umich.edu"

ENV DOCKER_BSDPY_IFACE eth0
ENV DOCKER_BSDPY_PROTO http

RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN apt-get update
RUN dpkg-divert --local --rename --add /sbin/initctl
RUN ln -s /bin/true /sbin/initctl
RUN apt-get install -y apt-utils dialog nginx tftpd-hpa

RUN git clone https://bitbucket.org/bruienne/bsdpy.git
RUN git clone https://github.com/bruienne/pydhcplib.git
RUN cd ~/pydhcplib; python setup.py install
RUN pip install docopt
RUN mkdir /nbi

ADD IzzyBoot-10.9-13A3017.nbi /nbi/NI.nbi/
ADD nginx.conf /etc/nginx/nginx.conf
ADD start.sh /start.sh

RUN chown -R root:root /nbi/NI.nbi && \
    chown -R root:root /etc/nginx/nginx.conf && \
    chown -R root:root start.sh
RUN chmod +x start.sh

EXPOSE 67/udp
EXPOSE 68/udp
EXPOSE 69/udp
EXPOSE 80

ENTRYPOINT ["/start.sh"]
