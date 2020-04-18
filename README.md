### Python SNMP Utilities

Class which allows interaction with SNMP devices via pySNMP

#### Python Dependencies

The class requires the following Python packages to be installed:

  - pysnmp
    -  https://github.com/etingof/pysnmp


#### Usage Example

Return a dictionary of disk statistics from a Netgear ReadyNAS

```python

from snmp_utilities import SnmpQuery

host = 'readynas.example.com'
community_string = 'public'
snmp = SnmpQuery()

disk_entries = snmp.get_next(host,
                             [
                                 {'READYNASOS-MIB': 'diskNumber'},
                                 {'READYNASOS-MIB': 'ataError'},
                                 {'READYNASOS-MIB': 'diskState'},
                                 {'READYNASOS-MIB': 'diskTemperature'}
                             ], snmp.construct_credentials(False, community_string))

print(snmp.get_snmp_name(host, community_string))  # Print the hostname

for disk_entry in disk_entries:
    # Iterate over dictionary of entries

    for key, value in disk_entry.items():
        # Iterate over fields

        print(snmp.get_brief_name(key) + ': ' + str(value))

```

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