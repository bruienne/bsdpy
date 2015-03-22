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


# Check and convert ipv4 address type
class ipv4:
    def __init__(self,value="0.0.0.0") :
        ip_type = type(value)
        if ip_type == str :
            if not self.CheckString(value) : raise ValueError, "ipv4 string argument is not an valid ip "
            self._ip_string = value
            self._StringToNumlist()
            self._StringToLong()
            self._NumlistToString()
        elif ip_type == list :
            if not self.CheckNumList(value) : raise ValueError, "ipv4 list argument is not an valid ip "
            self._ip_numlist = value
            self._NumlistToString()
            self._StringToLong()
        elif ip_type == int or ip_type == long:
            self._ip_long = value
            self._LongToNumlist()
            self._NumlistToString()
        elif ip_type == bool :
            self._ip_long = 0
            self._LongToNumlist()
            self._NumlistToString()
            
        else : raise TypeError , 'ipv4 init : Valid types are str, list, int or long'

    # Convert Long type ip to numlist ip
    def _LongToNumlist(self) :
        self._ip_numlist = [self._ip_long >> 24 & 0xFF]
        self._ip_numlist.append(self._ip_long >> 16 & 0xFF)
        self._ip_numlist.append(self._ip_long >> 8 & 0xFF)
        self._ip_numlist.append(self._ip_long & 0xFF)
        if not self.CheckNumList(self._ip_numlist) : raise ValueError, "ipv4 list argument is not an valid ip "
    # Convert String type ip to Long type ip
    def _StringToLong(self) :
        ip_numlist = map(int,self._ip_string.split('.'))
        self._ip_long = ip_numlist[3] + ip_numlist[2]*256 + ip_numlist[1]*256*256 + ip_numlist[0]*256*256*256
        if not self.CheckNumList(self._ip_numlist) : raise ValueError, "ipv4 list argument is not an valid ip "
    # Convert NumList type ip to String type ip
    def _NumlistToString(self) :
        self._ip_string = ".".join(map(str,self._ip_numlist))
        if not self.CheckNumList(self._ip_numlist) : raise ValueError, "ipv4 list argument is not an valid ip "
    # Convert String type ip to NumList type ip
    def _StringToNumlist(self) :
        self._ip_numlist = map(int,self._ip_string.split('.'))
        if not self.CheckNumList(self._ip_numlist) : raise ValueError, "ipv4 list argument is not an valid ip "

    """ Public methods """
    # Check if _ip_numlist is valid and raise error if not.
    # self._ip_numlist
    def CheckNumList(self,value) :
        if len(value) != 4 : return False
        for part in value :
            if part < 0 or part > 255 : return False
        return True

    # Check if _ip_numlist is valid and raise error if not.
    def CheckString(self,value) :
        tmp = value.strip().split('.')
        if len(tmp) != 4 :  return False
        for each in tmp : 
            if not each.isdigit() : return False
        return True
    
    # return ip string
    def str(self) :
        return self._ip_string

    # return ip list (useful for DhcpPacket class)
    def list(self) :
        return self._ip_numlist

    # return Long ip type (useful for SQL ip address backend)
    def int(self) :
        return self._ip_long


    """ Useful function for native python operations """

    def __hash__(self) :
        return self._ip_long.__hash__()

    def __repr__(self) :
        return self._ip_string

    def __cmp__(self,other) :
        return cmp(self._ip_long, other._ip_long);

    def __nonzero__(self) :
        if self._ip_long != 0 : return 1
        return 0



