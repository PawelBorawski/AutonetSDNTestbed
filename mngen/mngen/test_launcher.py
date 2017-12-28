#!/usr/bin/env python
# coding=utf-8
"""@package test_launcher

Mininet test scenario launcher
@author Tomasz Osiński (osinstom@gmail.com), Paweł Borawski ()
"""

import argparse
import multiprocessing
import os
import time
from functools import partial
from xml.dom import minidom
import logging

from mininet.clean import cleanup
import mininet.node
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.net import Mininet
from mininet.node import RemoteController, OVSController

import util
from config import SCENARIOS_DIR, LOGS_DIR
from mngen.models import Flow, TrafficTool, RunTestParams
from test_tool import TestToolIperf
from mngen.exceptions import MininetIsBusyError

_flows = []
INITIALIZATION_DELAY = 3  # in seconds


class TestTopo(Topo):

    def __init__(self, scenario, **opts):
        self.logger = logging.getLogger('mngen_api')
        self.logger.info("Running scenario... '{}'".format(scenario))
        # Initialize Topology
        Topo.__init__(self, **opts)
        self.logger.info("Create a topology for scenario '{}'".format(scenario))
        self.create_topology_from_xml(scenario)

    def create_topology_from_xml(self, scenario):
        """ Create Mininet topology using scenario description from XML file.\n
        Reads XML file and invokes Mininet Python API methods.\n
        :param scenario:
        """

        hosts = []
        switches = []

        DOMTree = minidom.parse(scenario)

        cNodes = DOMTree.childNodes

        n_switches = cNodes[0].getElementsByTagName("switches")
        n_hosts = cNodes[0].getElementsByTagName("hosts")
        n_links = cNodes[0].getElementsByTagName("links")
        n_flows = cNodes[0].getElementsByTagName("flows")

        for n in n_switches[0].getElementsByTagName("switch"):
            datapathid = n.getAttribute("dpid")
            id = n.getAttribute("id")
            if datapathid is not None:
                switches.append(self.addSwitch(str(id), dpid=str(datapathid)))
            else:
                switches.append(self.addSwitch(str(id)))

        for h in n_hosts[0].getElementsByTagName("host"):
            id = h.getAttribute("id")
            hosts.append(self.addHost(str(id)))

        for l in n_links[0].getElementsByTagName("link"):
            src = l.getAttribute("src")
            dst = l.getAttribute("dst")
            latency = l.getAttribute("latency")
            bandw = l.getAttribute("bw")
            if l.getAttribute("type") == "network":
                self.addLink(switches[switches.index(src)],
                             switches[switches.index(dst)],
                             bw=float(bandw),
                             delay=str(latency))
            if l.getAttribute("type") == "host":
                self.addLink(switches[switches.index(src)],
                             hosts[hosts.index(dst)])

        for f in n_flows[0].getElementsByTagName("flow"):
            src = f.getAttribute("src")
            dst = f.getAttribute("dst")
            c_rate = f.getAttribute("c_rate")
            delay = f.getAttribute("delay")
            l4type = f.getAttribute("l4type")
            duration = f.getAttribute("duration")
            _flows.append(Flow(src, dst, delay, c_rate, l4type, duration))


class TestWorker():

    def __init__(self, params, process):
        self.params = params
        self.process = process

    def get_params(self):
        return self.params

    def get_process(self):
        return self.process


