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

import operator
from struct import unpack
from struct import pack
from dhcp_constants import *
import sys


# DhcpPacket : base class to encode/decode dhcp packets.

class DhcpBasicPacket:
    def __init__(self):
        self.packet_data = [0]*240
        self.options_data = {}
        self.packet_data[236:240] = MagicCookie
        self.source_address = False
        
    def IsDhcpPacket(self):
        if self.packet_data[236:240] != MagicCookie : return False
        return True

    # Check if variable is a list with int between 0 and 255
    def CheckType(self,variable):
        if type(variable) == list :
            for each in variable :
                if (type(each) != int)  or (each < 0) or (each > 255) :
                    return False
            return True
        else : return False
        

    def DeleteOption(self,name):
        # if name is a standard dhcp field
        # Set field to 0
        if DhcpFields.has_key(name) :
            begin = DhcpFields[name][0]
            end = DhcpFields[name][0]+DhcpFields[name][1]
            self.packet_data[begin:end] = [0]*DhcpFields[name][1]
            return True

        # if name is a dhcp option
        # delete option from self.option_data
        elif self.options_data.has_key(name) :
            # forget how to remove a key... try delete
            self.options_data.__delitem__(name)
            return True

        return False

    def GetOption(self,name):
        if DhcpFields.has_key(name) :
            option_info = DhcpFields[name]
            return self.packet_data[option_info[0]:option_info[0]+option_info[1]]

        elif self.options_data.has_key(name) :
            return self.options_data[name]

        return []
        

    def SetOption(self,name,value):

        # Basic value checking :
        # has value list a correct length
        
        # if name is a standard dhcp field
        if DhcpFields.has_key(name) :
            if len(value) != DhcpFields[name][1] :
                sys.stderr.write( "pydhcplib.dhcp_basic_packet.setoption error, bad option length : "+name)
                return False
            begin = DhcpFields[name][0]
            end = DhcpFields[name][0]+DhcpFields[name][1]
            self.packet_data[begin:end] = value
            return True

        # if name is a dhcp option
        elif DhcpOptions.has_key(name) :

            # fields_specs : {'option_code':fixed_length,minimum_length,multiple}
            # if fixed_length == 0 : minimum_length and multiple apply
            # else : forget minimum_length and multiple 
            # multiple : length MUST be a multiple of 'multiple'
            # FIXME : this definition should'nt be in dhcp_constants ?
            fields_specs = { "ipv4":[4,0,1], "ipv4+":[0,4,4],
                             "string":[0,0,1], "bool":[1,0,1],
                             "char":[1,0,1], "16-bits":[2,0,1],
                             "32-bits":[4,0,1], "identifier":[0,2,1],
                             "RFC3397":[0,4,1],"none":[0,0,1],"char+":[0,1,1]
                             }
            
            specs = fields_specs[DhcpOptionsTypes[DhcpOptions[name]]]
            length = len(value)
            if (specs[0]!=0 and specs==length) or (specs[1]<=length and length%specs[2]==0):
                self.options_data[name] = value
                return True
            else :
                return False

        sys.stderr.write( "pydhcplib.dhcp_basic_packet.setoption error : unknown option "+name)
        return False



    def IsOption(self,name):
        if self.options_data.has_key(name) : return True
        elif DhcpFields.has_key(name) : return True
        else : return False

    # Encode Packet and return it
    def EncodePacket(self):

        # MUST set options in order to respect the RFC (see router option)
        order = {}

        for each in self.options_data.keys() :
            order[DhcpOptions[each]] = []
            order[DhcpOptions[each]].append(DhcpOptions[each])
            order[DhcpOptions[each]].append(len(self.options_data[each]))
            order[DhcpOptions[each]] += self.options_data[each]
        
        # print order    
        options = []
        
        # if 60 in order.keys():
        #     print 'Found BSDP packet, special sort'
        #     for each in [53,54,60,17,43,52]:
        #         if each in order:
        #             options += (order[each])
        # else:
        #     print 'Not a BSDP packet, regular sort'
        #     for each in sorted(order.keys()) : options += (order[each])
        for each in sorted(order.keys()) : options += (order[each])
        
        packet = self.packet_data[:240] + options
        packet.append(255) # add end option
        pack_fmt = str(len(packet))+"c"

        packet = map(chr,packet)
        
        return pack(pack_fmt,*packet)


    # Insert packet in the object
    def DecodePacket(self,data,debug=False):
        self.packet_data = []
        self.options_data = {}

        if (not data) : return False
        # we transform all data to int list
        unpack_fmt = str(len(data)) + "c"
        for i in unpack(unpack_fmt,data):
            self.packet_data.append(ord(i))

        # Some servers or clients don't place magic cookie immediately
        # after headers and begin options fields only after magic.
        # These 4 lines search magic cookie and begin iterator after.
        iterator = 236
        end_iterator = len(self.packet_data)
        while ( self.packet_data[iterator:iterator+4] != MagicCookie and iterator < end_iterator) :
            iterator += 1
        iterator += 4
        
        # parse extended options

        while iterator < end_iterator :
            if self.packet_data[iterator] == 0 : # pad option
                opt_first = iterator+1
                iterator += 1

            elif self.packet_data[iterator] == 255 :
                self.packet_data = self.packet_data[:240] # base packet length without magic cookie
                return
                
            elif DhcpOptionsTypes.has_key(self.packet_data[iterator]) and self.packet_data[iterator]!= 255:
                opt_len = self.packet_data[iterator+1]
                opt_first = iterator+1
                self.options_data[DhcpOptionsList[self.packet_data[iterator]]] = self.packet_data[opt_first+1:opt_len+opt_first+1]
                iterator += self.packet_data[opt_first] + 2
            else :
                opt_first = iterator+1
                iterator += self.packet_data[opt_first] + 2

        # cut packet_data to remove options
        
        self.packet_data = self.packet_data[:240] # base packet length with magic cookie
