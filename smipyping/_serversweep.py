
"""
Server sweep functions.

These functions allow sweeping a set of subnets for specific open
ports.

WARNING: Because the sweep uses SYN to test for an open https port this
code must be executed in privileged mode. That is a python requirement.

While  other tests can detect open http ports, we must detect an open
https port so the choices of test are limited.
"""

from __future__ import print_function, absolute_import
import sys
import time
import argparse as _argparse
import threading
import itertools
import six

from ._cliutils import SmartFormatter as _SmartFormatter
from ._cliutils import check_negative_int
from .config import DEFAULT_SWEEP_PORT
from ._utilities import display_argparser_args
from ._scanport import check_port_syn

# Results list, a list of tuples of ip_address, port. May be appended
# multithread
RESULTS = []


def check_port(test_ip, port, verbose):
    """
    Runs define test against a single ip/port.

    If the port is OK, sets results into RESULTS

    This may be used either single threaded or multithreaded

    Returns True if port OK
    """
    result = check_port_syn(test_ip, port, verbose)  # Test one ip:port
    if result is True:
        RESULTS.append([test_ip, port])
    return result


def expand_subnet_definition(net_def, min_val=1, max_val=254):
    """
    Get a list of IP addresses from the net_definition provided in net_def.

    The syntax for the net definition is as follows:

    Defines for octets of an IPV4 address where each octet is one of the
    following:

      Integer representing the octet.

      Range definition for the octet defining the range of values in the
      expansion.  The syntax of the range definition is <nin>:<max> where
      min and max are integers.  Thus, 3:10 expands to all values from 3 to
      10 (inclusive) for that octet of the IP address

      List definition consists of list of values separated by commans. All of
      the values in the list are included in the expansion.

      Any missing octets are expanded to the range definition between
      the input parameters min_val and max_val

      Returns a list of the IP address that make up this expansion

      Parameters:

        net_def: String. See above for syntax

        min_val - minimum value for the expand any missing octets in the
        net definition

        max_val - maximum value for the range expand for any missing octets
        in the net definition

      Returns:  A generator that returns ip addresses until the expansion
      is exhausted.

      Exceptions:
        ValueError if any of the components of the net definition are in
        error.
    """
    octet_max = 255
    # try:
    #    octets = expand_subnet_def(subnet_def, min_ip, max_ip)
    # except Exception as ex:
    #    print('Exception subnet %s Exception %s' % (subnet_def, ex))
    #    raise

    try:
        octets = net_def.split('.')
        ipv4_octet_count = 4
        for index in range(ipv4_octet_count):
            try:
                octets[index]
            except IndexError:
                octets.append('%d:%d' % (min_val, max_val))
    except Exception as ex:
        print('Exception subnet %s Exception %s' % (net_def, ex))
        raise

    octet_lists = []
    try:
        for octet in octets:
            if octet.isdigit():
                try:
                    octet = int(octet)
                except Exception as ex:
                    raise ValueError('octet %s not integer' % octet)
                octet_lists.append([octet])
            elif ':' in octet:
                range_ = octet.split(':')
                min_ = int(range_[0])
                max_ = int(range_[1]) + 1    # range is inclusive
                if len(range_) != 2:
                    raise ValueError('Range %s invalid. Too many components' %
                                     range_)
                if min_ < 0:
                    raise ValueError('Value %s in range %s invalid' % (min_,
                                                                       range_))
                if max_ > octet_max:
                    raise ValueError('Value %s in range %s invalid. gt %s' %
                                     (max_, range_, octet_max))
                if max_ <= min_:
                    raise ValueError('Value %s must be gt %s in  def %s' %
                                     (max_, min_, octet))

                octect_list = [item for item in six.moves.range(min_, max_)]
                octet_lists.append(octect_list)
            elif ',' in octet:
                items = octet.split(',')
                octet_lists.append([int(x) for x in items])
            else:
                raise ValueError('Invalid octet %s in net definition %s' %
                                 (octet, net_def))
    except ValueError:
        raise

    # product_get, a generator that iproduces results of merged lists
    for ip in itertools.product(*octet_lists):
        yield '.'.join(map(str, ip))  # pylint: disable=bad-builtin