class TestLauncher():

    def __init__(self):
        self.logger = logging.getLogger('mngen_api')
        self.tasks = list()
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)

    def is_autonet_alive(self):
        for p in self.tasks:
            if p.get_process().is_alive():
                return True
        return False

    def run(self, params):
        if self.is_autonet_alive():
            raise MininetIsBusyError
        p = multiprocessing.Process(
            name="autonet",
            target=self.run_test,
            args=(
                params,
            ))
        worker = TestWorker(params, p)
        self.tasks.append(worker)
        worker.get_process().start()

        self.logger.info("Starting {} {} ".format(p.name, p.pid))

    def stop(self):
        os.system('sudo mn -c')
        for worker in self.tasks:
            p = worker.get_process()
            if p.is_alive():
                if worker.get_params().tool == TrafficTool.IPERF:
                    os.system('pkill -9 iperf')
                p.terminate()
                p.join()
                self.logger.info("[TERMINATED] Process '{}', pid={}".format(p.name, p.pid))
        del self.tasks[:]
        del _flows[:]

    def run_test(self, params):
        """ Run test using provided scenario.\n
        Creates Mininet network and pushes traffic between hosts.\n
        :param scenario:
        :param tool:
        """

        self.cleanup_mn_env()

        # load topo from XML and parse it to Mininet topology abstraction
        topo = TestTopo(SCENARIOS_DIR + params.scenario + ".xml")

        # check if params contain remote controller IP and port, if not: use default OVS controller
        # TODO: OVSController is not working yet
        if params.controller_ip is not None and params.controller_port is not None:
            ctrl = partial(
                RemoteController,
                ip=params.controller_ip,
                port=params.controller_port)
        else:
            ctrl = partial(OVSController)
            self.logger.info('Running default OVS Controller..')

        # create Mininet network
        net = Mininet(topo=topo, controller=ctrl, link=TCLink) # host=CPULimitedHost)
        self.logger.info("Starting network..")

        net.start()
        # no need to run ARP broadcast in network
        net.staticArp()
        # net.pingAll()

        logs_dir = util.prepare_logs_dir(params.scenario)
        retcode = self.push_traffic(
            net, logs_dir, params.iterations)

        # CLI ( net )
        self.logger.info("Stopping network..")
        net.stop()
        self.clear_test(retcode, logs_dir)

        return retcode

    def clear_test(self, test_status, logs_dir):
        s = os.stat('.')
        util.rchmod(logs_dir, s.st_uid, s.st_gid)
        if test_status == 2:
            self.logger.info("END Test finished with WARNINGS")
        elif test_status == 1:
            self.logger.info("ERROR CRITICAL server went down during test")
        else:
            self.logger.info("END Test finished successfully")
            # clear flows array
            del _flows[:]

    def push_traffic(self, net, logs_dir, iterations):
        """ Push traffic into generated test network\n
        Generates traffic between hosts in network.\n
        :param net:
        :param tool:
        :param logs_dir:
        :param iterations:
        """
        test_tool = TestToolIperf(net, logs_dir)
        info("Using IPERF as traffic generator\n")

        # Run servers
        info("Starting servers..\n")
        test_tool.run_servers(_flows)
        info("Waiting for servers to start..\n")
        # wait for server to start
        time.sleep(INITIALIZATION_DELAY)
        # start all test's iterations
        if iterations > 1:
            start_time = time.time()
        i = 0
        retcode = None
        self.logger.info("Starting test..")
        while i != iterations:
            self.logger.info("Iteration: {} / {}".format(i + 1, iterations))
            iteration_start_time = time.time()
            # Run traffic from host with parameters defined in flows
            for f in _flows:
                test_tool.run_client(f)

            self.logger.info("Waiting for iteration {} end..".format(i + 1))
            retcode = test_tool.wait_for_end()

            end_time = time.time()
            iter_time = end_time - iteration_start_time
            self.logger.info("Iteration time: {:0.2f} s".format(iter_time))
            i += 1
        if iterations > 1:
            total_time = end_time - start_time
        else:
            total_time = iter_time

        self.logger.info("Total testing time: {:0.2f} s".format(total_time))

        self.logger.info("Killing all test tool processes.")
        test_tool.kill_all()

        return retcode

    def cleanup_mn_env(self):
        self.logger.info("Cleaning up Mininet environment..")
        # kill all mn_generator related processes
        cleanup()
        os.system('pkill -9 iperf')
        del _flows[:]


if __name__ == '__main__':
    setLogLevel('info')
#     setLogLevel('debug')
    parser = argparse.ArgumentParser(
        description="Launches D-ITG test scenario in mininet.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-s", "--scenario",
                        help="Input name of scenario defined in .xml file")

    parser.add_argument("-t", "--tool",
                        help="tool")

    args = parser.parse_args()

    iterations = 2

    params = RunTestParams(args.scenario, args.tool, iterations)
    launcher = TestLauncher()
    launcher.run(params)
