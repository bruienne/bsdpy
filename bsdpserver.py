#!/usr/bin/python
################################################################################
# Copyright 2015 The Regents of the University of Michigan
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
# BSDPy - A BSDP NetBoot server implemented in Python - v0.5b
#
#   Author: Pepijn Bruienne - University of Michigan - bruienne@umich.edu
#
# Reasonably stable, test before using in production - you know the drill...
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
from urlparse import urlparse

import socket, struct, fcntl
import os, fnmatch
import plistlib
import logging, optparse
import signal, errno
from docopt import docopt

platform = sys.platform

usage = """Usage: bsdpyserver.py [-p <path>] [-r <protocol>] [-i <interface>]

Run the BSDP server and handle requests from client. Optional parameters are
the root path to serve NBIs from, the protocol to serve them with and the
interface to run on.

Options:
 -h --help               This screen.
 -p --path <path>        The path to serve NBIs from. [default: /nbi]
 -r --proto <protocol>   The protocol to serve NBIs with. [default: http]
 -i --iface <interface>  The interface to bind to. [default: eth0]
"""

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
                    level=logging.DEBUG,
                    filename='/var/log/bsdpserver.log',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


# A dict that holds mappings of the BSDP option codes for lookup later on
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

# Some standard DHCP/BSDP options to set listen, server ports and what IP
#   address to listen on. Default is 0.0.0.0 which means all requests are
#   replied to if they are a BSDP[LIST] or BSDP[SELECT] packet.
netopt = {'client_listen_port':"68",
           'server_listen_port':"67",
           'listen_address':"0.0.0.0"}


