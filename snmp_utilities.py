## @file snmp_utilities.py
# @brief SNMP Utility Classes
# @author Ross A. Stewart
# @copyright 2019-2020
# @par License
# MIT License
# @date 29th April 2020
# @details
#
# This module allows access to classes which provide SNMP
# querying functionality using the EasySNMP library.
#
# Required libraries:
#   - easysnmp
#       - https://github.com/fgimian/easysnmp
#


from easysnmp import Session


class SnmpQuery:
    """! @brief SNMP query class

    @details This class provides methods to query SNMP devices
    """

    def __init__(self, host, community_string, snmp_version):
        """! @brief Constructor

        @param host STRING - The name of the host to perform the SNMP query on
        @param community_string STRING - The SNMP 1 / v2c community string
        @param snmp_version INTEGER - The SNMP version to use 1, 2 or 3
        @exception NotImplementedError Triggered if SNMP v3 is attempted
        @details

        SnmpQuery class constructor, stores parameters and instantiates a new
        instance of EasySNMP Session.
        """

        if snmp_version == 1 or snmp_version == 2:
            # Using SNMP version 1 or 2c

            ## @var host
            # @brief STRING - The hostname of the SNMP device
            self.host = host

            ## @var community_string
            # @brief STRING - The SNMP community string set on the device
            self.community_string = community_string

            ## @var snmp
            # @brief OBJECT - Instance of EasySNMP Session
            self.snmp = Session(host, snmp_version, community_string)

        if snmp_version == 3:
            raise NotImplementedError

    def bulkwalk(self, oids):
        """! @brief Perform SNMP GETBULK operation

        @param oids LIST - List of OIDs, or textual names to query
        @return LIST of DICTIONARIES - Returns a list of dicts containing SNMP fields, one list entry per SNMP index entry
        @details

        Performs an SNMP GETBULK operation and passes the results to parse()
        """

        fetched_results = {}  # Blank dictionary to hold fields

        for oid in oids:
            # OIDS must be fed to bulkwalk one at a time

            fields = self.snmp.bulkwalk(oid)

            for field in fields:
                if str(field.oid_index) not in fetched_results:
                    fetched_results[str(field.oid_index)] = {
                        str(field.oid): self.cast(field.value)
                    }
                else:
                    fetched_results[str(field.oid_index)].update(
                        {field.oid: self.cast(field.value)})

        return self.parse(fetched_results)

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

    def get(self, oids):
        """! @brief Perform SNMP GET operation

        @param oids LIST - OID, or textual name to query
        @return DICTIONARY - Dictionary containing the result
        @details

        Performs an SNMP GET operation and passes the result to parse().

        The variable results will contain a list of SNMPVariable objects
        if multiple OIDs were passed.  In this case the method will generate
        a nested dictionary with the OID index as key and a dictionary containing
        each OID and OID value as the dictionary value.

        The variable results will contain a single SNMPVariable object if a
        single OID was passed.  In this case the method will generate a single
        dictionary with the OID and OID value pair
        """

        results = self.snmp.get(oids)

        fetched_results = {}  # Define blank dictionary to hold results

        if type(results) is list:
            # Multiple OIDs were returned

            for result in results:
                if str(result.oid_index) not in fetched_results:
                    fetched_results[str(result.oid_index)] = {
                        str(result.oid): self.cast(result.value)
                    }
                else:
                    fetched_results[str(result.oid_index)].update(
                        {result.oid: self.cast(result.value)})
        else:
            # A single OID was returned
            fetched_results = {
                results.oid: self.cast(results.value)
            }

        return self.parse(fetched_results)

    def parse(self, snmp_results):
        """! @brief Parse SNMP results

        @param snmp_results DICTIONARY - Either a single key / value pair or a Dict of dicts containing returned SNMP fields organised by Field index
        @return LIST of DICTIONARIES Returns a list of dicts containing SNMP fields, one list entry per SNMP index entry
        @return DICTIONARY Returns a dictionary if only a single result is passed in snmp_results
        """

        # Process the results into a list of dictionaries
        result_list = []

        if len(snmp_results) == 1:
            return snmp_results

        for index, stats_list in snmp_results.items():
            result_list.append(stats_list)

        return result_list


class SnmpUtility(SnmpQuery):
    """! @brief SNMP utility class

    @details

    This class provides methods which gather standard information
    from SNMP enabled devices.
    """

    def __init__(self, *args):
        """! @brief Constructor

        @param args TUPLE - Arguments to pass to the parent constructor, hostname and community string
        @details

        Passes the SNMP device hostname and community string to the parent constructor
        """

        super().__init__(*args)

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

        oids = [
            'IF-MIB::ifIndex',
            'IF-MIB::ifName',
            'IF-MIB::ifType',
            'IF-MIB::ifAdminStatus',
            'IF-MIB::ifOperStatus',
            'IF-MIB::ifHCInOctets',
            'IF-MIB::ifHCInUcastPkts',
            'IF-MIB::ifHCInMulticastPkts',
            'IF-MIB::ifHCInBroadcastPkts',
            'IF-MIB::ifHCOutOctets',
            'IF-MIB::ifHCOutUcastPkts',
            'IF-MIB::ifHCOutMulticastPkts',
            'IF-MIB::ifHCOutBroadcastPkts',
            'IF-MIB::ifInDiscards',
            'IF-MIB::ifInErrors',
            'IF-MIB::ifInUnknownProtos',
            'IF-MIB::ifOutDiscards',
            'IF-MIB::ifOutErrors'
        ]

        interface_stats = self.bulkwalk(oids)

        return interface_stats  # Return out the gathered statistics

    def get_snmp_name(self):
        """! @brief Get the name of an SNMP device

        @return DICTIONARY - Dictionary containing the value of SNMPv2-MIB::sysName.0
        """

        host_name = self.get('SNMPv2-MIB::sysName.0')

        return host_name

    def get_snmp_uptime(self):
        """! @brief Get the uptime from an SNMP enabled device

        @return DICTIONARY - Dictionary containing the value of DISMAN-EVENT-MIB::sysUpTimeInstance
        """

        host_uptime = self.get('DISMAN-EVENT-MIB::sysUpTimeInstance')

        return host_uptime
