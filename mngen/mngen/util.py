#!/usr/bin/env python
# coding=utf-8
"""@package util

Utilities for MN Scenario Generator
@author Tomasz Osiński (osinstom@gmail.com), Paweł Borawski ()

"""
import datetime
import os
import logging

from mngen.models import *
from config import TOPOLOGIES_DIR, SCENARIOS_DIR, LOGS_DIR

logger = logging.getLogger('mngen_api')

def get_host_id(filename):
    hostname = filename.split('.')[0]
    host_id = hostname.replace('h', '')
    return '10.0.0.{}'.format(host_id)


def get_scenarios():
    scenarios = []
    for i, f in enumerate(os.listdir(SCENARIOS_DIR)):
        ext = os.path.splitext(f)[-1].lower()
        if ext == ".xml":
            s = dict()
            s['id'] = i+1
            s['name'] = f.replace(".xml", "")
            scenarios.append(s)

    return scenarios


def get_scenario_details(scenario_id):
    scenarios = get_scenarios()

    for s in scenarios:
        if str(s['id']) == scenario_id:
            s_filename = s['name'] + ".xml"

    if s_filename is not None:
        with open(os.path.join(SCENARIOS_DIR, s_filename), 'r') as f:
            scenario = f.read()

    return scenario


def get_topologies():
    topologies = []

    for i, f in enumerate(os.listdir(TOPOLOGIES_DIR)):
        ext = os.path.splitext(f)[-1].lower()
        if ext == ".jpg":
            topo = dict()
            topo['id'] = i+1
            topo['name'] = f.replace(".jpg", "")
            topo['url'] = TOPOLOGIES_DIR + f
            topologies.append(topo)

    return topologies


def get_host_by_id(hosts, id):
    for h in hosts:
        if h.id == id:
            return h

    return None


def get_switch_id_by_name(switches, name):
    for s in switches:
        if s.name == name:
            return s.id

    return None


def get_host_id_by_name(hosts, name):
    for h in hosts:
        if h.name == name:
            return h.id

    return None


def validate_params(traffic_type):
    if traffic_type == TrafficType.RANDOM:
        return
    if not (TRAFFIC_TYPES.__contains__(traffic_type.lower())):
        logger.info("Wrong traffic parameters!")
        logger.info("Available TRAFFIC TYPES: {}".format(TRAFFIC_TYPES))
        raise ValueError


def prepare_logs_dir(test_name):
    '''
    Clean (if needed) or create new logs directory. Create logs_dir name based on test_name and datetime.
    :param test_name: 
    :return: 
    '''

    timestamp = datetime.datetime.now().strftime ("%Y-%m-%d-%H:%M")
    logs_dir = os.path.join(os.getcwd(), LOGS_DIR + test_name + '_' + timestamp)


    # TODO: perhaps it isn't necessary now, with timestamp included in dir name
    if not os.path.exists(logs_dir):
        logger.info("Creating new dir: {}".format(logs_dir))
        os.mkdir(logs_dir, 0o775)
        os.chmod(logs_dir, 0o775)
    else:
        clean_dir(logs_dir)

    return logs_dir


def clean_dir(directory):
    logger.info("Clearing {}...".format(directory))
    for f in os.listdir(directory):
        path = os.path.join(directory, f)
        os.remove(path)


def rchmod(path, uid, guid):
    os.chown(path, uid, guid)
    for root, dirs, files in os.walk(path):
        for momo in dirs:
            os.chown(momo, uid, guid)
        for file in files:
            fname = os.path.join(root, file)
            os.chown(fname, uid, guid)
