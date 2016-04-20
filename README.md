BSDPy 1.0
=========

BSDPy is a platform-independent Apple NetBoot (BSDP) service for organizations
that have a need for Apple Mac NetBoot functionality but that lack the ability
to support OS X server in order to implement it.

 

General Functionality
---------------------

The BSDPy service provides the same NetInstall feature set provided by Apple's
OS X Server, which depending on the OS X version is either called "NetBoot" or
"NetInstall". Management tools like DeployStudio and JAMF Casper which rely on a
NetInstall-style image to launch an imaging client that writes a disk image to a
local HD or SSD and performs post-imaging configuration are fully compatible
with BSDPy. NetInstall-style images created by Apple's System Image Utility or
any other tools that create a NetInstall-style NBI are also fully compatible.
BSDPy does not currently support the less frequently used diskless NetBoot mode
which relies on a shadow disk image to be mounted from an AFP share. Shadowing
using a RAM disk or local storage is fully supported.

 

Configuration
-------------

To function, BSDPy needs to be given a valid network interface to listen on, the
boot image network protocol to use and the boot image root path on the host. By
default it uses **"eth0"**, **"HTTP"** and **"/nbi"** for these settings.
Configuration of BSDPy is mainly done through environment variables due to its
Docker-leaning deployment preference. A few basic items like aforementioned
required network interface, boot image protocol and NBI root path can also be
set using command line flags. The complete set of configuration items is as
follows, with defaults in square brackets:

 

### Supported environment variables

-   **BSDPY\_IFACE** - Interface to listen on - *['eth0']*

-   **BSDPY\_PROTO** - Protocol to serve boot image - *['http']*

-   **BSDPY\_NBI\_PATH** - Root path to NBIs - *['/nbi']*

-   **BSDPY\_IP** - Public IP BSDPy listens on - (optional)

-   **BSDPY\_NBI\_URL** - Alternate base URL for boot images (HTTP/NFS) -
    (optional)

-   **BSDPY\_API\_URL** - API endpoint to obtain NBI entitlements - (optional)

-   **BSDPY\_API\_KEY** - API key to use in conjunction with BSDPY\_API\_URL -
    (required with API URL)

 

### Supported runtime flags

-   **-i** *['eth0']* - Interface to listen on

-   **-r** *['http']* - Protocol to serve boot image

-   **-p** *['/nbi']* - Root path to NBIs

 

Modes of Operation
------------------

 

BSDPy has a few distinct modes of operation:

1.  Self-contained, single-host mode

2.  Separate NBI repository mode

3.  API-connected mode

 

Regardless of the mode of operation a functional TFTP service must be running on
the same host as BSDPy. In addition to TFTP the self-contained mode also
requires a properly configured HTTP or NFS service to be running. Specific
configuration details regarding the TFTP, HTTP and NFS services will be covered
in the **"Deployment methods"** section later in this document.

 

### Running self-contained

When running in self-contained mode BSDPy and its NBI content and supporting
services are located on the same host. This means that BSDP, TFTP and HTTP/NFS
services are all running on the host with a local directory containing one or
more NBI bundles. By default this directory is `/nbi`.

Required settings (defaults in brackets):

-   **BSDPY\_IFACE** or **-i** *['eth0']*

-   **BSDPY\_PROTO** or **-r** *['http']*

-   **BSDPY\_NBI\_PATH** or **-p** *['/nbi']*

 

Required **local** services:

-   **BSDPy** listening on port **67 UDP**

-   **TFTPD** listening on port **69 UDP**

