#!/usr/bin/env python
# coding=utf-8
import math
import os
import random
import re
import sys
from lxml import etree as ET
import logging

import util
from mngen.models import *
from config import TOPOLOGIES_DIR, SCENARIOS_DIR


class TestCreator():

    def __init__(self, **opts):
        self.logger = logging.getLogger('mngen_api')
        self.logger.info("TestCreator started..")

    def get_zoo_topologies(self):
        """
        Return list of available topologies from topology-zoo.
        :return: List of available topologies.
        """

        topos = []
        for f in os.listdir(TOPOLOGIES_DIR):
            topo_path = os.path.join(TOPOLOGIES_DIR, f)
            ext = os.path.splitext(f)[-1].lower()
            if ext == ".graphml":
                topos.append(f.replace(".graphml", "").lower())

        return topos

    def position_encode(self, dec):
        """
        Encode position to hex string.
        :param dec:
        :return: Position in hexadecimal string.
        """

        if(dec >= 0):
            dec_hex = hex(int(dec * 1e5))[2:]
            while(len(dec_hex) < 8):
                dec_hex = "0" + dec_hex
        else:
            dec_hex = hex(int(dec * 1e5))[3:]
            while(len(dec_hex) < 7):
                dec_hex = "0" + dec_hex
            dec_hex = "1" + dec_hex
        return dec_hex

    def gen_rand_dist_hosts(self, no_switches, number_of_hosts):
        """
        Generate randomly distributed hosts.
        :param no_switches:
        :param number_of_hosts:
        :return:
        """

        switches_hosts = []
        for i in range(0, no_switches):
            switches_hosts.append(random.randint(0, number_of_hosts))

        self.logger.debug("Number of hosts " + str(number_of_hosts))
        self.logger.debug("Switches_hosts: {}".format(switches_hosts))

        return switches_hosts

    def generate_test(
            self,
            test_name,
            topology,
            link_bw,
            host_num,
            distr,
            traffic):
        """
        Method generates test scenario based on input parameters.
        :param test_name: Name of generated test scenario.
        :param topology: Name of topology from topology-zoo catalog.
        :param link_bw: Bandwidth of network link.
        :param host_num: Number of hosts per switch in topology.
        :param distr: Type of host distrubution in network (uniform/random).
        :param traffic: Traffic parameters.
        :return:
        """

        self.logger.info("Generating test '{}' with topology '{}'".format(test_name, topology))

        if not topology.lower() in self.get_zoo_topologies():
            raise ValueError

        created_topology = self.create_topology(
            topology.lower(), host_num, distr, link_bw)
        self.logger.info("Topology {} created..".format(topology))


        flows = self.create_flows(
            created_topology.hosts,
            traffic.min_flows,
            traffic.max_flows,
            traffic.max_delay,
            traffic.c_min,
            traffic.c_max,
            traffic.l4type,
            traffic.max_duration)

        scenario_xml = self.parse_scenario_to_xml(created_topology, flows)

        outputfile = open(SCENARIOS_DIR + test_name + ".xml", 'w')
        outputfile.write(scenario_xml)
        outputfile.close()

        self.logger.info("Scenario created!")

    def create_topology(self, topo_name, host_num, hosts_distr, link_bw):
        """
         Method converts topology from .graphml format into Python object.
         :param topo_name: Name of topology from topology-zoo catalog.
         :param host_num: Number of hosts per switch in topology.
         :param hosts_distr: Type of host distrubution in network (uniform/random).
         :param link_bw: Bandwidth of network link.
         :return: Topology
        """

        input_file_name = TOPOLOGIES_DIR + topo_name.title() + ".graphml"

        if input_file_name == '':
            sys.exit('\n\tNo input file was specified as argument....!')

        # READ FILE AND DO ALL THE ACTUAL PARSING IN THE NEXT PARTS
        xml_tree = ET.parse(input_file_name)
        namespace = "{http://graphml.graphdrawing.org/xmlns}"
        ns = namespace  # just doing shortcutting, namespace is needed often.

        # GET ALL ELEMENTS THAT ARE PARENTS OF ELEMENTS NEEDED LATER ON
        root_element = xml_tree.getroot()
        graph_element = root_element.find(ns + 'graph')

        # GET ALL ELEMENT SETS NEEDED LATER ON
        index_values_set = root_element.findall(ns + 'key')
        node_set = graph_element.findall(ns + 'node')
        edge_set = graph_element.findall(ns + 'edge')

        # SET SOME VARIABLES TO SAVE FOUND DATA FIRST
        # memomorize the values' ids to search for in current topology
        node_label_name_in_graphml = ''
        node_latitude_name_in_graphml = ''
        node_longitude_name_in_graphml = ''
        # for saving the current values
        node_index_value = ''
        node_name_value = ''
        node_longitude_value = ''
        node_latitude_value = ''
        # id:value dictionaries
        id_node_name_dict = {}     # to hold all 'id: node_name_value' pairs
        id_longitude_dict = {}     # to hold all 'id: node_longitude_value' pairs
        id_latitude_dict = {}     # to hold all 'id: node_latitude_value' pairs

        # list of created links, switches and hosts
        switches = []
        hosts = []
        links = []

        # FIND OUT WHAT KEYS ARE TO BE USED, SINCE THIS DIFFERS IN DIFFERENT
        # GRAPHML TOPOLOGIES
        for i in index_values_set:

            if i.attrib['attr.name'] == 'label' and i.attrib['for'] == 'node':
                node_label_name_in_graphml = i.attrib['id']
            if i.attrib['attr.name'] == 'Longitude':
                node_longitude_name_in_graphml = i.attrib['id']
            if i.attrib['attr.name'] == 'Latitude':
                node_latitude_name_in_graphml = i.attrib['id']

        # NOW PARSE ELEMENT SETS TO GET THE DATA FOR THE TOPO
        # GET NODE_NAME DATA
        # GET LONGITUDE DATK
        # GET LATITUDE DATA
        for n in node_set:

            node_index_value = n.attrib['id']

            # get all data elements residing under all node elements
            data_set = n.findall(ns + 'data')

            # finally get all needed values
            for d in data_set:

                # node name
                if d.attrib['key'] == node_label_name_in_graphml:
                    # strip all whitespace from names so they can be used as
                    # id's
                    node_name_value = re.sub(r'\s+', '', d.text)
                    node_name_value = node_name_value.replace(",", "")
                # longitude data
                if d.attrib['key'] == node_longitude_name_in_graphml:
                    node_longitude_value = d.text
                # latitude data
                if d.attrib['key'] == node_latitude_name_in_graphml:
                    node_latitude_value = d.text

                # save id:data couple
                id_node_name_dict[node_index_value] = node_name_value
                id_longitude_dict[node_index_value] = node_longitude_value
                id_latitude_dict[node_index_value] = node_latitude_value

        if hosts_distr == HostDistribution.RANDOM:
            hosts_in_switch = self.gen_rand_dist_hosts(
                len(id_node_name_dict), int(host_num))

        host_count = 1

        for i in range(0, len(id_node_name_dict)):

            # ######################## Create position string #################
            # Currently, position encoding is not used
            # position_string = self.position_encode(float(id_latitude_dict[str(i)])) + self.position_encode(float(id_longitude_dict[str(i)]))
            # ######################## Add switch to list #####################
            switch = Switch(id_node_name_dict[str(i)], dpid=None, id=i + 1)
            switches.append(switch)

            if hosts_distr == HostDistribution.UNIFORM:
                for h in range(0, int(host_num)):
                    name = id_node_name_dict[str(i)] + str(h + 1)
                    id = host_count
                    host = Host(name, id)
                    hosts.append(host)
                    host_count += 1

                # link each switch and its host...
                for h in range(0, int(host_num)):

                    link = Link(util.get_switch_id_by_name(switches,
                                                           id_node_name_dict[str(i)]),
                                util.get_host_id_by_name(hosts,
                                                         id_node_name_dict[str(i)] + str(h + 1)),
                                0,
                                0,
                                False)
                    links.append(link)

            elif hosts_distr == HostDistribution.RANDOM:
                for h in range(0, hosts_in_switch[i]):
                    name = id_node_name_dict[str(i)] + str(h + 1)
                    id = host_count
                    host = Host(name, id)
                    hosts.append(host)
                    host_count += 1

                for h in range(0, hosts_in_switch[i]):
                    link = Link(util.get_switch_id_by_name(switches,
                                                           id_node_name_dict[str(i)]),
                                util.get_host_id_by_name(hosts,
                                                         id_node_name_dict[str(i)] + str(h + 1)),
                                0,
                                0,
                                False)
                    links.append(link)

        distance = 0.0
        latency = 0.0

        for e in edge_set:

            # GET IDS FOR EASIER HANDLING
            src_id = e.attrib['source']
            dst_id = e.attrib['target']

            # CALCULATE DELAYS

            #    CALCULATION EXPLANATION
            #
            #    formula: (for distance)
            #    dist(SP,EP) = arccos{ sin(La[EP]) * sin(La[SP]) + cos(La[EP]) * cos(La[SP]) * cos(Lo[EP] - Lo[SP])} * r
            #    r = 6378.137 km
            #
            #    formula: (speed of light, not within a vacuumed box)
            #     v = 1.97 * 10**8 m/s
            #
            #    formula: (latency being calculated from distance and light speed)
            #    t = distance / speed of light
            # t (in ms) = ( distance in km * 1000 (for meters) ) / ( speed of
            # light / 1000 (for ms))

            #    ACTUAL CALCULATION: implementing this was no fun.

            first_product = math.sin(
                float(id_latitude_dict[dst_id])) * math.sin(float(id_latitude_dict[src_id]))
            second_product_first_part = math.cos(
                float(id_latitude_dict[dst_id])) * math.cos(float(id_latitude_dict[src_id]))
            second_product_second_part = math.cos(
                (float(id_longitude_dict[dst_id])) - (float(id_longitude_dict[src_id])))

            distance = math.radians(math.acos(
                first_product + (second_product_first_part * second_product_second_part))) * 6378.137

            # t (in ms) = ( distance in km * 1000 (for meters) ) / ( speed of light / 1000 (for ms))
            # t         = ( distance       * 1000              ) / ( 1.97 * 10**8   / 1000         )
            latency = (distance * 1000) / (197000)

            # BANDWIDTH LIMITING
            # set bw to 10mbit if nothing was specified otherwise on startup
            if link_bw is None:
                link_bw = '10'

            link = Link(
                util.get_switch_id_by_name(
                    switches,
                    id_node_name_dict[src_id]),
                util.get_switch_id_by_name(
                    switches,
                    id_node_name_dict[dst_id]),
                latency,
                link_bw,
                True)
            links.append(link)

        controller = Controller("127.0.0.1", 6633)

        topology = Topology(switches, hosts, links, controller)

        return topology

    def parse_scenario_to_xml(self, topology, flows):
        """
        Method creates topology XML file .
        :param topology: Topology object that describes network topology.
        :param flows: List of flows in a network.
        :return: Topology in format of XML.
        """

        n_scenario = ET.Element("scenario")
        n_topology = ET.SubElement(n_scenario, "topology")

        n_switches = ET.SubElement(n_topology, "switches")
        for sw in topology.switches:
            switch = ET.SubElement(n_switches, "switch")
            switch.set("id", "s" + str(sw.id))
            switch.set("name", sw.name)
            if sw.dpid is not None:
                switch.set("dpid", sw.dpid)

        n_hosts = ET.SubElement(n_topology, "hosts")
        for h in topology.hosts:
            host = ET.SubElement(n_hosts, "host")
            host.set("id", "h" + str(h.id))
            host.set("name", h.name)

        n_links = ET.SubElement(n_topology, "links")
        for l in topology.links:
            link = ET.SubElement(n_links, "link")
            type = ""
            if l.in_network:
                type = "network"
                link.set("src", "s" + str(l.src))
                link.set("dst", "s" + str(l.dst))
            else:
                type = "host"
                link.set("src", "s" + str(l.src))
                link.set("dst", "h" + str(l.dst))

            link.set("latency", str(l.latency))
            link.set("bw", str(l.bandwidth))
            link.set("type", type)

        n_traffic = ET.SubElement(n_scenario, "traffic")
        n_flows = ET.SubElement(n_traffic, "flows")
        for f in flows:
            flow = ET.SubElement(n_flows, "flow")
            flow.set("src", "h" + str(f.src.id))
            flow.set("dst", "h" + str(f.dst.id))
            flow.set("c_rate", str(f.bitrate))
            flow.set("delay", str(f.delay))
            flow.set("l4type", f.l4type)
            flow.set("duration", str(f.duration))

        xml_str = ET.tostring(n_scenario, pretty_print=True)

        return xml_str

    def create_flows(
            self,
            hosts,
            min_flows,
            max_flows,
            max_delay,
            c_min,
            c_max,
            l4type,
            max_duration):
        """
        Method creates list of flows in a network.
        :param hosts: List of hosts in a network.
        :param min_flows: Minumum number of flows.
        :param max_flows: Maximum number of flows.
        :param max_delay: Maximum delay of particular flow.
        :param c_min: Minimum bitrate of particular flow.
        :param c_max: Maxiumum bitrate of particular flow.
        :param l4type: L4 type of traffic (TCP, UDP or random)
        :param max_duration: Maximum duration of particular flow.
        :return: List of generated flows.
        """

        self.logger.info("Creating flows..")
        flows = []

        for h in hosts:
            id = h.id
            h_flows = []
            num_flows = random.randint(int(min_flows), int(max_flows))

            while len(h_flows) < int(num_flows):
                rand_id = random.randint(1, hosts[len(hosts) - 1].id)
                if(id != rand_id):
                    src = util.get_host_by_id(hosts, id)
                    dst = util.get_host_by_id(hosts, rand_id)
                    delay = random.uniform(0, max_delay)  # in seconds
                    bitrate = random.uniform(
                        int(c_min), int(c_max))  # in kbit/s
                    traffic_type = ""
                    if l4type == TrafficType.RANDOM:
                        # choose between 1 = tcp , 2 = udp
                        traffic_type = random.choice(TRAFFIC_TYPES)
                    else:
                        traffic_type = l4type.lower()
                    duration = random.randint(1, max_duration)  # in seconds
                    flow = Flow(
                        src,
                        dst,
                        delay,
                        bitrate,
                        traffic_type,
                        duration)
                    h_flows.append(flow)

            flows = flows + h_flows

        return flows
