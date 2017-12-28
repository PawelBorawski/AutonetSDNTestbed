#!/usr/bin/env python

import os

config = {
    'host': '0.0.0.0',
    'port': 8181,
    'debug': True,
}

TOPOLOGIES_DIR = "data/topologies/zoo-dataset/"
SCENARIOS_DIR = "data/scenarios/"
LOGS_DIR = "data/logs/"

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
