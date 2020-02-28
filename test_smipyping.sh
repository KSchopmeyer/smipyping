#!/bin/bash
#
#   Test script in bash for smicli commands.  This executes the commands
#   and displays results.  The only tests it does are for error or good
#   commands.
#   This is just a quick test and does not replace detailed unit tests
#
#  It runs against the configuration defned in the CONFIGFILE varaible

function USAGE {
cat << EOF
Usage: `basename $0` <parameters> ;

Execute smicli script with parameters:
    -h --help      Output the help information on this script and exit
    -r --remote    Execute tests that depend on being in smi environment
    -l --locallive Execute tests that depend on local server running
    -t --testmods  Execute tests that modify db
EOF
}

REMOTE=0
LOCAL_LIVE=0
CMD=smicli
MOD_DB=False

VALID_TARGET_ID=115
NOT_VALID_TARGETID=900
CONFIGFILE='smicli.ini'

# TODO test that remote exists
ping 10.2.119.20 -c 3
PING_ERR=$?
if ((PING_ERR > 0)); then
    echo ERROR: %1 Error $PING_ERR
    exit
fi

# find all servers that return OK and create single line list of target ids
OKS="$(smicli cimping all | grep OK | cut -c-5 | tr '\n' ' ' | paste -sd' ')"
#echo "${OKS}"
IFS=', ' read -r -a OKS_ARRAY <<< "$OKS"
echo "${OKS_ARRAY[0]}"
VALID_TARGET_ID = "${OKS_ARRAY[0]}"


# Execute script and report if any errors occur
# Parameter 1 is the command with all options.
# Parameter 2 data for comparison of return TODO
function do_cmd {
    echo
    echo CMD: $CMD $1
    $CMD $1
    #if [ $# -lt 2 ]
    #then
    #    $CMD $1
    #else
    #    echo $2 | $CMD $1
    #fi
    error=$?
    if ((error > 0)); then
        echo ERROR: %1 Error $error
        exit
    fi
}

function do_expect {
    echo
    expect <<EOF
    $CMD $1
    expect $2
    send $3
EOF
    error=$?
    if ((error > 0)); then
        echo ERROR: %1 Error $error
        exit
    fi
}


# Execute script expecting non-zero exit code response
function do_cmd_er {
    echo
    echo CMD: $CMD $1
    $CMD $1
    error=$?
    if ((error == 0)); then
        echo ERROR: Non zero code expected: %1 Error $error
        exit
    fi
    echo ExitCode $error received
}

for i in "$@"
do
case $i in
    -h|--help)
        USAGE
        exit 1
    ;;

    -r|--remote)
        REMOTE=1
    ;;

    -l|--locallive)
        LOCALLIVE=1
    ;;

    -t|--testmods)
        TEST_MODS=1
    ;;

    -l=*|--lib=*)
    LIBPATH="${i#*=}"
    shift # past argument=value
    ;;
    --default)
    DEFAULT=YES
    shift # past argument with no value
    ;;
    *)
        echo "Unknown argument $1"
        USAGE
        exit 1
    ;;
esac
done
echo "REMOTE  = ${REMOTE}"

# Place to test single call
#exit

# top level
do_cmd '--help'

# targets
do_cmd 'targets -h'
do_cmd 'targets fields'
do_cmd 'targets info'
do_cmd "targets get ${VALID_TARGET_ID}"
do_cmd 'targets list'
do_cmd 'targets list  -f CompanyName -f Credential -f Principal'
do_cmd_er 'targets list  -f CompanyNamex'
do_cmd_er 'targets delete 900'
# delete, disable, modify, new

# companies

do_cmd 'companies -h'
do_cmd 'companies list -h'
do_cmd 'companies add -h'
do_cmd 'companies delete -h'
do_cmd 'companies modify -h'
do_cmd 'companies list'
do_cmd 'companies add  -c BlahBlah'
# This one needs a response. Our autoresponse fails. User answer n
do_cmd 'companies list'
do_cmd_er 'companies delete 900'
# Cannot do modify or delete, we do not know the id of the company

# users
do_cmd 'users list'
do_cmd 'users list --disabled'
do_cmd 'users list --disabled'
do_cmd 'users list -f FirstName -f Lastname'
do_cmd 'users list -f FirstName -f Lastname -f CompanyName -o CompanyName'
do_cmd_er 'users list -f blah'
do_cmd_er 'users delete 900'

# history

do_cmd "history -h"
do_cmd "history timeline -h"
do_cmd "history timeline -t 89  -s 01/02/19 -n 20"
do_cmd "history timeline -t 89 -t 81  -s 01/02/19 -n 20"
do_cmd "history timeline  -s 01/02/19 -n 2"


do_cmd "history list -h"
do_cmd "history list -t 89  -s 01/02/19 -n 20"
do_cmd "history list -t 89 -t 81  -s 01/02/19 -n 20"
do_cmd "history list  -s 01/02/19 -n 20"

do_cmd "history overview -h"
do_cmd "history overview"

#companies

# The following commands can be executed only if there is a set of valid
# servers.

if [[REMOTE == 0]]; then
    echo "Do not execute against remote system"
    exit
fi
#
# cimping
#
# host id
do_cmd_er 'cimping ids 999'
do_cmd 'cimping ids 89'
# host name
do_cmd 'cimping host http://localhost'
# all
do_cmd 'cimping all'

#
# Provider commands
#
# classes, info, interop, namespaces, ping profiles
do_cmd "provider interop "$VALID_TARGET_ID
do_cmd "provider namespaces "$VALID_TARGET_ID
do_cmd "provider profiles "$VALID_TARGET_ID
do_cmd "provider profiles "$VALID_TARGET_ID" -o SNIA"
do_cmd "provider profiles "$VALID_TARGET_ID" -n SMI-S"
do_cmd "provider classes "$VALID_TARGET_ID" -c CIM_ManagedElement"
do_cmd "provider classes "$VALID_TARGET_ID" -s"

#
#   Exercise explorer
#

do_cmd 'explorer all'
do_cmd 'explorer ids 89'

# sweep commands