def scan_subnets(subnets, start_ip, end_ip, port, verbose):
    """
    Nonthreaded scan of IP addresses for open ports.

    Scan a subnet and return list of hosts found with port open.

    Subnet can be either a specific subnet or a list of subnets
    Ports can be either single port or list of ports
    Returns Dictionary of hosts that have defined port open.
    """
    open_hosts = []

    # if subnets or port is list, recursively call with each entry
    if isinstance(subnets, list):
        for subnet in subnets:
            rtn = scan_subnets(subnet, start_ip, end_ip, port, verbose)
            if rtn is not None:
                open_hosts.extend(rtn)
        return open_hosts

    # if ports is list, make recursive call for ports
    if isinstance(port, list):
        for p in port:
            rtn = scan_subnets(subnets, start_ip, end_ip, p, verbose)
            if rtn is not None:
                open_hosts.extend(rtn)
        return open_hosts

    # scan ports in this range
    for ip in range(start_ip, end_ip + 1):
        test_ip = subnets + '.' + str(ip)
        test_host_id = [test_ip, port]

        result = check_port(test_ip, port, verbose)  # Test one ip:port

        # print('test %s %s result %s' % (test_ip, port, result))

        if verbose:
            response_txt = 'Exists' if result else 'None'
            print('test address=%s, %s' % ((test_host_id,), response_txt))
        else:
            sys.stdout.flush()
            addr_ = "%s:%s" % (test_host_id[0], test_host_id[1])
            sys.stdout.write(addr_)
            if not test_ip == end_ip:
                sys.stdout.write('\b' * (len(addr_) + 4))

        if result:  # Port exists
            open_hosts.append(test_host_id)  # Append to list

    return open_hosts


def scan_subnets_threaded(subnets, start_ip, end_ip, port, verbose):
    """
    Threaded scan of IP Addresses for open ports.

    Scan the IP address defined by the input and return a list of open
    IP addresses. This function creates multiple processes and executes
    each call in a process for speed.
    """

    # TODO modify this so we use a queue since the user can not force
    # hundreds of scans with the net definition mechanism.
    # Queue will set the max threads to execute in parallel.

    threads_ = []
    for test in build_test_list(subnets, start_ip, end_ip, port):
        thread_ = threading.Thread(target=check_port, args=(test[0],
                                                             test[1],
                                                             verbose))
        threads_.append(thread_)
    # pylint: disable=expression-not-assigned
    [process.start() for process in threads_]
    [process.join() for process in threads_]

    open_hosts = [result for result in RESULTS]

    return open_hosts


def build_test_list(net_defs, start_ip, end_ip, ports):
    """
    Create list of IP addresses and ports to scan.

    Create dictionary of IP address: port for all ports in the ranges
    defined by the input parameters and return that dictionary

    Parameters:

      net_defs:
        single net definition or list of net definitions.

      start_ip:
        min value of any octets in net_defs that are not defined

      end_ip:
        max value for any octets in net_def that are not defined

      ports:
        single port or list of ports to scan

    Returns:
      Generator that generates a set of the combination of net defs and
      ports until the combinations are exhausted.
    """

    if not isinstance(net_defs, list):
        net_defs = [net_defs]

    if not isinstance(ports, list):
        ports = [ports]

    for net_def in net_defs:
        for test_ip in expand_subnet_definition(net_def, start_ip, end_ip):
            for port_ in ports:
                yield test_ip, port_


def print_open_hosts_report(open_hosts, total_time, provider_data, subnets,
                            ports, startip, endip):
    """
    Output report of the entries found.

    If userdata is found, include the userdata info including CompanyName,
    Product, etc.
    """
    print('\n')
    print("=" * 50)
    execution_time = ''
    if total_time <= 60:
        execution_time = "%.2f sec" % (round(total_time, 1))
    else:
        execution_time = "%.2f min" % (total_time / 60)

    range_txt = '%s:%s' % (startip, endip)

    if len(open_hosts) != 0:
        print('Open WBEMServers:subnet(s)=%s port(s)=%s range %s, %s count %s'
              % (subnets, ports, range_txt, execution_time, len(open_hosts)))
        # open_hosts.sort(key=lambda ip: map(int, ip.split('.')))
        # TODO this probably requires ordered dict rather than dictionary to
        # keep order
        for host_data in open_hosts:
            if provider_data is not None:
                record_list = provider_data.get_targets_host(host_data)
                if record_list:
                    # TODO this should be a list since there may be multiples
                    # for single ip address
                    entry = provider_data.get_dict_record(record_list[0])
                    if entry is not None:
                        print(
                            '%s:%s %-20s %-18s %-18s' % (host_data[0],
                                                         host_data[1],
                                                         entry['CompanyName'],
                                                         entry['Product'],
                                                         entry['SMIVersion']))
                    else:
                        print('Invalid entry %s %s:%s %s' % (
                            record_list[0], host_data[0], host_data[1],
                            "Not in user data"))
                else:
                    print('%s:%s %s' % (host_data[0], host_data[1],
                                        "UnknownServer"))

            else:
                print('%s, %s' % (host_data[0], host_data[1]))
    else:
        print('No WBEM Servers:subnet(s)=%s port(s)=%s range %s, %s' %
              (subnets, ports, range_txt, execution_time))
    print("=" * 50)


