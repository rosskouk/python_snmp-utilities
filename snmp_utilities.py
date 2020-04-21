## @file snmp_utilities.py
# @brief SNMP Utility Classes
# @author Ross A. Stewart
# @copyright 2019-2020
# @par License
# MIT License
# @date 18th April 2020
# @details
#
# This module allows access to classes which provide SNMP
# querying functionality using the pySNMP library.  Based
# on code from https://www.ictshore.com/sdn/python-snmp-tutorial
#
# Required libraries:
#   - re
#   - pysnmp
#       - https://github.com/etingof/pysnmp
#

import re

from pysnmp import hlapi


class SnmpQuery:
    """! @brief SNMP query class

    @details This class provides methods to query SNMP devices
    """

    def cast(self, value):
        """! @brief Correctly set the type of the given variable

        @param value - MIXED The value to be cast
        @return MIXED The value correctly cast to it's type
        @details

        Attempts to cast value as and integer, float then string.
        if a ValueError or TypeError occurs the next attempt it made.
        If the value cannot be cast as any of the types it is returned
        as is.
        """
        try:
            return int(value)
        except (ValueError, TypeError):
            try:
                return float(value)
            except (ValueError, TypeError):
                try:
                    return str(value)
                except (ValueError, TypeError):
                    pass

        return value

    def construct_credentials(self, v3, credentials):
        """! @brief Construct SNMP credentials

        @param v3 BOOL - True of SNMP v3 is in use, False otherwise
        @param credentials STRING|ARRAY - A community string or an array of SNMP v3 credential information
        @return OBJECT - A CommunityData or UsmUserData object is returned
        @exception NotImplementedError - Triggered if SNMP v3 is used
        """

        if(v3 is False):
            community_string = hlapi.CommunityData(credentials)
            return community_string
        else:
            raise NotImplementedError

    def construct_object_types(self, list_of_oids):
        """! @brief Construct a list of PySNMP ObjectType objects for use in an SNMP query

        @param list_of_oids LIST - list of OIDs, or textual names to query
        @return LIST - List of PySNMP ObjectType objects
        @exception ValueError Triggered if an invalid textual SNMP value is provided
        @details

        Takes a list of OIDs or textual representations and creates PySNMP
        ObjectType objects for them.  OIDs are string entries in the list, textual
        representations are dictionary entries with the MIB as the key and field
        as the value. Example:
        @code
        [
            {'READYNASOS-MIB': 'fanRPM'},
            '1.3.6.1.4.1.4526.22.4.1.2.1',
            ...
        ]
        @endcode
        """

        object_types = []
        for oid in list_of_oids:
            if type(oid) is str:
                #
                # This is a regular OID
                #
                object_types.append(hlapi.ObjectType(
                    hlapi.ObjectIdentity(oid)))
            if type(oid) is dict:
                #
                # This is a MIB and textual name pair
                #
                for key, value in oid.items():
                    if '.' in value:
                        #
                        # The textual name has a key attached, split it to create ObjectIdentity properly
                        #
                        split_value = value.split('.')
                        if len(split_value) != 2:
                            raise ValueError(
                                'Error in construct_object_types(): Invalid SNMP value')

                        object_types.append(hlapi.ObjectType(
                            hlapi.ObjectIdentity(key, split_value[0], split_value[1]).addMibSource('./mibs')))
                    else:
                        object_types.append(hlapi.ObjectType(
                            hlapi.ObjectIdentity(key, value).addMibSource('./mibs')))

        return object_types

    def fetch(self, handler):
        """! @brief Loop over a handler and return queried values

        @param handler - OBJECT Preconfigured snmp query object
        @return LIST of DICTIONARIES - List of dictionaries containing the identifier and value of each query
        @exception RuntimeError - Triggered when an SNMP error occurs
        """

        result = []
        for (error_indication,
                error_status,
                error_index,
                var_binds) in handler:
            try:
                if not error_indication and not error_status:
                    items = {}
                    for var_bind in var_binds:
                        items[str(var_bind[0].prettyPrint())
                              ] = self.cast(var_bind[1])
                    result.append(items)
                else:
                    raise RuntimeError(
                        'Got SNMP error: {0}'.format(error_indication))
            except StopIteration:
                break

        return result

    def get(self, target, oids, credentials, port=161, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
        """! @brief Get a single SNMP value

        @param target STRING - The SNMP target
        @param oids LIST - OID, or textual name to query
        @param credentials OBJECT - PySNMP CommunityData or UsmUserData object see below
        @param port INTEGER - The SNMP port number
        @param engine OBJECT - PySNMP SnmpEngine object
        @param context OBJECT - PySNMP ContextData object
        @return DICTIONARY - Dictionary containing the result
        @details

        Creates a handler which performs an SNMP get request and passes it to fetch().
        The credentials parameter differs depending on which version of SNMP is
        being used examples:
        - SNMP v1 or v2c
          - hlapi.CommunityData('public')
        - SNMP v3
          - hlapi.UsmUserData('testuser', authKey='authenticationkey', privKey='encryptionkey',
                              authProtocol=hlapi.usmHMACSHAAuthProtocol, privProtocol=hlapi.usmAesCfb128Protocol)
        """

        handler = hlapi.getCmd(
            engine,
            credentials,
            hlapi.UdpTransportTarget((target, port)),
            context,
            # Asterisk automatically expands list of objects
            *self.construct_object_types(oids),
            lexicographicMode=False
        )

        return self.fetch(handler)

    def get_brief_name(self, full_name):
        """! @brief Return the brief textual name of an SNMP OID

        @param full_name STRING The full textual name
        @return STRING - String containing the brief name
        @details

        Accepts a full textual SNMP OID name as generated
        by pySNMP's prettyPrint() method, example:

        READYNASOS-MIB::ataError.3

        will return ataError
        """

        brief_name = re.search('(?<=::)(.*?)(?=\.)', full_name)

        if type(brief_name.group()) is not str:
            raise ValueError(
                'The string passed to get_brief_name was not in the correct format')

        return brief_name.group()

    def get_next(self, target, oids, credentials, port=161, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
        """! @brief Get a single SNMP value

        @param target STRING - The SNMP target
        @param oids LIST - OIDs, or textual names to query
        @param credentials OBJECT - PySNMP CommunityData or UsmUserData object see below
        @param port INTEGER - The SNMP port number
        @param engine OBJECT - PySNMP SnmpEngine object
        @param context OBJECT - PySNMP ContextData object
        @return DICTIONARY - Dictionary containing the result
        @details

        Creates a handler which performs an SNMP get request and passes it to fetch(). The credentials parameter differs depending on
        which version of SNMP is being used, examples:
        - SNMP v1 or v2c
          - hlapi.CommunityData('public')
        - SNMP v3
          - hlapi.UsmUserData('testuser', authKey='authenticationkey', privKey='encryptionkey',
                              authProtocol=hlapi.usmHMACSHAAuthProtocol, privProtocol=hlapi.usmAesCfb128Protocol)
        """

        handler = hlapi.nextCmd(
            engine,
            credentials,
            hlapi.UdpTransportTarget((target, port)),
            context,
            *self.construct_object_types(oids),
            lexicographicMode=False
        )

        return self.fetch(handler)


class SnmpUtility(SnmpQuery):
    """! @brief SNMP utility class

    @details

    This class provides methods which gather standard information
    from SNMP enabled devices.
    """

    def __init__(self, host, community_string):
        """! @brief Constructor

        @param host STRING - The hostname of the SNMP device
        @param community_string STRING - The SNMP community string set on the device
        @details

        Sets required parameters
        """

        ## @var host
        # @brief STRING - The hostname of the SNMP device
        self.host = host

        ## @var community_string
        # @brief STRING - The SNMP community string set on the device
        self.community_string = community_string

    def get_snmp_interfaces(self):
        """! @brief Get interface statistics via SNMP

        @details

        Gets statistics for network interfaces, the following fields
        are returned:

          - IF-MIB::ifIndex
          - IF-MIB::ifName
          - IF-MIB::ifType
          - IF-MIB::ifAdminStatus
          - IF-MIB::ifOperStatus
          - IF-MIB::ifHCInOctets
          - IF-MIB::ifHCInUcastPkts
          - IF-MIB::ifHCInMulticastPkts
          - IF-MIB::ifHCInBroadcastPkts
          - IF-MIB::ifHCOutOctets
          - IF-MIB::ifHCOutUcastPkts
          - IF-MIB::ifHCOutMulticastPkts
          - IF-MIB::ifHCOutBroadcastPkts
          - IF-MIB::ifInDiscards
          - IF-MIB::ifInErrors
          - IF-MIB::ifInUnknownProtos
          - IF-MIB::ifOutDiscards
          - IF-MIB::ifOutErrors

        The information is returned as a list of dictionaries
        """

        interface_stat_list = []  # Blank list to hold dictionaries of interface statistics

        interface_entries = self.get_next(self.host,
                                          [
                                              {'IF-MIB': 'ifIndex'},
                                              {'IF-MIB': 'ifName'},
                                              {'IF-MIB': 'ifType'},
                                              {'IF-MIB': 'ifAdminStatus'},
                                              {'IF-MIB': 'ifOperStatus'},
                                              {'IF-MIB': 'ifHCInOctets'},
                                              {'IF-MIB': 'ifHCInUcastPkts'},
                                              {'IF-MIB': 'ifHCInMulticastPkts'},
                                              {'IF-MIB': 'ifHCInBroadcastPkts'},
                                              {'IF-MIB': 'ifHCOutOctets'},
                                              {'IF-MIB': 'ifHCOutUcastPkts'},
                                              {'IF-MIB': 'ifHCOutMulticastPkts'},
                                              {'IF-MIB': 'ifHCOutBroadcastPkts'},
                                              {'IF-MIB': 'ifInDiscards'},
                                              {'IF-MIB': 'ifInErrors'},
                                              {'IF-MIB': 'ifInUnknownProtos'},
                                              {'IF-MIB': 'ifOutDiscards'},
                                              {'IF-MIB': 'ifOutErrors'}
                                          ], self.construct_credentials(False, self.community_string))

        for interface_entry in interface_entries:
            # Iterate over list of interfaces

            fields = {}  # Define a blank dictionary to hold the fields

            # Store the hostname
            fields['host'] = self.get_snmp_name()

            for key, value in interface_entry.items():
                # Iterate over measurement fields
                fields[self.get_brief_name(key)] = value

            # Add the measurement to the list
            interface_stat_list.append(fields)

        return interface_stat_list  # Return out the gathered statistics

    def get_snmp_name(self):
        """! @brief Get the name of an SNMP device

        @return STRING - The name of the device as defined by SNMPv2-MIB::sysName.0
        """

        host_name = self.get(self.host,
                             [
                                 {'SNMPv2-MIB': 'sysName.0'}
                             ], self.construct_credentials(False, self.community_string))

        return host_name[0]['SNMPv2-MIB::sysName.0']