def get_ip(iface=''):
    """
        The get_ip function retrieves the IP for the network interface BSDPY
        is running on.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockfd = sock.fileno()
    SIOCGIFADDR = 0x8915

    ifreq = struct.pack('16sH14s', iface, socket.AF_INET, '\x00' * 14)
    try:
        res = fcntl.ioctl(sockfd, SIOCGIFADDR, ifreq)
    except:
        return None
    ip = struct.unpack('16sH2x4s8x', res)[2]
    return socket.inet_ntoa(ip)

arguments = docopt(usage, version='0.0.1')

# Set the root path that NBIs will be served out of, either provided at
#  runtime or using a default if none was given. Defaults to /nbi.

tftprootpath = arguments['--path']
bootproto = arguments['--proto']
serverinterface = arguments['--iface']

# Get the server IP and hostname for use in in BSDP calls later on.
try:
    if os.environ.get('DOCKER_BSDPY_IP'):
        externalip = os.environ.get('DOCKER_BSDPY_IP')
        serverhostname = externalip
        serverip = map(int, externalip.split('.'))
        serverip_str = externalip
        logging.debug('Found $DOCKER_BSDPY_IP - using custom external IP %s'
                        % externalip)
    elif 'darwin' in platform:
        from netifaces import ifaddresses
        logging.debug('Running on OS X, using alternate netifaces method')
        myip = ifaddresses(serverinterface)[2][0]['addr']
        serverhostname = myip
        serverip = map(int, myip.split('.'))
        serverip_str = myip
    else:
        myip = get_ip(serverinterface)
        serverhostname = myip
        serverip = map(int, myip.split('.'))
        serverip_str = myip
        logging.debug('No BSDPY_IP env var found, using IP from %s interface'
                        % serverinterface)
    if 'http' in bootproto:
        if os.environ.get('DOCKER_BSDPY_NBI_URL'):
            nbiurl = urlparse(os.environ.get('DOCKER_BSDPY_NBI_URL'))
            nbiurlhostname = nbiurl.hostname

            # EFI bsdp client doesn't do DNS lookup, so we must do it
            try:
                socket.inet_aton(nbiurlhostname)
            except socket.error:
                nbiurlhostname = socket.gethostbyname(nbiurlhostname)
                logging.debug('Resolving hostname to IP - %s -> %s' % (nbiurl.hostname, nbiurlhostname))

            basedmgpath = 'http://%s%s/' % (nbiurlhostname, nbiurl.path)
            logging.debug('Found DOCKER_BSDPY_NBI_URL - using basedmgpath %s' % basedmgpath)
        else:
            basedmgpath = 'http://' + serverip_str + '/'
            logging.debug('Using HTTP basedmgpath %s' % basedmgpath)
    if 'nfs' in bootproto:
        basedmgpath = 'nfs:' + serverip_str + ':' + tftprootpath + ':'
        logging.debug('Using NFS basedmgpath %s' % basedmgpath)
    logging.debug('Server IP: ' + serverip_str + '\n' +
                  'Server FQDN: ' + serverhostname + '\n' +
                  'Serving on ' + serverinterface + '\n' +
                  'Using ' + bootproto + ' to serve boot image.\n')
except:
    logging.debug('Error setting serverip, serverhostname or basedmgpath %s' %
                    sys.exc_info()[1])
    raise


def getBaseDmgPath(nbiurl) :

    logging.debug('*********\nRefreshing basedmgpath because DOCKER_BSDPY_NBI_URL uses hostname, not IP')
    if 'http' in bootproto:
        if os.environ.get('DOCKER_BSDPY_NBI_URL'):
            nbiurlhostname = nbiurl.hostname

            # EFI bsdp client doesn't do DNS lookup, so we must do it
            try:
                socket.inet_aton(nbiurlhostname)
            except socket.error:
                nbiurlhostname = socket.gethostbyname(nbiurlhostname)
                logging.debug('Resolving hostname to IP - %s -> %s' % (nbiurl.hostname, nbiurlhostname))

            basedmgpath = 'http://%s%s/' % (nbiurlhostname, nbiurl.path)
            logging.debug('Found DOCKER_BSDPY_NBI_URL - using basedmgpath %s\n*********\n' % basedmgpath)
        else:
            basedmgpath = 'http://' + serverip_str + '/'
            logging.debug('Using HTTP basedmgpath %s\n*********\n' % basedmgpath)

    if 'nfs' in bootproto:
        basedmgpath = 'nfs:' + serverip_str + ':' + tftprootpath + ':'
        logging.debug('Using NFS basedmgpath %s' % basedmgpath)

    return basedmgpath

# Invoke the DhcpServer class from pydhcplib and configure it, overloading the
#   available class functions to only listen to DHCP INFORM packets, which is
#   what BSDP uses to do its thing - HandleDhcpInform().
# http://www.opensource.apple.com/source/bootp/bootp-268/Documentation/BSDP.doc


class DhcpServer(DhcpNetwork) :
    def __init__(self, listen_address="0.0.0.0",
                    client_listen_port=68,server_listen_port=67) :

        DhcpNetwork.__init__(self,
                            listen_address,
                            server_listen_port,
                            client_listen_port)

        self.EnableBroadcast()
        if 'darwin' in platform:
            self.EnableReuseaddr()
        else:
            self.DisableReuseaddr()

        self.CreateSocket()
        self.BindToAddress()


class Server(DhcpServer):
    def __init__(self, options):
        DhcpServer.__init__(self,options["listen_address"],
                                 options["client_listen_port"],
                                 options["server_listen_port"])

    def HandleDhcpInform(self, packet):
        return packet


def find(pattern, path):
    """
        The find() function provides some basic file searching, used later
        to look for available NBIs.
    """
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


def chaddr_to_mac(chaddr):
    """Convert the chaddr data from a DhcpPacket Option to a hex string
    of the form '12:34:56:ab:cd:ef'"""
    return ":".join(hex(i)[2:] for i in chaddr[0:6])


def getNbiOptions(incoming):
    """
        The getNbiOptions() function walks through a given directory and
        finds and parses compatible NBIs by looking for NBImageInfo.plist
        files which are then processed with plistlib to extract an NBI's
        configuration items that are needed later on to send to BSDP clients.

        It is assumed that the NBI root directory is laid out as follows:
            /nbi/MyGreatImage.nbi
            /nbi/AnotherNetBootImage.nbi
    """
    # Initialize lists to store NBIs and their options
    nbioptions = []
    nbisources = []
    try:
        for path, dirs, files in os.walk(incoming):
            # Create an empty dict that will hold an NBI's settings
            thisnbi = {}
            if os.path.splitext(path)[1] == '.nbi':
                del dirs[:]

                # Search the path for an NBImageInfo.plist and parse it.
                logging.debug('Considering NBI source at ' + str(path))
                nbimageinfoplist = find('NBImageInfo.plist', path)[0]
                nbimageinfo = plistlib.readPlist(nbimageinfoplist)

                # Pull NBI settings out of the plist for use later on:
                #   booter = The kernel which is loaded with tftp
                #   disabledsysids = System IDs to blacklist, optional
                #   dmg = The actual OS image loaded after the booter
                #   enabledsysids = System IDs to whitelist, optional
                #   enabledmacaddrs = Enabled MAC addresses to whitelist, optional
                #                     (and for which a key may not exist in)
                #   id = The NBI Identifier, must be unique
                #   isdefault = Indicates the NBI is the default
                #   length = Length of the NBI name, needed for BSDP packet
                #   name = The name of the NBI

                if nbimageinfo['Index'] == 0:
                    logging.debug('Image "%s" Index is NULL (0), skipping!'
                                    % nbimageinfo['Name'])
                    continue
                elif nbimageinfo['IsEnabled'] is False:
                    logging.debug('Image "%s" is disabled, skipping.'
                                    % nbimageinfo['Name'])
                    continue
                else:
                    thisnbi['id'] = nbimageinfo['Index']

                thisnbi['booter'] = \
                    find('booter', path)[0]
                thisnbi['description'] = \
                    nbimageinfo['Description']
                thisnbi['disabledsysids'] = \
                    nbimageinfo['DisabledSystemIdentifiers']
                thisnbi['dmg'] = \
                    '/'.join(find('*.dmg', path)[0].split('/')[2:])

                thisnbi['enabledmacaddrs'] = \
                    nbimageinfo.get('EnabledMACAddresses', [])
                # EnabledMACAddresses must be lower-case - Apple's tools create them
                # as such, but in case they aren't..
                thisnbi['enabledmacaddrs'] = [mac.lower() for mac in
                                              thisnbi['enabledmacaddrs']]

                thisnbi['enabledsysids'] = \
                    nbimageinfo['EnabledSystemIdentifiers']
                thisnbi['isdefault'] = \
                    nbimageinfo['IsDefault']
                thisnbi['length'] = \
                    len(nbimageinfo['Name'])
                thisnbi['name'] = \
                    nbimageinfo['Name']
                thisnbi['proto'] = \
                    nbimageinfo['Type']


                # Add the parameters for the current NBI to nbioptions
                nbioptions.append(thisnbi)
                # Found an eligible NBI source, add it to our nbisources list
                nbisources.append(path)
    except:
        logging.debug("Unexpected error getNbiOptions: %s" %
                        sys.exc_info()[1])
        raise

    return nbioptions, nbisources


def getSysIdEntitlement(nbisources, clientsysid, clientmacaddr, bsdpmsgtype):
    """
        The getSysIdEntitlement function takes a list of previously compiled NBI
        sources and a clientsysid parameter to determine which of the entries in
        nbisources the clientsysid is entitled to.

        The function:
        - Initializes the 'hasdupes' variable as False.
        - Checks for an enabledmacaddrs value:
            - If an empty list, no filtering is performed
            - It will otherwise contain one or more MAC addresses, and thisnbi
              will be skipped if the client's MAC address is not in this list.
            - Apple's NetInstall service also may create a "DisabledMACAddresses"
              blacklist, but this never seems to be used.
        - Checks for duplicate clientsysid entries in enabled/disabledsysids:
            - If found, there is a configuration issue with
              NBImageInfo.plist and thisnbi is skipped; a warning
              is thrown for the admin to act on. The hasdupes variable will be
              set to True.
        - Checks if hasdupes is False:
            - If True, continue with the tests below, otherwise iterate next.
        - Checks for empty disabledsysids and enabledsysids lists:
            - If both lists are zero length thisnbi is added to nbientitlements.
        - Checks for a missing clientsysid entry in enabledsysids OR a matching
          clientsysid entry in disabledsysids:
            - If if either is True thisnbi is skipped.
        - Checks for matching clientsysid entry in enabledsysids AND a missing
          clientsysid entry in disabledsysids:
            - If both are True thisnbi is added to nbientitlements.
    """

    # Globals are used to give other functions access to these later
    global defaultnbi
    global imagenameslist
    global hasdefault

    logging.debug('Determining image list for system ID ' + clientsysid)

    # Initialize lists for nbientitlements and imagenameslist, both will
    #   contain a series of dicts
    nbientitlements = []
    imagenameslist = []

    try:
        # Iterate over the NBI list
        for thisnbi in nbisources:

            # First a sanity check for duplicate system ID entries
            hasdupes = False

            if clientsysid in thisnbi['disabledsysids'] and \
               clientsysid in thisnbi['enabledsysids']:

                # Duplicate entries are bad mkay, so skip this NBI and warn
                logging.debug('!!! Image "' + thisnbi['description'] +
                        '" has duplicate system ID entries '
                        'for model "' + clientsysid + '" - skipping !!!')
                hasdupes = True

            # Check whether both disabledsysids and enabledsysids are empty and
            #   if so add the NBI to the list, there are no restrictions.
            if not hasdupes:
                # If the NBI had a non-empty EnabledMACAddresses array present,
                # skip this image if this client's MAC is not in the list.
                if thisnbi['enabledmacaddrs'] and \
                    clientmacaddr not in thisnbi['enabledmacaddrs']:
                    logging.debug('MAC address ' + clientmacaddr + ' is not '
                                  'in the enabled MAC list - skipping "' +
                                  thisnbi['description'] + '"')
                    continue

                if len(thisnbi['disabledsysids']) == 0 and \
                   len(thisnbi['enabledsysids']) == 0:
                    logging.debug('Image "' + thisnbi['description'] +
                            '" has no restrictions, adding to list')
                    nbientitlements.append(thisnbi)

                # Check for a missing entry in enabledsysids, this means we skip
                elif clientsysid in thisnbi['disabledsysids']:
                    logging.debug('System ID "' + clientsysid + '" is disabled'
                                    ' - skipping "' + thisnbi['description'] + '"')

                # Check for an entry in enabledsysids
                elif clientsysid not in thisnbi['enabledsysids'] or \
                     (clientsysid in thisnbi['enabledsysids'] and
                     clientsysid not in thisnbi['disabledsysids']):
                    logging.debug('Found enabled system ID ' + clientsysid +
                          ' - adding "' + thisnbi['description'] + '" to list')
                    nbientitlements.append(thisnbi)

    except:
        logging.debug("Unexpected error filtering image entitlements: %s" %
                        sys.exc_info()[1])
        raise

    try:
        # Now we iterate through the entitled NBIs in search of a default
        #   image, as determined by its "IsDefault" key
        for image in nbientitlements:

            # Check for an isdefault entry in the current NBI
            if image['isdefault'] is True:
                logging.debug('Found default image ID ' + str(image['id']))

                # By default defaultnbi is 0, so change it to the matched NBI's
                #   id. If more than one is found (shouldn't) we use the highest
                #   id found. This behavior may be changed if it proves to be
                #   problematic, such as breaking out of the for loop instead.
                if defaultnbi < image['id']:
                    defaultnbi = image['id']
                    hasdefault = True
                    # logging.debug('Setting default image ID ' + str(defaultnbi))
                    # logging.debug('hasdefault is: ' + str(hasdefault))

            # This is to match cases where there is  no default image found,
            #   a possibility. In that case we use the highest found id as the
            #   default. This too could be changed at a later time.
            elif not hasdefault:
                if defaultnbi < image['id']:
                    defaultnbi = image['id']
                    # logging.debug('Changing default image ID ' + str(defaultnbi))

            # Next we construct our imagenameslist which is a list of ints that
            #   encodes the image id, total name length and its name for use
            #   by the packet encoder

            # The imageid should be a zero-padded 4 byte string represented as
            #   ints
            imageid = '%04X' % image['id']

            # Our skip interval within the list; the "[129,0]" header each image
            #   ID requires, we don't want to count it for the length
            n = 2

            # Construct the list by iterating over the imageid, converting to a
            #   16 bit string as we go, for proper packet encoding
            imageid = [int(imageid[i:i+n], 16) \
                for i in range(0, len(imageid), n)]
            imagenameslist += [129,0] + imageid + [image['length']] + \
                              strlist(image['name']).list()
    except:
        logging.debug("Unexpected error setting default image: %s" %
                        sys.exc_info()[1])
        raise

    # print 'Entitlements: ' + str(len(nbientitlements)) + '\n' + str(nbientitlements) + '\n'
    # print imagenameslist

    # All done, pass the finalized list of NBIs the given clientsysid back
    return nbientitlements


def parseOptions(bsdpoptions):
    """
        The parseOptions function parses a given bsdpoptions list and decodes
        the BSDP options contained within, giving them the proper names that
        pydhcplib expects. References the bsdpoptioncodes dict that was defined
        earlier on.
    """
    optionvalues = {}
    msgtypes = {}
    pointer = 0

    # Using a pointer we step through the given bsdpoptions. These are raw DHCP
    #   packets we are decoding so this looks incredibly laborious, but the
    #   input is a 16 bit list of encoded strings and options that needs to be
    #   diced up according to the BSDP option encoding as set forth in the
    #   Apple BSDP documentation.
    while pointer < len(bsdpoptions):
        start = pointer
        length = pointer + 1
        optionlength = bsdpoptions[length]
        pointer = optionlength + length + 1

        msgtypes[bsdpoptioncodes[bsdpoptions[start]]] = \
            [length+1, bsdpoptions[length]]

    # Now that we have decoded the raw BSDP options we iterate the msgtypes dict
    #   and pull its values, appending them to the optionvalues dict as we go
    for msg, values in msgtypes.items():
        start = values[0]
        end = start + values[1]
        options = bsdpoptions[start:end]

        optionvalues[msg] = options

    return optionvalues


def ack(packet, defaultnbi, msgtype):
    """
        The ack function constructs either a BSDP[LIST] or BSDP[SELECT] ACK
        DhcpPacket(), determined by the given msgtype, 'list' or 'select'.
        It calls the previously defined getSysIdEntitlement() and parseOptions()
        functions for either msgtype.
    """

    bsdpack = DhcpPacket()

    try:
        # Get the requesting client's clientsysid and MAC address from the
        # BSDP options
        clientsysid = \
        str(strlist(packet.GetOption('vendor_class_identifier'))).split('/')[2]

        clientmacaddr = chaddr_to_mac(packet.GetOption('chaddr'))

        # Decode and parse the BSDP options from vendor_encapsulated_options
        bsdpoptions = \
            parseOptions(packet.GetOption('vendor_encapsulated_options'))

        # Figure out the NBIs this clientsysid is entitled to
        enablednbis = getSysIdEntitlement(nbiimages, clientsysid, clientmacaddr, msgtype)

        # The Startup Disk preference panel in OS X uses a randomized reply port
        #   instead of the standard port 68. We check for the existence of that
        #   option in the bsdpoptions dict and if found set replyport to it.
        if 'reply_port' in bsdpoptions:
            replyport = int(str(format(bsdpoptions['reply_port'][0], 'x') +
                        format(bsdpoptions['reply_port'][1], 'x')), 16)
        else:
            replyport = 68

        # Get the client's IP address, a standard DHCP option
        clientip = ipv4(packet.GetOption('ciaddr'))
        if str(clientip) == '0.0.0.0':
            clientip = ipv4(packet.GetOption('request_ip_address'))
            logging.debug("Did not get a valid clientip, using request_ip_address %s instead" % (str(clientip),))
    except:
        logging.debug("Unexpected error: ack() common %s" %
                        sys.exc_info()[1])
        raise

    #print 'Configuring common BSDP packet options'

    # We construct the rest of our common BSDP reply parameters according to
    #   Apple's spec. The only noteworthy parameter here is sname, a zero-padded
    #   64 byte string list containing the BSDP server's hostname.
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

    # Process BSDP[LIST] requests
    if msgtype == 'list':
        #print 'Creating LIST packet'
        try:
            nameslength = 0
            n = 2

            # First calculate the total length of the names of all combined
            #   NBIs, a required parameter that is part of the BSDP
            #   vendor_encapsulated_options.
            for i in enablednbis:
                nameslength += i['length']

            # Next calculate the total length of all enabled NBIs
            totallength = len(enablednbis) * 5 + nameslength

            # The bsdpimagelist var is inserted into vendor_encapsulated_options
            #   and comprises of the option code (9), total length of options,
            #   the IDs and names of all NBIs and the 4 byte string list that
            #   contains the default NBI ID. Promise, all of this is part of
            #   the BSDP spec, go look it up.
            bsdpimagelist = [9,totallength]
            bsdpimagelist += imagenameslist
            defaultnbi = '%04X' % defaultnbi

            # Encode the default NBI option (7) its standard length (4) and the
            #   16 bit string list representation of defaultnbi
            defaultnbi = [7,4,129,0] + \
            [int(defaultnbi[i:i+n], 16) for i in range(0, len(defaultnbi), n)]

            if int(defaultnbi[-1:][0]) == 0:
                hasnulldefault = True
            else:
                hasnulldefault = False

            # To prevent sending a default image ID of 0 (zero) to the client
            #   after the initial INFORM[LIST] request we test for 0 and if
            #   so, skip inserting the defaultnbi BSDP option. Since it is
            #   optional anyway we won't confuse the client.
            compiledlistpacket = strlist([1,1,1,4,2,128,128]).list()
            if not hasnulldefault:
                compiledlistpacket += strlist(defaultnbi).list()
            compiledlistpacket += strlist(bsdpimagelist).list()

            # And finally, once we have all the image list encoding taken care
            #   of, we plug them into the vendor_encapsulated_options DHCP
            #   option after the option header:
            #   - [1,1,1] = BSDP message type (1), length (1), value (1 = list)
            #   - [4,2,255,255] = Server priority message type 4, length 2,
            #       value 0xffff (65535 - Highest)
            #   - defaultnbi (option 7) - Optional, not sent if '0'
            #   - List of all available Image IDs (option 9)

            bsdpack.SetOption("vendor_encapsulated_options", compiledlistpacket)

            # Some debugging to stdout
            logging.debug('-=========================================-')
            logging.debug("Return ACK[LIST] to " +
                    str(clientip) +
                    ' on ' +
                    str(replyport))
            if hasnulldefault is False: logging.debug("Default boot image ID: " +
                                              str(defaultnbi[2:]))
        except:
            logging.debug("Unexpected error ack() list: %s" %
                            sys.exc_info()[1])
            raise

    # Process BSDP[SELECT] requests
    elif msgtype == 'select':
        #print 'Creating SELECT packet'
        # Get the value of selected_boot_image as sent by the client and convert
        #   the value for later use.
        try:
            imageid = int('%02X' % bsdpoptions['selected_boot_image'][2] +
                            '%02X' % bsdpoptions['selected_boot_image'][3], 16)
        except:
            logging.debug("Unexpected error ack() select: imageid %s" %
                            sys.exc_info()[1])
            raise

        # Initialize variables for the booter file (kernel) and the dmg path
        booterfile = ''
        rootpath = ''
        selectedimage = ''
        if nbiurl.hostname[0].isalpha():
            basedmgpath = getBaseDmgPath(nbiurl)

        # Iterate over enablednbis and retrieve the kernel and boot DMG for each
        try:
            for nbidict in enablednbis:
                if nbidict['id'] == imageid:
                    booterfile = nbidict['booter']
                    rootpath = basedmgpath + nbidict['dmg']
                    # logging.debug('-->> Using boot image URI: ' + str(rootpath))
                    selectedimage = bsdpoptions['selected_boot_image']
                    # logging.debug('ACK[SELECT] image ID: ' + str(selectedimage))
        except:
            logging.debug("Unexpected error ack() selectedimage: %s" %
                            sys.exc_info()[1])
            raise

        # Generate the rest of the BSDP[SELECT] ACK packet by encoding the
        #   name of the kernel (file), the TFTP path and the vendor encapsulated
        #   options:
        #   - [1,1,2] = BSDP message type (1), length (1), value (2 = select)
        #   - [8,4] = BSDP selected_image (8), length (4), encoded image ID
        try:
            bsdpack.SetOption("file",
                strlist(booterfile.ljust(128,'\x00')).list())
            bsdpack.SetOption("root_path", strlist(rootpath).list())
            bsdpack.SetOption("vendor_encapsulated_options",
                strlist([1,1,2,8,4] + selectedimage).list())
        except:
            logging.debug("Unexpected error ack() select SetOption: %s" %
                            sys.exc_info()[1])
            raise

        try:
            # Some debugging to stdout
            logging.debug('-=========================================-')
            logging.debug("Return ACK[SELECT] to " +
                          str(clientip) +
                          ' on ' +
                          str(replyport))
            logging.debug("--> TFTP path: %s\n-->Boot image URI: %s"
                          % (str(strlist(bsdpack.GetOption("file"))), str(rootpath)))
        except:
            logging.debug("Unexpected error ack() select print debug: %s" %
                            sys.exc_info()[1])
            raise

    # Return the finished packet, client IP and reply port back to the caller
    return bsdpack, clientip, replyport

imagenameslist = []
nbiimages = []
defaultnbi = 0
hasdefault = False


def main():
    """Main routine. Do the work."""

    # # First, write a PID so we can monitor the process
    # pid = str(os.getpid())
    # pidfile = "/var/run/bspdserver.pid"
    #
    # if os.path.isfile(pidfile):
    #     print "%s already exists, exiting" % pidfile
    #     sys.exit()
    # else:
    #     file(pidfile, 'w').write(pid)

    # Some logging preamble
    logging.debug('\n\n-=- Starting new BSDP server session -=-\n')

    # We are changing nbiimages for use by other functions
    global nbiimages

    # Instantiate a basic pydhcplib DhcpServer class using netopts (listen port,
    #   reply port and listening IP)
    server = Server(netopt)

    # Do a one-time discovery of all available NBIs on the server. NBIs added
    #   after the server was started will not be picked up until after a restart
    nbiimages, nbisources = getNbiOptions(tftprootpath)

    def scan_nbis(signal, frame):
        global nbiimages
        logging.debug('[========= Updating boot images list =========]')
        nbiimages, nbisources = getNbiOptions(tftprootpath)
        for nbi in nbisources:
            logging.debug(nbi)
        logging.debug('[=========      End updated list     =========]')

    signal.signal(signal.SIGUSR1, scan_nbis)
    signal.siginterrupt(signal.SIGUSR1, False)

    # Print the full list of eligible NBIs to the log
    logging.debug('[========= Using the following boot images =========]')
    for nbi in nbisources:
        logging.debug(nbi)
    logging.debug('[=========     End boot image listing      =========]')

    # Loop while the looping's good.
    while True:

        # Listen for DHCP packets. Since select() is used upstream we need to
        #   catch the EINTR signal it trips on when we receive a USR1 signal to
        #   reload the nbiimages list.
        try:
            packet = server.GetNextDhcpPacket()
        except select.error, e:
            if e[0] != errno.EINTR: raise

        try:
            # Check to see if any vendor_encapsulated_options are present
            if len(packet.GetOption('vendor_encapsulated_options')) > 1:

                # If we have vendor_encapsulated_options check for a value of 1
                #   which in BSDP terms means the packet is a BSDP[LIST] request
                if packet.GetOption('vendor_encapsulated_options')[2] == 1:
                    logging.debug('-=========================================-')
                    logging.debug('Got BSDP INFORM[LIST] packet: ')

                    # Pass ack() the matching packet, defaultnbi and 'list'
                    bsdplistack, clientip, replyport = ack(packet,
                                                            defaultnbi,
                                                            'list')
                    # Once we have a finished DHCP packet, send it to the client
                    server.SendDhcpPacketTo(bsdplistack, str(clientip),
                                                            replyport)

                # If the vendor_encapsulated_options BSDP type is 2, we process
                #   the packet as a BSDP[SELECT] request
                elif packet.GetOption('vendor_encapsulated_options')[2] == 2:
                    logging.debug('-=========================================-')
                    logging.debug('Got BSDP INFORM[SELECT] packet: ')


                    bsdpselectack, selectackclientip, selectackreplyport = \
                        ack(packet, None, 'select')

                    # Once we have a finished DHCP packet, send it to the client
                    server.SendDhcpPacketTo(bsdpselectack,
                                            str(selectackclientip),
                                            selectackreplyport)
                # If the packet length is 7 or less, move on, BSDP packets are
                #   at least 8 bytes long.
                elif len(packet.GetOption('vendor_encapsulated_options')) <= 7:
                    pass
        except:
            # Error? No worries, keep going.
            pass

if __name__ == '__main__':
    main()
