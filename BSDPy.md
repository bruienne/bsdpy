BSDPy 1.0
=========

BSDPy is a platform-independent Apple NetBoot (BSDP) service for organizations
that have a need for Apple Mac NetBoot functionality without the ability to
support Apple Mac server hardware and software.

 

General Functionality
---------------------

The BSDPy service provides the same NetInstall feature set provided by Apple's
OS X Server application, which depending on the OS X version is either called
"NetBoot" or "NetInstall". Management tools like DeployStudio and JAMF Casper
which rely on a NetInstall-style image to launch an imaging client that writes a
disk image to a local HD or SSD and performs post-imaging configuration are
fully compatible with BSDPy. NetInstall-style images created by Apple's System
Image Utility or any other tools that create a NetInstall-style NBI are also
fully compatible. BSDPy does not currently support the less frequently used
diskless NetBoot mode which relies on a shadow disk image to be mounted from the
NetBoot server.

 

Configuration
-------------

To function, BSDPy needs to be told about a valid network interface to listen
on, the boot image network protocol to use and the boot image root path on the
host. By default it uses **"eth0"**, **"HTTP"** and **"/nbi"** for these
settings. Configuration of BSDPy is mainly done through environment variables
due to its Docker-leaning deployment preference. A few basic items like
aforementioned required network interface, boot image protocol and NBI root path
can also be set using command line flags. The complete set of configuration
items is as follows, with defaults in square brackets:

 

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
more NBI bundles.

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

`http://10.0.1.100/netboot`

\+

`109-13E28.nbi/NetInstall.dmg`

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

### Linux single host

### Linux multi-host

 

Docker run mode
---------------

### Single Docker host

### Multiple Docker hosts

 
