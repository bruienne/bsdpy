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


from binascii import unhexlify,hexlify

# Check and convert hardware/nic/mac address type
class hwmac:
    def __init__(self,value="00:00:00:00:00:00") :
        self._hw_numlist = []
        self._hw_string = ""
        hw_type = type(value)
        if hw_type == str :
            print 'Working with string MAC'
            value = value.strip()
            self._hw_string = value
            self._StringToNumlist(value)
            self._CheckNumList()
        elif hw_type == list :
            print 'Working with list MAC'
            self._hw_numlist = value
            self._CheckNumList()
            self._NumlistToString()
        else : raise TypeError , 'hwmac init : Valid types are str and list'



    # Check if _hw_numlist is valid and raise error if not.
    def _CheckNumList(self) :
        if len(self._hw_numlist) != 6 : raise ValueError , "hwmac : wrong list length."
        for part in self._hw_numlist :
            if type (part) != int : raise TypeError , "hwmac : each element of list must be int"
            if part < 0 or part > 255 : raise ValueError , "hwmac : need numbers between 0 and 255."
        return True


    def _StringToNumlist(self,value):
        self._hw_string = self._hw_string.replace("-",":").replace(".",":")
        self._hw_string = self._hw_string.lower()

        for twochar in self._hw_string.split(":"):
            self._hw_numlist.append(ord(unhexlify(twochar)))
            
    # Convert NumList type ip to String type ip
    def _NumlistToString(self) :
        self._hw_string = ":".join(map(hexlify,map(chr,self._hw_numlist)))

    # Convert String type ip to NumList type ip
    # return ip string
    def str(self) :
        return self._hw_string

    # return ip list (useful for DhcpPacket class)
    def list(self) :
        return self._hw_numlist

    def __hash__(self) :
        return self._hw_string.__hash__()

    def __repr__(self) :
        return self._hw_string

    def __cmp__(self,other) :
        if self._hw_string == other : return 0
        return 1

    def __nonzero__(self) :
        if self._hw_string != "00:00:00:00:00:00" : return 1
        return 0