-   **HTTPD** listening on port **80 TCP** or **NFSD** listening on ports
    **110**, **2049 UDP**/**TCP**

 

### Running with a separate NBI repository

When running in this mode BSDPy will poll a filesystem location on the host it
is running on for NBI bundles to offer. All files that are to be served by TFTP
(booter, kernelcache) will also originate from this host. Once the client is
ready to load the boot image (NetInstall.dmg) it will do so through a URI
located on another host using either HTTP or NFS. The layout of the NBI bundle
is expected to be the same between the BSDPy host and the remote host(s) since
the URI as provided through the `BSDPY_NBI_URL` setting will be combined with
the path of the NBI on the BSDPy host.

Required settings (defaults in brackets):

-   **BSDPY\_IFACE** or **-i** *[eth0]*

-   **BSDPY\_PROTO** or **-r** *[http]*

-   **BSDPY\_NBI\_PATH** or **-p** *[/nbi]*

-   **BSDPY\_NBI\_URL** ("http://mynbirepo.org/netboot") - *Must be HTTP/port
    80*

 

Required **local** services:

-   **BSDPy** listening on port **67 UDP**

-   **TFTPD** listening on port **69 UDP**

 

Required **remote** services:

-   **HTTPD** listening on port **80 TCP** or **NFSD** listening on ports
    **110**, **2049 UDP**/**TCP**

 

In this example, the BSDPy host has NBI bundles stored at /nbi and parses them
to offer to clients:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
bsdpy-host$ ls /nbi
bsdpy-host$ 109-13E28.nbi
bsdpy-host$ ls /nbi/109-13E28.nbi
bsdpy-host$ NBImageInfo.plist NetInstall.dmg i386
bsdpy-host$ ls /nbi/109-13E28.nbi/i386
bsdpy-host$ PlatformSupport.plist booter com.apple.Boot.plist x86_64

DEBUG: BSDPY_IP: 10.0.1.2
DEBUG: BSDPY_NBI_PATH: /nbi
DEBUG: BSDPY_IFACE: eth0
DEBUG: BSDPY_PROTO: http
DEBUG: BSDPY_NBI_URL: http://mynbirepo.org/netboot
DEBUG: [========= Updating boot images list =========]
DEBUG: Considering NBI source at /nbi/109-13E28.nbi
DEBUG: /nbi/109-13E28.nbi
DEBUG: [=========      End updated list     =========]
DEBUG: [===== Using the following boot images =======]
DEBUG: /nbi/109-13E28.nbi
DEBUG: [======     End boot image listing      ======]
DEBUG: -=============================================-

<snip for client LIST and SELECT requests>

DEBUG: Resolving BSDPY_NBI_URL to IP - mynbirepo.org -> 10.0.1.100
DEBUG: Found BSDPY_NBI_URL - using basedmgpath http://10.0.1.100/netboot/
DEBUG: -========================================================================-
DEBUG: Return ACK[SELECT] to 3c:1:de:ad:be:ef - 10.0.1.5 on port 68
DEBUG: --> TFTP URI: tftp://10.0.1.2/nbi/109-13E28.nbi/i386/booter
DEBUG: --> Boot Image URI: http://10.0.1.100/netboot/109-13E28.nbi/NetInstall.dmg
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

The contents of the `i386` directory will be offered to the client via TFTP from
the BSDPy host at `10.0.1.2`. Once the client completes loading the booter,
com.apple.Boot.plist, PlatformSupport.plist and kernelcache files it will send a
request to mount `NetInstall.dmg`. With `BSDPY_NBI_URL` set to
`http://mynbirepo.org/netboot`, the request for `NetInstall.dmg` will now be
sent as a URI made up of the contents of the environment variable (optionally
converted to an IP address if a DNS hostname was used) and the relative path to
NetInstall.dmg from the root directory set by `BSDPY_NBI_PATH` on the BSDPy
host:

`BSDPY_NBI_URL` = `http://10.0.1.100/netboot`

\+

`BSDPY_NBI_PATH` = `109-13E28.nbi/NetInstall.dmg`

=

`http://10.0.1.100/netboot/109-13E28.nbi/NetInstall.dmg`

The NBI repository host has the same NBI bundle(s) stored on disk and a **HTTP**
service has been configured to serve their parent location at the URL set with
`BSDPY_NBI_PATH`: `http://mynbirepo.org/netboot`. Now, when a request for
`http://10.0.1.100/netboot/OSX109-13E28.nbi/NetInstall.dmg` is received from a
client it is successfully handled by the HTTP service on the NBI repository
server and the client mounts the image and boots. The same general
behind-the-scenes process applies if BSDPy was configured to use **NFS** as boot
image protocol instead, but the URI will instead look similar to this:
`nfs:10.0.1.100/netboot/OSX109-13E28.nbi/NetInstall.dmg` - the NFS service
should be configured to allow all connections to `mynbirepo.org:/netboot` in
`/etc/exports`.

 