def sweep_servers(subnets, startip, endip, ports, no_threads, user_data,
                  verbose):
    """
    Execute the scan on the subnets defined by the input parameters.

    Parameters:
      subnets: list of subnets. Each subnet is defined as a sweep range where
      the sweep range for each component of the ip address is either an
      integer (designates a single address) or a range (integer:integer)

      startip: start ip for the scan on each subnet

      endip: Last ip to include in scan

      ports: list of ports to scan

      no_threads: Boolean. Use non-threaded implementation if True. The
      default is to use the threaded implementation

      verbose: detailed display if True

      Returns:
          List of hosts results as a tuple of (ip, port) for hosts with
          open ports in the defined range of subnets and ports input
    """
    start_time = time.time()   # Scan start time

    try:
        open_hosts = []

        if no_threads:
            scan_results = scan_subnets(subnets, startip,
                                        endip, ports, verbose)
        else:
            scan_results = scan_subnets_threaded(subnets, startip,
                                                 endip, ports, verbose)
        if scan_results is not None:
            open_hosts.extend(sorted(scan_results))

    except KeyboardInterrupt:
        # Used in case the  user press "Ctrl+C", it will show the
        # following error instead of a python scary error
        print("\nCtrl+C. Exiting with no output.")
        sys.exit(1)

    total_time = time.time() - start_time

    print_open_hosts_report(open_hosts, total_time, user_data, subnets, ports,
                            startip, endip)


def create_sweep_argparser(prog_name):
    """
    Create the argument parser for server sweep cmd line.

    Returns the created parser.
    """
    prog = prog_name  # Name of the script file invoking this module
    usage = '%(prog)s [options] subnet [subnet] ...'
    desc = 'Sweep possible WBEMServer ports across a range of IP subnets '\
           'and ports to find existing open WBEM servers.'
    epilog = """
Examples:
  %s 10.1.134 --startip=1 --endip=254
        The above example will scan the subnets 10.1.134 from 1 to 254
  %s 10.1.134
        Scan a complete subnet, 10.1.134 for the default port (5989)
  %s 10.1.132 10.1.134 -p 5989 -p 5988
        Scan 10.1.132 and 10.1.134 for ports 5988 and 5989

""" % (prog, prog, prog)

    argparser = _argparse.ArgumentParser(
        prog=prog, usage=usage, description=desc, epilog=epilog,
        formatter_class=_SmartFormatter)

    pos_arggroup = argparser.add_argument_group(
        'Positional arguments')
    pos_arggroup.add_argument(
        'subnet', metavar='subnet', nargs='+',
        help='IP subnets to scan (ex. 10.1.132). Multiple subnets allowed. '
             'Each subnet definition is itself a definition that consists '
             'of octets that are integers, range definitions, or integer '
             'lists. A range expansion is in the form int:int which defines '
             'the mininum and maximum values for that octet. '
             'A list expansion is in the form int, int, int that defines '
             'the set of valuse for that octet. '
             'Examples: 10.1.132,134 expands to addresses in 10.1.132 and '
             '10.1.134.')

    subnet_arggroup = argparser.add_argument_group(
        'Scan related options',
        'Specify parameters of the subnet scan')
    subnet_arggroup.add_argument(
        '--startip', '-s', metavar='Start', nargs='?', default=1,
        type=check_negative_int,
        help='Start scanning from this IP')
    subnet_arggroup.add_argument(
        '--endip', '-e', metavar='End', nargs='?', default=254,
        type=check_negative_int,
        help='Scan to this IP')
    subnet_arggroup.add_argument(
        '--port', '-p', nargs='?', action='append', type=int,
        help='Port(s) to test. This argument may be repeated to test '
             'multiple ports')

    general_arggroup = argparser.add_argument_group(
        'General options')
    general_arggroup.add_argument(
        '--config_file', '-c',
        help='Use config file to determine if server is in database')
    # TODO note that default is none and that is what happensw
    general_arggroup.add_argument(
        '--no_threads', action='store_true', default=False,
        help='If set, defaults to non-threaded implementation. The'
             ' non-threaded implementation takes much longer to execute.')
    general_arggroup.add_argument(
        '--verbose', '-v', action='store_true', default=False,
        help='If set output detail displays as test proceeds')

    return argparser


def parse_sweep_args(argparser):
    """
    Process the cmdline arguments including any default substitution.

    This is based on the argparser defined by the create... function.

    Either returns the args or executes argparser.error
    """
    args = argparser.parse_args()

    if not args.subnet:
        argparser.error('No Subnet specified. At least one subnet required.')

    # set default port if none provided.
    if args.port is None:
        # This is from a variable in config.py
        args.port = [DEFAULT_SWEEP_PORT]

    if args.verbose:
        display_argparser_args(args)

    return args
