**BSDPy**
=========

### A BSDP/Apple NetBoot server implemented in Python



### Purpose

The purpose of this project is to implement a feature-complete NetBoot (BSDP)
server using Python. It relies on the pydhcplib module (http://bit.ly/IGtv67) to
handle BSDP requests from Apple Mac clients.

Apple has long been the only game in town when it comes to providing NetBoot
service. Other projects have been able to replicate partial functionality
through ISC DHCPd and custom configurations, most notably JAMF’s NetSUS
(https://github.com/jamf/NetSUS/). Some of the DHCPd-based solutions also
require patching of the DHCPd source to work properly. What they have in common
is that none are compatible with the OS X Startup Disk preference pane because
it uses a randomized reply port instead of the standard port (68).

**Note: **Instructions regarding installation as a system daemon will be added
at a later date. Currently the service can be tested by running it from a CLI
prompt. Some basic logging is written to STDOUT in this case. More complete
logging to a logging facility is planned but not yet implemented.

**WARNING:** As with any BSDP service, proper DNS functionality is required in
order for it to work - the same requirements as Apple’s NetInstall Server. At a
minimum this means having working forward lookups for the TFTP server which in
the example below is the same as the BSDPy and NFS server. It is possible to
separate these roles, which will be up to the individual admin to implement.
Additionally you really want to have a static IP assignment for the BSDPy host,
either through DHCP reservation or directly set. Things are guaranteed to be
flakey or broken if either one of these is not working.

### Sample** **setup

The following walkthrough assumes a base CentOS 6.4 (32 or 64-bit) install. I
created mine using Vagrant.

Install and start the TFTP and NFS services and clone the required repositories:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ sudo yum -y install xinetd tftp-server nfs-utils nfs-utils-lib git-core python python-devel
$ sudo sed -i 's/\/var\/lib\/tftpboot/\/nbi/' /etc/xinetd.d/tftp
$ sudo sed -i 's/\-s$//' /etc/xinetd.d/tftp
$ sudo sh -c 'echo "/nbi   *(async,ro,no_root_squash,insecure)" >> /etc/exports'
$ sudo mkdir /nbi
$ sudo chkconfig --levels 235 nfs on
$ sudo chkconfig --levels 235 xinetd on
$ sudo chkconfig --levels 235 tftp on
$ sudo chkconfig --levels 235 iptables off
$ sudo service nfs start
$ sudo service xinetd start
$ git clone https://bruienne@bitbucket.org/bruienne/bsdpy.git
$ git clone https://github.com/bruienne/pydhcplib.git
$ cd pydhcplib
$ sudo python setup.py install
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the above is complete, one or more NBI bundles must be transferred to the
server’s NetBoot service root path, **/nbi**. Assuming SSH is active, using scp
to copy one or more images over would be straightforward:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ scp -r /Path/To/MyNetBoot.nbi user@bsdpyhost:/nbi
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once one or more boot images have been transferred, verify that both TFTP and
NFS work by testing their connectivity from a client that can reach the BSDPy
server:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ showmount -e <ip or hostname of BSDPy server>
Export list for <ip or hostname of BSDPy server>:
/nbi *
$ cd ~/; mkdir nbimount
$ mount -t nfs <ip or hostname>:/nbi ~/nbimount
$ ls ~/nbimount
#Sample output
DSR-1090.nbi  NI2.nbi  NI.nbi

$ umount ~/nbimount
$ tftp <ip or hostname>
#Sample get command
tftp> get nbi/MyNetBoot.nbi/i386/booter
Received 174997 bytes in 0.2 seconds
tftp> quit
$ ls -l booter
#Sample output
-rwxr-xr-x 1 root root 994464 May 15  2013 booter

$ rm booter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If TFTP and NFS check out successfully the BSDPy service can be started:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ cd bsdpy
$ sudo bsdpserver.py
#Sample output
Using /nbi as root path
********************************************************
Got BSDP INFORM[LIST] packet: 
=================================================================
Return ACK[LIST] to 10.0.2.5 on 68
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default BSDPy will assume the service root path is /nbi. If it is not, you
can specify it in the CLI:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ sudo bsdpserver.py /mynbiroot
#Sample output
Using /mynbiroot as root path
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



### In depth

BSDPy aims to offer the same functionality as Apple’s NetBoot server without
relying on (Mac) OS X as its host OS. It is compatible with NetBoot Image (NBI)
bundles as created by Apple’s System Image Utility, DeployStudio Server
Assistant and those created by AutoNBI (https://bitbucket.org/bruienne/autonbi/)
with other tools likely to be compatible too. A checklist of features follows
below, with those not currently implemented in italic type:



-   Receive and process BSDP INFORM[LIST] requests from clients (broadcast)

-   Send BSDP ACK[LIST] responses to clients (unicast) containing:

    -   One or more NBI sources

    -   The default boot image’s identifier

    -   The optional identifier of a boot image that was previously selected by
        the client

-   Receive and process BSDP INFORM[SELECT] requests from clients (broadcast)

-   Send BSDP ACK[SELECT] responses to clients (unicast) containing:

    -   The booter’s TFTP server and its path on the server

    -   The selected NBI’s boot image URL using NFS or *HTTP*

-   **Apply available NBI filtering based on Mac model ID or MAC address entries
    in NBImageInfo.plist** This feature is now implemented. Please test it out.

-   BSDP Option Codes:

    1.  **BSDP Message Type** (List, Select, Failed)

    2.  **BSDP Version** (Currently 1.1)

    3.  **BSDP Server Identifier** (IPv4 address)

    4.  *BSDP Server Priority - allows clients to pick the least busy server if
        more than one BSDP server replied with an ACK[LIST] packet containing
        the same NBI identifier (5000+)*

    5.  **BSDP Reply Port** (Used by OS X Startup Disk)

    6.  *BSDP Boot Image List Path (Unused in current BSDP implementation)*

    7.  **BSDP Default Boot Image** (Sent when client is booted using N-key)

    8.  **BSDP Selected Boot Image** (Sent by client to indicate requested
        image, *by server to indicate it has a record of an image previously
        selected by the client*)

    9.  **BSDP Boot Image List** (Sent by server to indicate available boot
        images)

    10. *BSDP NetBoot 1.0 Firmware (Unused)*

    11. *BSDP Boot Image Attributes Filter List (Sent by client to request a
        list filtered by the server based on defined attributes:
        Install/Non-install image, Mac OS 9/Mac OS X/Mac OS X Server/Hardware
        Diagnostics)*

    12. **BSDP Maximum Message Size** (Sent by client to indicate the largest
        packet size it can interpret in addition to the size set by DHCP option
        57)



### Copyright and licensing

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Copyright 2014 The Regents of the University of Michigan

Licensed under the Apache License, Version 2.0 (the "License");    you may not use this file except in compliance with the License.    You may obtain a copy of the License at  

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software    distributed under the License is distributed on an "AS IS" BASIS,    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    See the License for the specific language governing permissions and    limitations under the License.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This software relies on a modified version of PyDhcpLib by Mathieu Ignacio (http://pydhcplib.tuxfamily.org/pmwiki/index.php) which was released under the GPL 3 license.

The modified source may be obtained from the project page here: https://github.com/bruienne/pydhcplib and used and modified under the same terms as set forth in the full GNU General Public License 3.

For the full GPL 3 license text see this link: http://www.gnu.org/licenses/gpl-3.0.txt
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
