# pydhcplib
# Copyright (C) 2008 Mathieu Ignacio -- mignacio@april.org
#
# This file is part of pydhcplib.
# Pydhcplib is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys
import dhcp_packet
import IN

class DhcpFileIO() :
    def __init__(self) :
        self.binary = False
        self.filedesc = False

    def EnableBinaryTransport(self) :
        self.binary = True

    def DisableBinaryTransport(self) :
        self.binary = False
    
    def SendDhcpPacketTo(self,packet,forgetthisparameter1=None,forgetthisparameter2=None) :
        if self.filedesc and self.binary :
            self.filedesc.write(packet.EncodePacket())
        elif self.filedesc and not self.binary :
            self.filedesc.write(packet.str())

    def GetNextDhcpPacket(self) :
        if self.filedesc and self.binary :
            packet = dhcp_packet.DhcpPacket()
            data = self.filedesc.read(4096)
            packet.DecodePacket(data)
            return packet

        elif self.filedesc and not self.binary :
            packet = dhcp_packet.DhcpPacket()
            for line in self.filedesc : packet.AddLine(line)
            return packet


class DhcpStdIn(DhcpFileIO) :
    def __init__(self) :
        self.EnableBinaryTransport()
        self.filedesc = sys.stdin

class DhcpStdOut(DhcpFileIO) :
    def __init__(self) :
        self.EnableBinaryTransport()
        self.filedesc = sys.stdout

class DhcpFileOut(DhcpFileIO) :
    def __init__(self,filename) :
        self.filedesc = file(filename, 'w')
        self.EnableBinaryTransport()

class DhcpFileIn(DhcpFileIO) :
    def __init__(self,filename) :
        self.filedesc = file(filename, 'r')
        self.EnableBinaryTransport()
