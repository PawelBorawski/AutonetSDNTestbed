#!/usr/bin/env python
# coding=utf-8
import argparse
import json

from mngen.models import HostDistribution, TrafficParams
from mngen.models import RunTestParams
from mngen.test_creator import TestCreator
from mngen.test_launcher import TestLauncher
import mngen.util as util
from config import TOPOLOGIES_DIR, SCENARIOS_DIR, LOGS_DIR

EPILOG = """
Topologies:
-----------
Topologies are located in {0}.

Scenarios:
----------
Scenario are located in {1} that contains XML files.
Each scenario should be in separate XML.

Logs:
----------
Logs are located in {2}.
Logs from each scenario are in separate dir under {2}/$TESTNAME.

Example usage:
--------------
Create scenario 'test':
    ./mngen_cli.py create
Run scenario 'test':
    sudo ./mngen_cli.py run -s <scenario_name>
List topologies:
    ./mngen_cli.py ctl -lt
List available scenarios:
    ./mngen_cli.py ctl -ls
""".format(TOPOLOGIES_DIR, SCENARIOS_DIR, LOGS_DIR)


def cli_create_scenario(args):

    if (args.random_distribution):
        distribution = HostDistribution.RANDOM
    else:
        distribution = HostDistribution.UNIFORM

    traffic = TrafficParams({'min_flows': args.min_flows,
                             'max_flows': args.max_flows,
                             'min_bitrate': args.c_min,
                             'max_bitrate': args.c_max,
                             'traffic_type': args.traffic_type,
                             'max_delay': args.delay,
                             'max_duration': args.duration})

    creator = TestCreator()
    creator.generate_test(
        args.scenario_name,
        args.topology,
        args.bandwidth,
        args.hosts,
        distribution,
        traffic)


def cli_run_scenario(args):
    data = dict()
    data['scenario'] = args.scenario
    data['iterations'] = int(args.iterations)
    if args.controller_port and args.controller_port:
        data['controller_ip'] = args.controller_ip
        data['controller_port'] = int(args.controller_port)

    launcher = TestLauncher()
    params = RunTestParams(data)
    launcher.run_test(params)


def cli_ctl(args):
    if args.list_scenarios:
        cli_list_scenarios()
    elif args.list_topologies:
        cli_list_topologies()


def cli_list_scenarios():
    print json.dumps(util.get_scenarios(), indent=4, sort_keys=True)
    exit(0)


def cli_list_topologies():
    print json.dumps(util.get_topologies(), indent=4, sort_keys=True)
    exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="Launches test scenario in Mininet.",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers()

    ctl_parser = subparsers.add_parser('ctl', help='run ctl')
    ctl_parser.add_argument("-lt", "--list-topologies", action="store_true",
                            help="list available topologies")

    ctl_parser.add_argument(
        "-ls",
        "--list-scenarios",
        action="store_true",
        help="list available scenarios")

    ctl_parser.set_defaults(func=cli_ctl)

    # create parser for 'run' command and associate arguments and method
    run_scenario_parser = subparsers.add_parser('run', help='run help')
    run_scenario_parser.add_argument(
        "-s",
        "--scenario",
        help="Name of Mininet test scenario",
        required=True)
    run_scenario_parser.add_argument(
        "-i",
        "--iterations",
        default=1,
        help="Number of test iterations (default: 1)")
    run_scenario_parser.add_argument(
        "-c",
        "--controller_ip",
        help="IP address of SDN controller")
    run_scenario_parser.add_argument(
        "-p",
        "--controller_port",
        help="Port number of SDN controller")
    run_scenario_parser.set_defaults(func=cli_run_scenario)

    # create parser for 'create' command and associate args and method
    create_scenario_parser = subparsers.add_parser(
        'create', help='create help')
    create_scenario_parser.add_argument(
        "-s",
        "--scenario-name",
        help="Name of scenario",
        required=True)
    create_scenario_parser.add_argument(
        "-t",
        "--topology",
        help="Name of topology to use",
        required=True)
    create_scenario_parser.add_argument(
        "-B",
        "--bandwidth",
        default=1,
        help="Bandwidth of links in Mbit/s (default: 1 Mbit/s)")
    create_scenario_parser.add_argument(
        "-H",
        "--hosts",
        default=1,
        help="Number of hosts ('per switch' for uniform distribution)")
    create_scenario_parser.add_argument(
        "-R",
        "--random-distribution",
        default=False,
        action='store_true',
        help="Random hosts distribution in network (default: uniform)")
    create_scenario_parser.add_argument(
        "-o",
        "--logs-dir",
        help="directory for storing logs (default: logs/ in scenario directory). Implies storing logs")
    create_scenario_parser.add_argument(
        "-i",
        "--iterations",
        type=int,
        default=1,
        help="Number of test case interations (-1 for infinite). Warning: Logs will be overridden")
    create_scenario_parser.add_argument(
        "-T",
        "--traffic-type",
        default='UDP',
        help="Type of generated traffic (TCP, UDP or RANDOM")
    create_scenario_parser.add_argument(
        "--c_min", default=1, help="Minimum bitrate of generated traffic")
    create_scenario_parser.add_argument(
        "--c_max", default=1, help="Maximum bitrate of generated traffic")
    create_scenario_parser.add_argument(
        "-C", "--clients", help="Number of clients generating traffic")
    create_scenario_parser.add_argument(
        "-minf",
        "--min-flows",
        default=1,
        help="Min number of flows per client")
    create_scenario_parser.add_argument(
        "-maxf",
        "--max-flows",
        default=1,
        help="Max number of flows per client")
    create_scenario_parser.add_argument(
        "--delay",
        help="Maximum delay of particular flow",
        required=True)
    create_scenario_parser.add_argument(
        "--duration",
        help="Maximum duration of particular flow",
        required=True)
    create_scenario_parser.set_defaults(func=cli_create_scenario)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
