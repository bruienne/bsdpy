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


MagicCookie = [99,130,83,99]
PyDhcpLibVersion = '0.6'

# DhcpBaseOptions = '{fieldname':[location,length]}
DhcpFields = {'op':[0,1],
    'htype':[1,1],
    'hlen':[2,1],
    'hops':[3,1],
    'xid':[4,4],
    'secs':[8,2],
    'flags':[10,2],
    'ciaddr':[12,4],
    'yiaddr':[16,4],
    'siaddr':[20,4],
    'giaddr':[24,4],
    'chaddr':[28,16],
    'sname':[44,64],
    'file':[108,128]
}
DhcpFieldsName = { 'op' : { '0': 'ERROR_UNDEF', '1' : 'BOOTREQUEST' , '2' : 'BOOTREPLY'},
    'dhcp_message_type' : { '0': 'ERROR_UNDEF', '1': 'DHCP_DISCOVER', '2': 'DHCP_OFFER',
        '3' : 'DHCP_REQUEST','4':'DHCP_DECLINE', '5': 'DHCP_ACK', '6': 'DHCP_NACK',
        '7': 'DHCP_RELEASE', '8' : 'DHCP_INFORM' }
}
DhcpNames = { 'ERROR_UNDEF':0 , 'BOOTREQUEST':1 , 'BOOTREPLY':2 ,
    'DHCP_DISCOVER':1 , 'DHCP_OFFER':2 , 'DHCP_REQUEST':3 ,
    'DHCP_DECLINE':4 , 'DHCP_ACK':5 , 'DHCP_NACK':6 ,
    'DHCP_RELEASE':7 , 'DHCP_INFORM':8 }

DhcpFieldsTypes = {'op':"int",
    'htype':"int",
    'hlen':"int",
    'hops':"int",
    'xid':"int4",
    'secs':"int2",
    'flags':"int2",
    'ciaddr':"ipv4",
    'yiaddr':"ipv4",
    'siaddr':"ipv4",
    'giaddr':"ipv4",
    'chaddr':"hwmac",
    'sname':"str",
    'file':"str"
}

