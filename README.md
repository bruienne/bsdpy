**BSDPy**
=========

### A BSDP/Apple NetBoot server implemented in Python



The purpose of this project is to implement a feature-complete NetBoot (BSDP)
server using Python. It relies on the pydhcplib module (http://bit.ly/IGtv67) to
handle BSDP requests from Apple Mac clients

Apple has long been the only game in town when it comes to providing NetBoot
service. Other projects have been able to replicate partial functionality
through ISC DHCPd and custom configurations, most notably JAMF’s NetSUS
(https://github.com/jamf/NetSUS/). Some of the DHCPd-based solutions also
require patching of the DHCPd source to work properly. What they have in common
is that none are compatible with the OS X Startup Disk preference pane because
it uses a randomized reply port instead of the standard (port 68).

**Note: **Instructions regarding installation as a system daemon will be added
at a later date. Currently the service can be tested by running it from a CLI
prompt. Some basic logging is written to STDOUT in this case. More complete
logging to a logging facility is still to be implemented.



**Sample setup:**

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ git clone https://bruienne@bitbucket.org/bruienne/bsdpy.git
$ git clone https://github.com/bruienne/pydhcplib.git
$ cd pydhcplib
$ sudo python setup.py install
$ cd ../
$ cd bsdpy
$ sudo bsdpserver.py [/path/to/tftp/root]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



BSDPy aims to offer the same functionality as Apple’s NetBoot server without
relying on (Mac) OS X as its host OS. A checklist of features follows below,
with those not currently implemented in italic type:



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

-   *Apply available NBI filtering based on Mac model ID or MAC address entries
    in NBImageInfo.plist*

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




