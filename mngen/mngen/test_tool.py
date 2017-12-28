#!/usr/bin/env python
# coding=utf-8
"""@package test_tool

Testing tools implementation
@author Tomasz Osiński (osinstom@gmail.com), Paweł Borawski ()
"""

import Queue
import abc
import os
import threading
import time
import logging
from subprocess import call

import util


class TestTool:
    def __init__(self, net, log_dir):
        self.logger = logging.getLogger('mngen_api')
        self.net = net
        self.log_dir = log_dir
        self.q = Queue.Queue()
        self.server_threads = list()
        self.client_threads = list()

    @abc.abstractmethod
    def run_server(self, host_name):
        pass

    @abc.abstractmethod
    def run_servers(self, flows):
        pass

    @abc.abstractmethod
    def run_client(self, flows):
        pass

    @abc.abstractmethod
    def is_server(self, cmd):
        pass

    @abc.abstractmethod
    def kill_all(self,):
        pass

    def run_cmd(self, src_name, dst_name, cmd, type, flow_id='', delay=0):
        t = threading.Thread(
            target=self.run_cmd_thread,
            args=(
                src_name,
                dst_name,
                cmd,
                type,
                delay,
                flow_id))
        if type == "server":
            self.server_threads.append(t)
        elif type == "client":
            self.client_threads.append(t)
        else:
            self.logger.info("Wrong client name")
            return
        t.start()

    def run_cmd_thread(
            self,
            src_name,
            dst_name,
            cmd_str,
            proc_type,
            delay,
            flow_id):
        """ Run command in host. Execute process in host's network namespace.\n
        Uses 'mnexec' provided by mininet.\n
        :param src_name:
        :param dst_name:
        :param cmd_str:
        :param proc_type:
        :param log_dir: """
        host = self.net.getNodeByName(src_name)
        if delay:
            time.sleep(float(delay))
        self.logger.info("{} pid({}): {}".format(src_name, host.pid, cmd_str))
        cmd = 'mnexec -da {pid} {cmd}'.format(pid=host.pid, cmd=cmd_str)
        if self.log_dir is None:
            log_dir = './'
        else:
            log_dir = self.log_dir
        ret = call(cmd.split(), stderr=open(os.path.join(log_dir, src_name +
                                                         '.' +
                                                         proc_type +
                                                         ('.' +
                                                          dst_name if not dst_name == "" else '') +
                                                         ('.' +
                                                          flow_id if not flow_id == "" else '') +
                                                         '.stderr'), mode='w+'), stdout=open(os.path.join(log_dir, src_name +
                                                                                                          '.' +
                                                                                                          proc_type +
                                                                                                          ('.' +
                                                                                                           dst_name if not dst_name == "" else '') +
                                                                                                          ('.' +
                                                                                                              flow_id if not flow_id == "" else '') +
                                                                                                          '.stdout'), mode='w+'))
        self.q.put((cmd, ret, src_name))

    def wait_for_end(self):
        while [True for t in self.client_threads if t.is_alive()]:
            ret = self.q.get()
            self.logger.info(
                "Return from {} on {}: {}".format(
                    ret[0], ret[2], ret[1]))
            cmd = ret[0]

            if self.is_server(cmd):
                self.logger.info("ERROR CRITICAL {} server is down".format(ret[2]))
                self.kill_all()
                return 1
            elif ret[1] != 0:
                self.logger.info("WARNING client on {} exited with {}".format(ret[2], ret[1]))
        return 0

    def get_queue(self):
        return self.q

#########################################################
# D-ITG is currently not used in beta version

