# coding=utf-8
#!/usr/bin/env python

"""@package models

Topology-related models
@author Tomasz Osiński (osinstom@gmail.com), Paweł Borawski ()
"""


class Controller:
    def __init__(self, ip_addr, port):
        self.ip_addr = ip_addr
        self.port = port


class Node(object):
    name = None
    id = None


class Host(Node):
    def __init__(self, name, id):
        self.name = name
        self.id = id


class Switch(Node):
    dpid = None

    def __init__(self, name, dpid, id):
        self.name = name
        self.dpid = dpid
        self.id = id


class Link:
    def __init__(self, src, dst, latency, bandwidth, in_network):
        self.src = src
        self.dst = dst
        self.latency = latency
        self.bandwidth = bandwidth
        self.in_network = in_network

    def __str__(self):
        return "{src=" + str(self.src) + ", dst=" + str(self.dst) + "}"


class Topology:

    hosts = []
    switches = []
    links = []
    controller = None

    def __init__(self, switches, hosts, links, controller):
        self.switches = switches
        self.hosts = hosts
        self.links = links
        self.controller = controller

    def __str__(self):
        return "Hosts = " + str(self.hosts) + " Switches = " + \
            str(self.switches) + " Links = " + str(self.links)


class HostMovement:
    def __init__(self, src, dst, timestamp):
        self.src = src
        self.dst = dst
        self.timestamp = timestamp

# traffic related models


class Flow:
    def __init__(self, src, dst, delay, bitrate, l4type, duration):
        self.src = src
        self.dst = dst
        self.delay = delay
        self.bitrate = bitrate
        self.l4type = l4type
        self.duration = duration


class Traffic:
    flows = []

    def __init__(self, flows):
        self.flows = flows


class Scenario:
    topology = None
    traffic = None

    def __init__(self, topology, traffic):
        self.topology = topology
        self.traffic = traffic


class TrafficTool:
    IPERF = 1
    DITG = 2


class HostDistribution:
    UNIFORM = 0
    RANDOM = 1


class TrafficType:
    TCP = "tcp"
    UDP = "udp"
    RANDOM = "random"


TRAFFIC_TYPES = [TrafficType.TCP, TrafficType.UDP]


class TrafficParams:
    def __init__(self, model):
        self.min_flows = model['min_flows']
        self.max_flows = model['max_flows']
        self.c_min = model['min_bitrate']
        self.c_max = model['max_bitrate']
        self.l4type = model['traffic_type'].lower()
        self.max_delay = model['max_delay']
        self.max_duration = model['max_duration']


class ScenarioParams:
    def __init__(self, model, traffic_params):
        self.test_name = model['test_name']  # test name passed by user
        self.topology = model['topology']  # topology name from topology-zoo
        self.hosts_num = model['hosts_num']  # int, number of hosts per switch
        self.host_distrbution = model['hosts_distribution']   #  int, 1 - uniform, 2 - random
        self.link_bw = model['link_bandwidth']
        self.traffic_params = traffic_params  # TrafficParams object


class RunTestParams:

    controller_ip = None
    controller_port = None

    def __init__(self, model):
        self.scenario = model['scenario']
        self.iterations = model['iterations']
        if 'controller_ip' in model and 'controller_port' in model:
            self.controller_ip = model['controller_ip']
            self.controller_port = model['controller_port']
        self.tool = TrafficTool.IPERF
