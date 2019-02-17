#!/bin/bash
#
#   Test script in bash for smicli commands.  This executes the commands
#   and displays results.  The only tests it does are for error or good
#   commands.
#   This is just a quick test and does not replace detailed unit tests
#

function USAGE {
cat << EOF
Usage: `basename $0` <parameters> ;

Execute smicli script with parameters:
    -h --help      Output the help information on this script and exit
    -r --remote     Execute tests that depend on being in smi environment
    -l --locallive Execute tests that depend on local server running
EOF
}

REMOTE=0
LOCAL_LIVE=0
CMD=smicli

VALID_TARGET_ID=115

# Execute script and report if any errors occur
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

# top level
do_cmd '--help'

# targets
do_cmd 'targets fields'
do_cmd 'targets info'
do_cmd 'targets get 89'
do_cmd 'targets list'
do_cmd 'targets list  -f CompanyName -f Credential -f Principal'
do_cmd_er 'targets list  -f CompanyNamex'

# programs

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

# history

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
