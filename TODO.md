ToDo list for pylint
====================

New ideas should be described as issues on GitHub, and not on this list.

2. Extend logging for more flexibility.

3. Consider extending all subcommands that ask for target id to:
   a. select from list (This can be messy becasuse list could be long)
   b. filter by options like company, etc
   c. Allow multip ids and id ranges.

4. Clean up and simplify documentation.

6. Implement travis testing

7. Move to python 3.  The only thing holding us at python 2.7 is the serversweep
   port test (SYN test) because it uses scapy, a python library that has not
   been ported to python 3.  The advantage of python 3 is that is removes
   issues about the mo2crypto install and makes this a pure python
   implementaiton.  Will greatly simplify installation on new systems

8. Add windows as a target.

9. Extend the provider group to inspect other components of the server. Note
   that we will try to put these into pywbem and just use them

10. Complete add/delete/modify for all table types

11. Start to use cimconfig loadable ref to get config file.

12. Force use of the config file all the time.
