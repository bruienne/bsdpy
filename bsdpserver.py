#!/usr/bin/python
################################################################################
# Copyright 2013 The Regents of the University of Michigan
# 
#  Licensed under the Apache License, Version 2.0 (the "License"); you may not
#  use this file except in compliance with the License. You may obtain a copy of
#  the License at  
# 
#       http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations under
#  the License.
# ##############################################################################
#
# BSDPy - A BSDP NetBoot server implemented in Python - v0.1a
#
#   Author: Pepijn Bruienne - University of Michigan - bruienne@umich.edu
#
# Extremely alpha, beware ye mortals - dragons be here...
#
# Requirements:
#
# - Python 2.5 or later. Not tested with Python 3.
#
# - A Linux distribution that supports:
#   Python 2.5 or later
#   NFS service
#   TFTP service
#
#   Tested on CentOS 6.4 and Ubuntu Precise
#
# - Working installation of this fork of the pydhcplib project:
#
#   $ git clone https://github.com/bruienne/pydhcplib.git
#   $ cd pydhcplib
#   $ sudo python setup.py install
#
#   The fork contains changes made to the names of DHCP options 43 and 60 which
#   are used in BSDP packets. The original library used duplicate names for
#   options other than 43 and 60 which breaks our script when they are looked
#   up through dhcp_constants.py.
#
# - Working DNS:
#   TFTP uses the DHCP 'sname' option to download the booter (kernel) - having
#   at least functioning forward DNS for the hostname in 'sname' is therefore
#   required. In a typical situation this would be the same server running the
#   BSDPy process, but this is not required. Just make sure that wherever TFTP
#   is running has working DNS lookup.
#
# - Root permissions. Due to its need to write to use raw sockets elevated
#   privileges are required. When run as a typical system service through init
#   or upstart this should not be an issue.
#

from pydhcplib.dhcp_packet import *
from pydhcplib.dhcp_network import *

import socket, struct, fcntl
import os, fnmatch
import plistlib

bsdpoptioncodes = {1: 'message_type',
                   2: 'version',
                   3: 'server_identifier',
                   4: 'server_priority',
                   5: 'reply_port',
                   6: 'image_icon_unused',
                   7: 'default_boot_image',
                   8: 'selected_boot_image',
                   9: 'boot_image_list',
                   10: 'netboot_v1',
                   11: 'boot_image_attributes',
                   12: 'max_message_size'}

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sockfd = sock.fileno()
SIOCGIFADDR = 0x8915


def get_ip(iface=''):
    ifreq = struct.pack('16sH14s', iface, socket.AF_INET, '\x00' * 14)
    try:
        res = fcntl.ioctl(sockfd, SIOCGIFADDR, ifreq)
    except:
        return None
    ip = struct.unpack('16sH2x4s8x', res)[2]
    return socket.inet_ntoa(ip)


if len(sys.argv) > 1:
    tftprootpath = sys.argv[1]
    print 'Using ' + tftprootpath + ' as root path'
else:
    tftprootpath = '/nbi'
    print 'Using ' + tftprootpath + ' as root path'

try:
    serverip = map(int, get_ip('eth0').split('.'))
    serverhostname = socket.gethostname()
    nfsrootpath = 'nfs:' + get_ip('eth0') + ':' + tftprootpath + ':'
except:
    print 'Error setting serverip, serverhostname or nfsrootpath', sys.exc_info()
    raise

netopt = {'client_listen_port':"68",
           'server_listen_port':"67",
           'listen_address':"0.0.0.0"}


class Server(DhcpServer):
    def __init__(self, options):
        DhcpServer.__init__(self,options["listen_address"],
                                 options["client_listen_port"],
                                 options["server_listen_port"])
    
    def HandleDhcpInform(self, packet):
        return packet


def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


def getnbioptions(incoming):
    nbioptions = []
    nbisources = []
    try:
        for path, dirs, files in os.walk(incoming):
            thisnbi = {}
            if path.count(os.sep) >= 2:
                del dirs[:]
                
                nbisources.append(path)
                
                nbimageinfoplist = find('NBImageInfo.plist', path)[0]
                nbimageinfo = plistlib.readPlist(nbimageinfoplist)
                
                thisnbi['dmg'] = '/'.join(find('*.dmg', path)[0].split('/')[2:])
                thisnbi['booter'] = find('booter', path)[0]
                thisnbi['id'] = nbimageinfo['Index']
                thisnbi['name'] = nbimageinfo['Name']
                thisnbi['isdefault'] = nbimageinfo['IsDefault']
                thisnbi['length'] = len(nbimageinfo['Name'])
                
                nbioptions.append(thisnbi)
    except:
        print "Unexpected error:", sys.exc_info()
        raise

    print 'Boot images used in this session:\n************************************'
    for nbi in nbisources:
        print nbi
        
    return nbioptions


def parseoptions(bsdpoptions):
    optionvalues = {}
    msgtypes = {}
    pointer = 0
    
    while pointer < len(bsdpoptions):
        start = pointer
        length = pointer + 1
        optionlength = bsdpoptions[length]
        pointer = optionlength + length + 1
        
        msgtypes[bsdpoptioncodes[bsdpoptions[start]]] = [length+1, bsdpoptions[length]]
    
    for msg, values in msgtypes.items():
        start = values[0]
        end = start + values[1]
        options = bsdpoptions[start:end]
        
        optionvalues[msg] = options
    
    return optionvalues


