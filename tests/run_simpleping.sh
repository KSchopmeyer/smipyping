#!/bin/bash

#
#  Hacked script to test simpleping.  This should be part of unittest but
#  for the moment this works.  Note that
#

GLOBALRESULT=0
function simplepingtest()
{
    echo simpleping $1   should return $2
    simpleping $1
    result_code=$?
    if [ $result_code -ne $2 ]; then
        echo Result. Result code mismatch. expected $2 received $result_code
        if [ GLOBALRESULT=0 ]; then
            GLOBALRESULT=1
        fi        
        return 1
    fi
    return 0
}
# These tests do not require a server
simplepingtest "http://localhostx -n root/cimv2" 6
simplepingtest "http://localhost -n root/cimv2x" 1
simplepingtest "http://localhost --help" 0
simplepingtest "http://localhost" 2
simplepingtest "http://localhost, -T 4" 1 

# This test fails if server not present
simplepingtest "http://localhost -n root/cimv2" 0

if [ $GLOBALRESULT -ne 0 ]; then
    echo Error in test!!!!!!!!!!!!!!!!!!!!!
fi
exit $GLOBALRESULT

    