# DhcpOptions = 'option_name':option_code
DhcpOptions = {'pad':0,
    
    # Vendor Extension
    'subnet_mask':1,'time_offset':2,
    'router':3,'time_server':4,'name_server':5,
    'domain_name_server':6,'log_server':7,
    'cookie_server':8,'lpr_server':9,
    'impress_server':10,'resource_location_server':11,
    'host_name':12,'boot_file':13,'merit_dump_file':14,
    'domain_name':15,'swap_server':16,'root_path':17,'extensions_path':18,
    
    # IP layer parameters per host
    'ip_forwarding':19,'nonlocal_source_rooting':20,
    'policy_filter':21,'maximum_datagram_reassembly_size':22,
    'default_ip_time-to-live':23,'path_mtu_aging_timeout':24,
    'path_mtu_table':25,
    
    # IP layer parameters per interface
    'interface_mtu':26,'all_subnets_are_local':27,
    'broadcast_address':28,'perform_mask_discovery':29,
    'mask_supplier':30,'perform_router_discovery':31,
    'routeur_solicitation_address':32,'static_route':33,
    
    # link layer parameters per interface
    'trailer_encapsulation':34,'arp_cache_timeout':35,
    'ethernet_encapsulation':36,
    
    # TCP parameters
    'tcp_default_ttl':37,'tcp_keepalive_interval':38,
    'tcp_keepalive_garbage':39,
    
    # Applications and service parameters
    'nis_domain':40,
    'nis_servers':41,
    'ntp_servers':42,
    'vendor_encapsulated_options':43,
    'nbns':44,
    'nbdd':45,'nb_node_type':46,
    'nb_scope':47,'x_window_system_font_server':48,
    'x_window_system_display_manager':49,
    
    # DHCP extensions
    'request_ip_address':50,
    'ip_address_lease_time':51,
    'overload':52,
    'dhcp_message_type':53,
    'server_identifier':54,
    'parameter_request_list':55,
    'message':56,
    'maximum_dhcp_message_size':57,
    'renewal_time_value':58,
    'rebinding_time_value':59,
    'vendor_class_identifier':60,
    'client_identifier':61,
    
    # Add from RFC 2132
    'netware_ip_domain_name':62,
    'netware_ip_sub_options':63,
    
    'nis+_domain':64,
    'nis+_servers':65,
    'tftp_server_name':66,
    'bootfile_name':67,
    'mobile_ip_home_agent':68,
    'smtp_servers':69,
    'pop_servers':70,
    'nntp_servers':71,
    'default_www_server':72,
    'default_finger_server':73,
    'default_irc_server':74,
    'streettalk_server':75,
    'streettalk_directory_assistance_server':76,
    
    'user_class':77,
    'directory_agent':78,
    'service_scope':79,
    'rapid_commit':80,
    
    'client_fqdn':81,
    'relay_agent':82,
    'internet_storage_name_service':83,
    '84':84,
    'nds_server':85,
    'nds_tree_name':86,
    'nds_context':87,
    '88':88,
    '89':89,
    'authentication':90,
    'client_last_transaction_time':91,
    'associated_ip':92,
    'client_system':93,
    'client_ndi':94,
    'ldap':95,
    'unassigned':96,
    'uuid_guid':97,
    'open_group_user_auth':98,
    'unassigned':99,
    'unassigned':100,
    'unassigned':101,
    'unassigned':102,
    'unassigned':103,
    'unassigned':104,
    'unassigned':105,
    'unassigned':106,
    'unassigned':107,
    'unassigned':108,
    'unassigned':109,
    'unassigned':110,
    'unassigned':111,
    'netinfo_address':112,
    'netinfo_tag':113,
    'url':114,
    'unassigned':115,
    'auto_config':116,
    'name_service_search':117,
    'subnet_selection':118,
    'domain_search':119,
    'sip_servers':120,
    'classless_static_route':121,
    'cablelabs_client_configuration':122,
    'geoconf':123,
    'vendor_class':124,
    'vendor_specific':125,
    '126':126,'127':127,'128':128,'129':129,
    '130':130,'131':131,'132':132,'133':133,
    '134':134,'135':135,'136':136,'137':137,
    '138':138,'139':139,'140':140,'141':141,
    '142':142,'143':143,'144':144,'145':145,
    '146':146,'147':147,'148':148,'149':149,
    '150':150,'151':151,'152':152,'153':153,
    '154':154,'155':155,'156':156,'157':157,
    '158':158,'159':159,'160':160,'161':161,
    '162':162,'163':163,'164':164,'165':165,
    '166':166,'167':167,'168':168,'169':169,
    '170':170,'171':171,'172':172,'173':173,
    '174':174,'175':175,'176':176,'177':177,
    '178':178,'179':179,'180':180,'181':181,
    '182':182,'183':183,'184':184,'185':185,
    '186':186,'187':187,'188':188,'189':189,
    '190':190,'191':191,'192':192,'193':193,
    '194':194,'195':195,'196':196,'197':197,
    '198':198,'199':199,'200':200,'201':201,
    '202':202,'203':203,'204':204,'205':205,
    '206':206,'207':207,'208':208,'209':209,
    '210':210,'211':211,'212':212,'213':213,
    '214':214,'215':215,'216':216,'217':217,
    '218':218,'219':219,'220':220,'221':221,
    '222':222,'223':223,'224':224,'225':225,
    '226':226,'227':227,'228':228,'229':229,
    '230':230,'231':231,'232':232,'233':233,
    '234':234,'235':235,'236':236,'237':237,
    '238':238,'239':239,'240':240,'241':241,
    '242':242,'243':243,'244':244,'245':245,
    '246':246,'247':247,'248':248,'249':249,
    '250':250,'251':251,'252':252,'253':253,
    '254':254,'end':255
    
}

