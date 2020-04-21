### Python SNMP Utilities

Classes which allows interaction with SNMP devices via pySNMP.  The module contains two classes

  - SnmpQuery
    - This class provides methods needed to perform raw SNMP queries on devices
  - SnmpUtility
    - This class provides methods which return standard information including:
      - Device name (get_snmp_name())
      - Interface statistics (get_snmp_interfaces())

### License

MIT License

Copyright (c) 2020 Ross A. Stewart (rosskouk@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

### Python Dependencies

The class requires the following Python packages to be installed:

  - pysnmp
    -  https://github.com/etingof/pysnmp


### Specifying OIDs

The the SNMP data to query is always passed to either get() or get_next() as a Python list.  
This can be a list of OID strings:

```python
list_of_oids = [
                    '1.3.6.1.4.1.4526.22.4.1.2.1',
                    '1.3.6.1.4.1.4526.22.4.1.2.2',
                    '1.3.6.1.4.1.4526.22.4.1.2.3'
               ]
```
The list can also be made up of dictionaries containing MIB and textual name pairs:

```python
list_of_textual_names = [
                            'READYNASOS-MIB': 'fanRPM',
                            'READYNASOS-MIB': 'fanStatus',
                            'READYNASOS-MIB': 'fanNumber'
                        ]
```
If textual names are used the MIB must be loaded into pySNMP

#### Adding MIBs to pySNMP

When the pySNMP package is installed it includes a utility called mibdump.py.  This
utility can be used to convert a regular MIB file to one compatible with pySNMP.  Create
a directory called 'mibs' at the same level as the script which uses the SnmpQuery class and
place the converted MIB file in that directory.

### Usage Example

Return a dictionary of disk statistics from a Netgear ReadyNAS

```python

from snmp_utilities import SnmpUtility

host = 'readynas.example.com'
community_string = 'public'
snmp = SnmpUtility(host, community_string)

disk_entries = snmp.get_next(host,
                             [
                                 {'READYNASOS-MIB': 'diskNumber'},
                                 {'READYNASOS-MIB': 'ataError'},
                                 {'READYNASOS-MIB': 'diskState'},
                                 {'READYNASOS-MIB': 'diskTemperature'}
                             ], snmp.construct_credentials(False, community_string))

print('Host: ' + snmp.get_snmp_name() + '\n')  # Print the hostname

for disk_entry in disk_entries:
    # Iterate over dictionary of entries

    for key, value in disk_entry.items():
        # Iterate over fields

        print(snmp.get_brief_name(key) + ': ' + str(value))

```
