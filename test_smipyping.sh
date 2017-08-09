#!/bin/bash
#
#   Test script in bash for smicli commands.  This executes the commands
#   and displays results.  The only tests it does are for error or good
#   commands.
#   This is just a quick test and does not replace detailed unit tests
#

REMOTE=0
CMD=smicli
function do_cmd {
    echo CMD: $CMD$1
    $CMD $1
    error=$?
    if ((error > 0)); then
        echo ERROR: %1 Error $error
        exit
    fi
}

function do_cmd_er {
    echo CMD: $CMD$1
    $CMD $1
    error=$?
    if ((error == 0)); then
        echo ERROR: Non zero code expected: %1 Error $error
        exit
    fi
}    

# top level
do_cmd '--help'

# targets
do_cmd 'targets fields'
do_cmd 'targets info'
do_cmd 'targets get 4'
do_cmd 'targets list'
do_cmd 'targets list  -f CompanyName -f Credential -f Principal'
do_cmd_er 'targets list  -f CompanyNamex'

if [[REMOTE == 0]]; then
    echo "Do not execute against remote system"
    exit
#
# cimping
#
# host id
do_cmd 'cimping ids 4'
do_cmd 'cimping host http://localhost'


#
# Provider commands
#
# classes, info, interop, namespaces, ping profiles
do_cmd 'provider 