# DhcpOptionsList : reverse of DhcpOptions
DhcpOptionsList = ['pad',
                   
                   # Vendor Extension
                   'subnet_mask','time_offset',
                   'router','time_server','name_server',
                   'domain_name_server','log_server',
                   'cookie_server','lpr_server',
                   'impress_server','resource_location_server',
                   'host_name','boot_file','merit_dump_file',
                   'domain_name','swap_server','root_path','extensions_path',
                   
                   # IP layer parameters per host
                   'ip_forwarding','nonlocal_source_rooting',
                   'policy_filter','maximum_datagram_reassembly_size',
                   'default_ip_time-to-live','path_mtu_aging_timeout',
                   'path_mtu_table',
                   
                   # IP layer parameters per interface
                   'interface_mtu','all_subnets_are_local',
                   'broadcast_address','perform_mask_discovery',
                   'mask_supplier','perform_router_discovery',
                   'routeur_solicitation_address','static_route',
                   
                   # link layer parameters per interface
                   'trailer_encapsulation','arp_cache_timeout',
                   'ethernet_encapsulation',
                   
                   # TCP parameters
                   'tcp_default_ttl','tcp_keepalive_interval',
                   'tcp_keepalive_garbage',
                   
                   # Applications and service parameters
                   'nis_domain',
                   'nis_servers',
                   'ntp_servers',
                   'vendor_encapsulated_options','nbns',
                   'nbdd','nd_node_type',
                   'nb_scope','x_window_system_font_server',
                   'x_window_system_display_manager',
                   
                   # DHCP extensions
                   'request_ip_address',
                   'ip_address_lease_time',
                   'overload',
                   'dhcp_message_type',
                   'server_identifier',
                   'parameter_request_list',
                   'message',
                   'maximum_dhcp_message_size',
                   'renewal_time_value',
                   'rebinding_time_value',
                   'vendor_class_identifier',
                   'client_identifier',
                   
                   
                   # adds from RFC 2132,2242
                   'netware_ip_domain_name',
                   'netware_ip_sub_options',
                   'nis+_domain',
                   'nis+_servers',
                   'tftp_server_name',
                   'bootfile_name',
                   'mobile_ip_home_agent',
                   'smtp_servers',
                   'pop_servers',
                   'nntp_servers',
                   'default_www_server',
                   'default_finger_server',
                   'default_irc_server',
                   'streettalk_server',
                   'streettalk_directory_assistance_server',
                   'user_class','directory_agent','service_scope',
                   
                   # 80
                   'rapid_commit','client_fqdn','relay_agent',
                   'internet_storage_name_service',
                   '84',
                   'nds_server','nds_tree_name','nds_context',
                   '88','89',
                   
                   #90
                   'authentication',
                   'client_last_transaction_time','associated_ip', #RFC 4388
                   'client_system', 'client_ndi', #RFC 3679
                   'ldap','unassigned','uuid_guid', #RFC 3679
                   'open_group_user_auth', #RFC 2485
                   
                   # 99->115 RFC3679
                   'unassigned','unassigned','unassigned',
                   'unassigned','unassigned','unassigned',
                   'unassigned','unassigned','unassigned',
                   'unassigned','unassigned','unassigned',
                   'unassigned','netinfo_address','netinfo_tag',
                   'url','unassigned',
                   
                   #116
                   'auto_config','name_service_search','subnet_selection',
                   'domain_search','sip_servers','classless_static_route',
                   'cablelabs_client_configuration','geoconf',
                   
                   #124
                   'vendor_class', 'vendor_specific',
                   
                   '126','127','128','129',
                   '130','131','132','133','134','135','136','137','138','139',
                   '140','141','142','143','144','145','146','147','148','149',
                   '150','151','152','153','154','155','156','157','158','159',
                   '160','161','162','163','164','165','166','167','168','169',
                   '170','171','172','173','174','175','176','177','178','179',
                   '180','181','182','183','184','185','186','187','188','189',
                   '190','191','192','193','194','195','196','197','198','199',
                   '200','201','202','203','204','205','206','207','208','209',
                   '210','211','212','213','214','215','216','217','218','219',
                   '220','221','222','223','224','225','226','227','228','229',
                   '230','231','232','233','234','235','236','237','238','239',
                   '240','241','242','243','244','245','246','247','248','249',
                   '250','251','252','253','254',
                   
                   'end'
                   ]


# See http://www.iana.org/assignments/bootp-dhcp-parameters
# FIXME : verify all ipv4+ options, somes are 32 bits...

