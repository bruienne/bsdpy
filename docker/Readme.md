## Running BSDPy as a Docker container

### Requirements

In order to successfully run a BSDPy Docker container you will need:

-   A Docker host with a network device attached to the desired subnet

    -   The IP of this network device

-   One or more NetBoot images (NBIs) to serve to clients

-   A dedicated storage container for the NBIs (setup details below)

### NBI Storage Container

The BSDPy container remains fully portable by using a separate storage
container that can be attached at runtime. This way the administrator
does not need to modify the BSDPy container itself but only has to
create a simple storage container for their organization's NBIs. The NBI
storage container can then be moved around to other hosts manually or by
pushing it to an internal Docker repository and running a "docker run -d
myorg/NBI:latest" on other hosts that will host BSDP services.

    docker run -v /nbi -name NetBootSP0 busybox true

    docker run -d -p 67:67/udp -p 69:69/udp -p 80:80 -e DOCKER_BSDPY_IP=10.0.1.193 --volumes-from NBI bruienne/bsdpy:latest