### Running with an API endpoint

If BSDPy is run with `BSDPY_API_URL` set it will not poll the local filesystem
for valid NBI bundles but instead send a **HTTP GET** request to the provided
API endpoint for NBI entitlements. An API call is made for each client that
sends a **BSDP LIST** request. At startup BSDPy will also make an API call to
retrieve all available NBIs and cache all TFTP content (`booter`,
`com.apple.Boot.plist`, `PlatformSupport.plist` and `kernelcache`) to the local
TFTP root directory via HTTP or NFS, depending on `BSDPY_PROTO`. It is important
that permissions for the NBI bundles on the remote server are set to allow
downloading of all files below the `ImageName.nbi` directory level. A TFTP
service running alongside BSDPy will serve the contents from this TFTP root
directory to clients. Unless `BSDPY_NBI_PATH` is set the default location of the
TFTP root directory is `/nbi`.

 

Required settings (defaults in brackets):

-   **BSDPY\_IFACE** or **-i** *[eth0]*

-   **BSDPY\_API\_URL** ("http(s)://myapiserver.org:port/{SOME\_ENDPOINT}")

-   **BSDPY\_API\_KEY** ("SOMEAPIKEYHERE")

 

Required **local** services:

-   **BSDPy** listening on port **67 UDP**

-   **TFTPD** listening on port **69 UDP**

 

Required **remote** services:

-   **HTTPD** listening on port **80 TCP** or **NFSD** listening on ports
    **110**, **2049 UDP**/**TCP**

-   **HTTPD** listening on **any available port**, either **HTTP** or **HTTPS**

 

### API requests and responses

When making the "all images" call the following parameter is sent in the **HTTP
GET** request:

-   `all=True` - (boolean)

 

When making the per-client API call the following parameters are sent in the
**HTTP GET** request:

-   `ip_address` - A valid IP address (string)

-   `mac_address` - A valid MAC address, colon-separated (string)

-   `model_name` - A valid Apple model ID, e.g. `MacBookPro10,1` (string)

 

The API response should be in JSON format, with a content type of
`application/json`. The root object should be an array of objects named
`images`. The following object keys are required for each valid image and should
have a non-empty value:

-   `booter_url` - A valid absolute path to the booter (string)

-   `name` - A valid unique image name (string)

-   `priority` - A valid unique (1-1024/1025-4096) image ID (integer)

-   `root_dmg_url` - A valid HTTP or NFS URL to the boot image (string)

 

A sample JSON response might look something like this:

 

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
{
 "images":[
           {
            "booter_url": "/nbi/10.10-14A389.nbi/i386/booter",
            "created_at": "2015-03-11T15:20:10-04:00",
            "id": 1,
            "name": "NetBoot 10.10",
            "priority": 2000,
            "root_dmg_url": "http://mynbirepo.org/netboot/10.10-14A389.nbi/NetInstall.dmg",
            "updated_at": "2015-03-11T15:25:46-04:00"
            },
            {
             "booter_url": "/nbi/10.9-13E28.nbi/i386/booter",
             "created_at": "2015-03-11T15:20:10-04:00",
             "id": 2,
             "name": "NetBoot 10.9",
             "priority": 2001,
             "root_dmg_url": "http://mynbirepo.org/netboot/10.9-13E28.nbi/NetInstall.dmg",
             "updated_at": "2015-03-11T15:21:16-04:00"
            }
           ]
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

BSDPy currently uses the `name`, `booter_url`, `root_dmg_url` and `priority`
keys to send a reply back to the client. Other fields may be added for your
organization's needs as well but will be ignored by BSDPy. The `priority` key
should be unique and additionally should be greater than **1024** if more than
one BSDPy instance will be running on the same network segment for compatibility
with the BSDP client's load balancing host selection mechanism.

![](<https://bytebucket.org/bruienne/bsdpy/raw/1a7eee604bfbb548ddc02e4d1ab3bb1dfee37b3b/BSDPy.images/N6n3r4.jpg>)

Linux run mode
--------------

As of version 1.0 the recommended way to run the BSDPy service is as a Docker
container, with supporting containers for the TFTP, HTTP and NFS services. It is
also still possible to run the service directly on most modern Linux
distributions but support for any distribution-specific implemenation is up to
the individual sys admin. That said, the service does not have a very
complicated set of requirements if run this way.

 

### Linux single host

To run the BSDPy service from a single Linux host the required BSDPy settings,
services and ports as outlined in the **Running self-contained **section earlier
in this document can be used. Settings can be provided either via command line
flags or environment variables. To recap, the `BSDPy` service, `TFTP` service
and either `HTTP` or `NFS` services will all be running on the same host and
connecting clients will be sent the same IP address or host name for all
requests.

A sample setup for CentOS 6.4 from an earlier version of this README follows.

 

Install and start the TFTP and NFS services and clone the required repositories:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ sudo yum -y install gcc xinetd tftp-server nfs-utils nfs-utils-lib git-core python python-devel
$ sudo sed -i 's/\/var\/lib\/tftpboot/\/nbi/' /etc/xinetd.d/tftp
$ sudo sed -i 's/\-s//' /etc/xinetd.d/tftp
$ sudo sed -i 's/SELINUX=.*/SELINUX=disabled/' /etc/sysconfig/selinux
$ sudo sh -c 'echo "/nbi   *(async,ro,no_root_squash,insecure)" >> /etc/exports'
$ sudo mkdir /nbi
$ sudo chkconfig --levels 235 nfs on
$ sudo chkconfig --levels 235 xinetd on
$ sudo chkconfig --levels 235 tftp on
$ sudo chkconfig --levels 235 iptables off
$ sudo service nfs start
$ sudo service xinetd start
$ git clone https://bitbucket.org/bruienne/bsdpy.git
$ cd /bsdpy
$ sudo pip install -r requirements.txt

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
tftp> get /nbi/MyNetBoot.nbi/i386/booter
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