DhcpOptionsTypes = {0:"none", 1:"ipv4", 2:"ipv4", 3:"ipv4+",
    4:"ipv4+", 5:"ipv4+", 6:"ipv4+", 7:"ipv4+",
    8:"ipv4+", 9:"ipv4+", 10:"ipv4+", 11:"ipv4+",
    12:"string", 13:"16-bits", 14:"string", 15:"string",
    16:"ipv4", 17:"string", 18:"string", 19:"bool",
    20:"bool", 21:"ipv4+", 22:"16-bits", 23:"char",
    24:"ipv4", 25:"16-bits", 26:"16-bits", 27:"bool",
    28:"ipv4", 29:"bool", 30:"bool", 31:"bool",
    32:"ipv4", 33:"ipv4+", 34:"bool", 35:"32-bits",
    36:"bool", 37:"char", 38:"32-bits", 39:"bool",
    40:"string", 41:"ipv4+", 42:"ipv4+", 43:"string",
    44:"ipv4+", 45:"ipv4+", 46:"char", 47:"string",
    48:"ipv4+", 49:"ipv4+", 50:"ipv4", 51:"32-bits",
    52:"char", 53:"char", 54:"32-bits", 55:"char+",
    56:"string", 57:"16-bits", 58:"32-bits", 59:"32-bits",
    60:"string", 61:"identifier", 62:"string", 63:"RFC2242",
    64:"string", 65:"ipv4+", 66:"string", 67:"string",
    68:"ipv4", 69:"ipv4+", 70:"ipv4+", 71:"ipv4+",
    72:"ipv4+", 73:"ipv4+", 74:"ipv4+", 75:"ipv4+",
    76:"ipv4+", 77:"RFC3004", 78:"RFC2610", 79:"RFC2610",
    80:"null", 81:"string", 82:"RFC3046", 83:"RFC4174",
    84:"Unassigned", 85:"ipv4+", 86:"RFC2241", 87:"RFC2241",
    88:"Unassigned", 89:"Unassigned", 90:"RFC3118", 91:"RFC4388",
    92:"ipv4+", 93:"Unassigned", 94:"Unassigned", 95:"Unassigned",
    96:"Unassigned", 97:"Unassigned", 98:"string", 99:"Unassigned",
    100:"Unassigned", 101:"Unassigned", 102:"Unassigned", 103:"Unassigned",
    104:"Unassigned", 105:"Unassigned", 106:"Unassigned", 107:"Unassigned",
    108:"Unassigned", 109:"Unassigned", 110:"Unassigned", 111:"Unassigned",
    112:"Unassigned", 113:"Unassigned", 114:"Unassigned", 115:"Unassigned",
    116:"char", 117:"RFC2937", 118:"ipv4", 119:"RFC3397",
    120:"RFC3361",
    
    #TODO
    121:"Unassigned", 122:"Unassigned", 123:"Unassigned",
    124:"Unassigned", 125:"Unassigned", 126:"Unassigned", 127:"Unassigned",
    128:"Unassigned", 129:"Unassigned", 130:"Unassigned", 131:"Unassigned",
    132:"Unassigned", 133:"Unassigned", 134:"Unassigned", 135:"Unassigned",
    136:"Unassigned", 137:"Unassigned", 138:"Unassigned", 139:"Unassigned",
    140:"Unassigned", 141:"Unassigned", 142:"Unassigned", 143:"Unassigned",
    144:"Unassigned", 145:"Unassigned", 146:"Unassigned", 147:"Unassigned",
    148:"Unassigned", 149:"Unassigned", 150:"Unassigned", 151:"Unassigned",
    152:"Unassigned", 153:"Unassigned", 154:"Unassigned", 155:"Unassigned",
    156:"Unassigned", 157:"Unassigned", 158:"Unassigned", 159:"Unassigned",
    160:"Unassigned", 161:"Unassigned", 162:"Unassigned", 163:"Unassigned",
    164:"Unassigned", 165:"Unassigned", 166:"Unassigned", 167:"Unassigned",
    168:"Unassigned", 169:"Unassigned", 170:"Unassigned", 171:"Unassigned",
    172:"Unassigned", 173:"Unassigned", 174:"Unassigned", 175:"Unassigned",
    176:"Unassigned", 177:"Unassigned", 178:"Unassigned", 179:"Unassigned",
    180:"Unassigned", 181:"Unassigned", 182:"Unassigned", 183:"Unassigned",
    184:"Unassigned", 185:"Unassigned", 186:"Unassigned", 187:"Unassigned",
    188:"Unassigned", 189:"Unassigned", 190:"Unassigned", 191:"Unassigned",
    192:"Unassigned", 193:"Unassigned", 194:"Unassigned", 195:"Unassigned",
    196:"Unassigned", 197:"Unassigned", 198:"Unassigned", 199:"Unassigned",
    200:"Unassigned", 201:"Unassigned", 202:"Unassigned", 203:"Unassigned",
    204:"Unassigned", 205:"Unassigned", 206:"Unassigned", 207:"Unassigned",
    208:"Unassigned", 209:"Unassigned", 210:"Unassigned", 211:"Unassigned",
    212:"Unassigned", 213:"Unassigned", 214:"Unassigned", 215:"Unassigned",
    216:"Unassigned", 217:"Unassigned", 218:"Unassigned", 219:"Unassigned",
    220:"Unassigned", 221:"Unassigned", 222:"Unassigned", 223:"Unassigned",
    224:"Unassigned", 225:"Unassigned", 226:"Unassigned", 227:"Unassigned",
    228:"Unassigned", 229:"Unassigned", 230:"Unassigned", 231:"Unassigned",
    232:"Unassigned", 233:"Unassigned", 234:"Unassigned", 235:"Unassigned",
    236:"Unassigned", 237:"Unassigned", 238:"Unassigned", 239:"Unassigned",
    240:"Unassigned", 241:"Unassigned", 242:"Unassigned", 243:"Unassigned",
    244:"Unassigned", 245:"Unassigned"}
