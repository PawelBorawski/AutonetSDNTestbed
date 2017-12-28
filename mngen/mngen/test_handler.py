import os

import util
import logging
from config import LOGS_DIR, SCENARIOS_DIR
import shutil
from lxml import etree
from lxml.etree import XMLSyntaxError

from mngen.exceptions import XMLValidationError


class TestModifier():

    def __init__(self):
        self.logger = logging.getLogger('mngen_api')
        self.xml_xsd_path = 'data/schemas/scenario.xsd'
        self.xml_schema_doc = etree.parse(self.xml_xsd_path)

    def modify_scenario(self, name, scenario_xml):
        try:
            self.validate_xml(scenario_xml)
        except (XMLSyntaxError, ValueError):
            raise XMLValidationError
        else:
            self.write_xml_to_file(name, scenario_xml)
            self.logger.info("Scenario {} has been modified".format(name))

    def delete_scenario(self, name):
        try:
            os.remove(SCENARIOS_DIR + name + ".xml")
        except:
            raise
        else:
            self.logger.info("Scenario {} has been removed".format(name))

    def validate_xml(self, xml):
        xml_schema = etree.XMLSchema(self.xml_schema_doc)
        xml_doc = etree.fromstring(xml)
        result = xml_schema.validate(xml_doc)
        if result is False:
            raise ValueError

    def write_xml_to_file(self, name, xml):
        outputfile = open(SCENARIOS_DIR + name + ".xml", 'w')
        outputfile.write(xml)
        outputfile.close()


class ResultsProvider():

    def __init__(self):
        self.logger = logging.getLogger('mngen_api')

    def delete_result(self, result_name):
        try:
            shutil.rmtree(LOGS_DIR + result_name)
        except:
            raise
        else:
            self.logger.info("Result {} has been removed".format(result_name))

    def get_test_result_list(self):
        results_list = list()
        for index, dir in enumerate(os.listdir(LOGS_DIR)):
            result = dict()
            result['id'] = index+1
            result['name'] = dir
            results_list.append(result)
        return results_list

    def get_results(self, result_name):
        results = list()

        result_dir = LOGS_DIR + result_name
        if not os.path.exists(result_dir):
            return results
        for index, file_name in enumerate(os.listdir(result_dir)):
            if file_name.endswith(".stdout") and 'client' in file_name:
                with open(os.path.join(result_dir, file_name), 'r') as f:
                    data = f.read()

                if data:
                    result = dict()
                    result['id'] = index+1
                    result['name'] = self.describe_result(file_name)
                    result['client'] = data
                    result['server'] = self.get_server_result_for_client(
                        result_dir, file_name)
                    results.append(result)

        return results

    def get_server_result_for_client(self, result_dir, client_file_name):
        data = ''
        for f in os.listdir(result_dir):
            if f.endswith(".stdout") and 'server' in f and client_file_name.split(
                    ".")[2] == f.split('.')[0] and client_file_name.split(".")[3] in f:

                with open(os.path.join(result_dir, f), 'r') as f:
                    data = f.read()
        host_id = util.get_host_id(client_file_name)

        return self.prepare_server_result(host_id, data)

    def prepare_server_result(self, host_id, server_result):
        tmp = server_result.split('\n')

        line_id = ''
        for line in tmp:
            if host_id in line:
                line_id = line.split(' ')[1]
        print line_id
        for line in tmp:
            if line_id in line is not None and 'sec' in line or 'connected' in line:
                tmp[tmp.index(line)] = ''

        tmp = filter(None, tmp)
        server_result = '\n'.join(tmp)

        return server_result

    def describe_result(self, file_name):
        return '{} Flow from client {} to server {}'.format(file_name.split(
            ".")[3].upper(), file_name.split(".")[0], file_name.split(".")[2])