# class TestToolITG(TestTool):
#     def run_server(self, host_name):
#         if self.log_dir:
#             cmd = 'ITGRecv -l '+os.path.join(self.log_dir, util.get_logname(host_name, False))
#         else:
#             cmd = 'ITGRecv'
#         print "{} {}".format(host_name, cmd)
#         self.run_cmd(host_name, "", cmd, 'server')
#
#     def run_client(self, script):
#         src = script.split("/")[7].replace(".itg", "")
#         cmd = 'ITGSend {}'.format(script)
#         if self.log_dir:
#             cmd += ' -l {logfile}'.format(logfile=os.path.join(self.log_dir, util.get_logname(src, True)))
#         self.run_cmd(src, "", cmd, 'client', 0)
#
#     def is_server(self, cmd):
#         if "ITGRecv" in cmd:
#             return True
#         elif "ITGSend" in cmd:
#             return False
#         else:
#             raise ValueError("It is not valid ITG command: "+cmd)
#
#     def kill_all(self):
#         os.system('pkill ITGRecv')
#         os.system('pkill ITGSend')
#
#     def prepare_scripts(self, flows):
#         dir = os.path.join(os.getcwd(), "temp/")
#         util.clean_dir(dir)
#         scripts = dict()
#         for f in flows:
#             line = "-a {} -T {} -C {} -t {} -d {}".format(self.net.getNodeByName(str(f.dst)).IP(), f.l4type.upper(), int(float(f.bitrate) * 1000000), int(f.duration) * 1000, int(float(f.delay) * 1000))
#             if f.src in scripts:
#                 scripts[f.src] += "{}\n".format(line)
#             else:
#                 scripts[f.src] = "{}\n".format(line)
#         files = []
#         for h in sorted(scripts):
#             with open(dir + (str(h) + ".itg"), "w") as script:
#                 script.write(scripts[h])
#                 files.append(script.name)
#
#         return files


class TestToolIperf(TestTool):
    def run_server(self, host_name):
        self.run_cmd(host_name, "tcp", "iperf -s -i 1", 'server')
        self.run_cmd(host_name, "udp", "iperf -u -s -p 5555 -i 1", 'server')

    def run_servers(self, flows):
        udp_servers = []
        tcp_servers = []
        for f in flows:
            if f.l4type.lower() == "udp":
                if f.dst not in udp_servers:
                    self.run_cmd(
                        f.dst,
                        f.src + '.udp',
                        "iperf -u -s -p 5555 -i 1",
                        'server')
                    udp_servers.append(f.dst)
            else:
                if f.dst not in tcp_servers:
                    self.run_cmd(
                        f.dst,
                        f.src + '.tcp',
                        "iperf -s -i 1",
                        'server')
                    tcp_servers.append(f.dst)
                self.logger.info("Running server on {}..".format(f.dst))

    def run_client(self, f):
        src_host = self.net.getNodeByName(str(f.src))
        dst_host = self.net.getNodeByName(str(f.dst))
        self.logger.info("DEBUG: {} : Flow: {} --> {} ,type: {}, rate: {}, duration: {}, delay: {}".format(src_host.name,
                                                                                                           src_host.IP(),
                                                                                                           dst_host.IP(),
                                                                                                           f.l4type,
                                                                                                           f.bitrate,
                                                                                                           f.duration,
                                                                                                           f.delay))
        cmd = 'iperf -c {} -t {} -i {}'.format(dst_host.IP(), f.duration, 1)
        # -y C in order to dump results into CSV format
        if f.l4type.lower() == "udp":
            rate = int(float(f.bitrate) * 1000000)
            cmd += ' -b {}'.format(rate)
            # if UDP, send data to port 5555 to avoid conflict with TCP
            cmd += ' -p 5555'
            self.logger.info("UDP bandwidth: {} bit/s".format(rate))

        self.logger.info("Thread delay: {} s".format(f.delay))
        # generate unique flow id to differentiate between flows
        rate = int(float(f.bitrate) * 1000000)
        id = rate + int(f.duration) + float(f.delay)
        flow_id = f.l4type + '.' + str(int(round(id, 2) * 100))
        self.run_cmd(
            src_host.name,
            dst_host.name,
            cmd,
            'client',
            flow_id,
            f.delay)

    def is_server(self, cmd):
        if 'iperf' not in cmd:
            raise ValueError("It is not valid iperf command: " + cmd)
        if '-s' in cmd:
            return True
        else:
            return False

    def kill_all(self):
        os.system('pkill -9 iperf')
