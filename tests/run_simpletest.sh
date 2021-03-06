#!/bin/bash
#
# Simply executes all subcommands with options that do not require input
# assumes that the test servers are connected. This does not test for
# valid response date or even zero exception code.
#

VALID_TARGET_ID=81
VALID_TARGETID_2=83
USER_TO_DEACTIVATE=82

ALLOW_UDPATE_TESTS=false

# Test to see if we can talk to the test implementation
ping 10.2.119.20 -c 1
retval=$?
if [ $retval -ne 0 ]; then
    echo "Ping Return code was not zero but $retval"
    exit 1
fi

function run_smicli {
    smicli $1
    retval=$?
    if [ $retval -ne 0 ]; then
        echo "Call smicli $1 failed with: $retval"
        exit 1
    fi
}

smicli --help

smicli companies list --help
smicli companies list

# Does not cover add, modify, delete

smicli programs --help
smicli programs current -h
smicli programs current
smicli programs list -h
smicli programs list

# does not cover add and delete

smicli history -h
smicli history overview -h
smicli history overview
smicli history weekly list -s 01/01/17 -e 01/01/18 -r count
smicli history weekly list -s 01/01/17 -e 01/01/18 -r %ok
smicli history weekly list -s 01/01/17 -e 01/04/18 -r status
smicli history weekly list -s 01/01/17 -e 01/04/18 -r changes
smicli history weekly list -t $VALID_TARGET_ID -s 01/01/17 -e 01/02/18 -r full
smicli history weekly list -s 01/01/17 -n 300 -r count
smicli history weekly list -s 01/01/17 -n 300 -r %ok
smicli history weekly list -s 01/01/17 -n 300 -r status
smicli history weekly list -s 01/01/17 -n 300 -r changes
smicli history weekly list -n 300 -r count
smicli history weekly list -n 300 -r %ok
smicli history weekly list -n 300 -r status
smicli history weekly list -n 300 -r changes

# TODO cover issues where -s missing.

smicli weekly list  -s 01/01/17 -e 01/01/18 -r %ok
# do not cover activate, delete, add, modify

smicli targets --help
smicli targets fields --help
smicli targets fields
smicli targets get --help
smicli targets get $VALID_TARGET_ID
smicli targets list --help
smicli targets list -o Product
smicli targets list -f CompanyName -f Product


smicli users --help
smicli users list --help

smicli users list
smicli users list -o CompanyName
smicli users list -f CompanyName -f CompanyID -f FirstName
smicli users list -d

smicli users activate -h
if [ $ALLOW_UDPATE_TESTS=true]; then
    smicli users activate $USER_TO_DEACTIVATE --active
    smicli users activate $USER_TO_DEACTIVATE --inactive
fi

smicli programs -h
smicli programs list -h
smicli programs list

# Does not test add or delete

smicli cimping --help
smicli cimping all --help
smicli cimping all
smicli cimping id --help
smicli cimping id $VALID_TARGET_ID
smicli cimping ids --help
smicli cimping ids $VALID_TARGET_ID $VALID_TARGET_ID2

smicli explorer --help
smicli explorer all --help
smicli explorer all --ping
smicli explorer all --no-ping
smicli explorer all -i
smicli explorer all --detail full
smicli explorer all --detail brief
smicli explorer all --detail all
smicli explorer all
smicli explorer all --include-disabled
smicli explorer ids 122 $VALID_TARGET_ID2 $VALID_TARGET_ID --detail full

smicli explorer ids --help
smicli explorer ids $VALID_TARGET_ID $VALID_TARGET_ID2

smicli provider -h
smicli provider classes -h
smicli provider classes $VALID_TARGET_ID -s
smicli provider classes $VALID_TARGET_ID
smicli provider classes $VALID_TARGET_ID -c CIM_Disk

smicli provider info $VALID_TARGET_ID
smicli provider namespaces $VALID_TARGET_ID
smicli provider interop $VALID_TARGET_ID
smicli provider ping $VALID_TARGET_ID
smicli provider profiles $VALID_TARGET_ID
smicli provider profiles $VALID_TARGET_ID -o SNIA
smicli provider profiles $VALID_TARGET_ID -o SNIA -n Array
smicli provider profiles $VALID_TARGET_ID -o SNIA -n Array -v 1.5.0

smicli sweep --help
smicli sweep nets --help
smicli sweep nets -s 10.1.132 -p 5988 -p 5989 --dryrun
smicli sweep nets -s 10.1.132 -p 5988 -p 5989
