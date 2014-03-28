# BSDPy
#
# Version 0.1

FROM douglasmiranda/python-base

RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN apt-get update

RUN git clone https://bitbucket.org/bruienne/bsdpy.git -b http
RUN git clone https://github.com/bruienne/pydhcplib.git
RUN cd ~/pydhcplib; python setup.py install
RUN pip install docopt
RUN mkdir /nbi
ADD IzzyBoot-10.9-13A3017.nbi /nbi/NI.nbi/

# RUN apt-get -y install tcpdump iptables
# RUN wget --no-check-certificate https://raw.github.com/jpetazzo/pipework/master/pipework
# RUN chmod +x pipework
# CMD \
    # echo Setting up iptables... &&\
    # iptables -t nat -A POSTROUTING -j MASQUERADE &&\
    # echo Waiting for pipework to give us the eth1 interface... &&\
    # /pipework --wait &&\
    # echo Starting BSDP server...&&\
    # /bsdpy/bsdpserver-http.py -i eth1

EXPOSE 67/UDP
EXPOSE 68/UDP

ENTRYPOINT ["/bsdpy/bsdpserver-http.py"]
CMD	["-i", "eth1"]
