### Python SNMP Utilities

Classes which allows interaction with SNMP devices via EasySNMP.  The module contains two classes

  - SnmpQuery
    - This class provides methods needed to perform raw SNMP queries on devices
  - SnmpUtility
    - This class provides methods which return standard information including:
      - Device name (get_snmp_name())
      - Interface statistics (get_snmp_interfaces())

### License

MIT License

Copyright (c) 2020 Ross A. Stewart

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

  - easysnmp
    -  https://github.com/fgimian/easysnmp


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

  'READYNASOS-MIB::fanRPM',
  'READYNASOS-MIB::fanStatus',
  'READYNASOS-MIB::fanNumber'
  
]
```
If textual names are used the MIB must be installed on the system

### Usage Example

Return a dictionary of disk statistics from a Netgear ReadyNAS

```python
from snmp_utilities import SnmpUtility

host = 'readynas.example.com'
community_string = 'public'
version = 2
snmp = SnmpUtility(host, community_string, version)

oids = [
    'READYNASOS-MIB::diskNumber',
    'READYNASOS-MIB::ataError',
    'READYNASOS-MIB::diskState',
    'READYNASOS-MIB::diskTemperature'
]

disk_entries = snmp.bulkwalk(oids)

device_name = snmp.get_snmp_name()

print('Host: ' + device_name['sysName'] + '\n')  # Print the hostname

for disk_entry in disk_entries:
    # Iterate over list of measurements

    fields = {}  # Define a blank dictionary to hold the fields

    # Store the hostname
    fields['host'] = device_name['sysName']

    for key, value in disk_entry.items():
        print(key + ': ' + str(value))
```