def ack(packet, msgtype, nbiimages):
    """docstring for createlistack"""
    
    bsdpack = DhcpPacket()
    
    try:
        bsdpoptions = parseoptions(packet.GetOption('vendor_encapsulated_options'))

        if 'reply_port' in bsdpoptions:
            replyport = int(str(format(bsdpoptions['reply_port'][0], 'x') + format(bsdpoptions['reply_port'][1], 'x')), 16)
        else:
            replyport = 68
        
        clientip = ipv4(packet.GetOption('ciaddr'))
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
    
    bsdpack.SetOption("op", [2])
    bsdpack.SetOption("htype", packet.GetOption('htype'))
    bsdpack.SetOption("hlen", packet.GetOption('hlen'))
    bsdpack.SetOption("xid", packet.GetOption('xid'))
    bsdpack.SetOption("ciaddr", packet.GetOption('ciaddr'))
    bsdpack.SetOption("siaddr", serverip)
    bsdpack.SetOption("yiaddr", [0,0,0,0])
    bsdpack.SetOption("sname", strlist(serverhostname.ljust(64,'\x00')).list())
    bsdpack.SetOption("chaddr", packet.GetOption('chaddr'))
    bsdpack.SetOption("dhcp_message_type", [5])
    bsdpack.SetOption("server_identifier", serverip)
    bsdpack.SetOption("vendor_class_identifier", strlist('AAPLBSDPC').list())
    
    if msgtype == 'list':
        nameslength = 0
        
        for i in nbiimages:
            nameslength += i['length']
        
        totallength = len(nbiimages) * 5 + nameslength
        bsdpimagelist = [9,totallength]
        imagenameslist = []
        defaultnbi = 0
        
        try:
            for image in nbiimages:
                if image['isdefault'] is True:
                    if defaultnbi < image['id']:
                        defaultnbi = image['id']

                imageid = '%04X' % image['id']
                n = 2
                imageid = [int(imageid[i:i+n], 16) for i in range(0, len(imageid), n)]
                imagenameslist += [129,0] + imageid + [image['length']] + strlist(image['name']).list()
        except:
            print "Unexpected error:", sys.exc_info()
            raise
        
        bsdpimagelist += imagenameslist
        
        defaultnbi = '%04X' % defaultnbi
        defaultnbi = [7,4,129,0] + [int(defaultnbi[i:i+n], 16) for i in range(0, len(defaultnbi), n)]
        
        bsdpack.SetOption("vendor_encapsulated_options", strlist([1,1,1,4,2,128,128] + defaultnbi + bsdpimagelist).list())
        
        print '================================================================='
        print "Return ACK[LIST] to " + str(clientip) + ' on ' + str(replyport)
        print "Default boot image ID: " + str(defaultnbi)
    
    elif msgtype == 'select':
        try:
            imageid = int('%02X' % bsdpoptions['selected_boot_image'][2] + '%02X' % bsdpoptions['selected_boot_image'][3], 16)
        except:
            print "Unexpected error:", sys.exc_info()
            raise
        
        booterfile = ''
        rootpath = ''
        
        for nbidict in nbiimages:
            try:
                if nbidict['id'] == imageid:
                    booterfile = nbidict['booter']
                    rootpath = nfsrootpath + nbidict['dmg']
                    selectedimage = bsdpoptions['selected_boot_image']
            except:
                print "Unexpected error:", sys.exc_info()
                raise
        
        bsdpack.SetOption("file", strlist(os.path.join(*booterfile.split('/')[2:]).ljust(128,'\x00')).list())
        bsdpack.SetOption("root_path", strlist(rootpath).list())
        bsdpack.SetOption("vendor_encapsulated_options", strlist([1,1,2,8,4] + selectedimage).list())
        
        print '================================================================='
        print "Return ACK[SELECT] to " + str(clientip) + ' on ' + str(replyport)

    return bsdpack, clientip, replyport


def main():
    """Main routine. Do the work."""
    
    server = Server(netopt)
    nbiimages = getnbioptions(tftprootpath)
    
    while True:
        
        packet = server.GetNextDhcpPacket()
        
        try:
            if len(packet.GetOption('vendor_encapsulated_options')) > 1:
                if packet.GetOption('vendor_encapsulated_options')[2] == 1:
                    print '********************************************************'
                    print 'Got BSDP INFORM[LIST] packet: '
                    
                    bsdplistack, clientip, replyport = ack(packet, 'list', nbiimages)
                    server.SendDhcpPacketTo(bsdplistack, str(clientip), replyport)
                
                elif packet.GetOption('vendor_encapsulated_options')[2] == 2:
                    print '********************************************************'
                    print 'Got BSDP INFORM[SELECT] packet: '
                    
                    bsdpselectack, selectackclientip, selectackreplyport = ack(packet, 'select', nbiimages)
                    server.SendDhcpPacketTo(bsdpselectack, str(selectackclientip), selectackreplyport)
                
                elif len(packet.GetOption('vendor_encapsulated_options')) <= 7:
                    pass
        except:
            pass

if __name__ == '__main__':
    main()