DEBUG: BSDPY_NBI_PATH: /nbi  
DEBUG: BSDPY_IFACE: eth0  
DEBUG: BSDPY_PROTO: http  
DEBUG: [========= Updating boot images list =========]  
DEBUG: Considering NBI source at /nbi/109-13E28.nbi  
DEBUG: /nbi/109-13E28.nbi  
DEBUG: [=========      End updated list     =========]  
DEBUG: [===== Using the following boot images =======]  
DEBUG: /nbi/109-13E28.nbi  
DEBUG: [======     End boot image listing      ======]  
DEBUG: -=============================================-  

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default BSDPy will assume the service root path is /nbi. If it is not, you
can specify it in the CLI:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ sudo bsdpserver.py -p /usr/share/netboot
#Sample output

DEBUG: BSDPY_NBI_PATH: /usr/share/netboot  
DEBUG: BSDPY_IFACE: eth0  
DEBUG: BSDPY_PROTO: http  
DEBUG: [========= Updating boot images list =========]  
DEBUG: Considering NBI source at /mynbiroot/109-13E28.nbi  
DEBUG: /usr/share/netboot/109-13E28.nbi  
DEBUG: [=========      End updated list     =========]  
DEBUG: [===== Using the following boot images =======]  
DEBUG: /usr/share/netboot/109-13E28.nbi  
DEBUG: [======     End boot image listing      ======]  
DEBUG: -=============================================-

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 

### Linux multi-host

To run the BSDPy service using multiple Linux hosts, for example to serve boot
images from a dedicated file server or content delivery network, the required
BSDPy settings, services and ports as outlined in the **Running with a separate
NBI repository** section earlier in this document can be used. Settings can be
provided either via command line flags or environment variables. To recap, the
`BSDPy` service and `TFTP` service will be running on one host while one or more
separate hosts will be running the `HTTP` or `NFS` service. The latter may
implement whatever load balancing methodology is appropriate for the
organization, keeping in mind that when the boot image is requested it will be
done using an IP address that was resolved from a hostname, if configured
through `BSDPY_NBI_URL`.

Docker run mode
---------------

### Single Docker host

### Multiple Docker hosts

