import os
import json
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from flask_jsonschema import JsonSchema, ValidationError, validate
import logging

from config import config
from mngen import util
from mngen.models import RunTestParams, TrafficParams, HostDistribution
from mngen.test_creator import TestCreator
from mngen.test_handler import TestModifier, ResultsProvider
from mngen.test_launcher import TestLauncher
from mngen.exceptions import XMLValidationError, MininetIsBusyError

app = Flask(__name__)
CORS(app)
app.config['JSONSCHEMA_DIR'] = os.path.join(app.root_path, 'data/schemas')
jsonschema = JsonSchema(app)

LOG_FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger('mngen_api')

creator = TestCreator()
launcher = TestLauncher()
modifier = TestModifier()
results_provider = ResultsProvider()

@app.errorhandler(ValidationError)
def on_validation_error(e):
    print e
    return jsonify({'message': "Bad arguments. Validation error."}), 404

@app.route("/create", methods=["POST"])
@validate('api_schema', 'create')
def create_scenario():
    data = request.json['scenario']
    status_ok = {'message': "Scenario created successfully"}
    status_error = {'message': "Scenario creator failed"}
    status_test_exists = {'message': "Scenario with this name already exists"}
    status_bad_arguments = {
        'message': "Wrong parameters (check topology name)"}

    scenarios = [x['name'] for x in util.get_scenarios()]
    logger.debug(scenarios)

    if data['name'] in scenarios:
        return jsonify(status_test_exists), 400

    logger.debug(data)
    traffic = TrafficParams(data)

    if data['hosts_distribution'] == "RANDOM":
        hosts_distr = HostDistribution.RANDOM
    else:
        hosts_distr = HostDistribution.UNIFORM

    try:
        creator.generate_test(
            data['name'], data['topology'], int(
                data['link_bandwidth']), int(
                data['hosts_num']), hosts_distr, traffic)
    except ValueError:
        return jsonify(status_bad_arguments), 400
    except Exception as e:
        print str(e)
        return jsonify(status_error), 500
    else:
        return jsonify(status_ok), 200


@app.route("/run", methods=["POST"])
@validate('api_schema', 'run')
def run_test():

    params = RunTestParams(request.json)

    try:
        launcher.run(params)
    except MininetIsBusyError as e:
        return jsonify({'message': e.message}), 486
    except Exception as e:
        print str(e)
        launcher.stop()
        return jsonify({'message': 'Something went wrong.'}), 500
    else:
        return jsonify({'message': 'Test has been started.'}), 200


@app.route("/status", methods=["GET"])
def status():
    if launcher.is_autonet_alive():
        return Response(status=486)
    else:
        logger.info("No test is running now..")
        return Response(status=200)


@app.route("/stop", methods=["POST"])
def stop():
    try:
        launcher.stop()
    except Exception:
        return jsonify({'message': 'Stopping test failed.'}), 500

    return jsonify({'message' : 'Test has been stopped'}), 200


@app.route("/modify", methods=["POST"])
@validate('api_schema', 'modify')
def modify():
    data = request.json
    try:
        modifier.modify_scenario(data['name'], data['scenario'])
    except XMLValidationError as e:
        return jsonify({'message' : e.message}), 500
    except:
        return jsonify({'message' : 'Modify scenario did not succeed'}), 500
    else:
        return jsonify({'message' : 'Scenario modified'}), 200


@app.route("/delete", methods=["POST"])
@validate('api_schema', 'default')
def delete_scenario():
    # try:
    #     modifier.delete_scenario(request.json["name"])
    # except:
    #     return jsonify({'message': 'Delete scenario did not succeed'}), 500
    # else:
    modifier.delete_scenario(request.json["name"])
    return jsonify({'message': 'Scenario has been deleted'}), 200


@app.route("/topologies", methods=["GET"])
def get_topologies():
    data = util.get_topologies()

    return json.dumps(data, ensure_ascii=False)


@app.route("/scenarios", methods=["GET"])
def get_scenarios():
    data = util.get_scenarios()

    return json.dumps(data)


@app.route("/scenario_details", methods=["GET"])
def get_scenario_details():

    resp = Response(status=200)
    scenario_id = request.args.get('id')
    if scenario_id is None:
        resp.status_code = 400
        return resp

    scenario = util.get_scenario_details(scenario_id)
    data = {"id": scenario_id, "content": scenario}

    resp.set_data(json.dumps(data))
    return resp

@app.route("/list_results", methods=["GET"])
def get_results_list():
    results_list = results_provider.get_test_result_list()
    data = json.dumps(results_list)
    resp = Response(status=200)
    resp.set_data(data)
    return resp

@app.route("/get_result", methods=["GET"])
def get_results():
    resp = Response(status=200)
    result_name = request.args.get('name')
    if result_name is None:
        resp.status_code = 400
        return resp

    results = results_provider.get_results(result_name)
    resp.set_data(json.dumps(results))
    return resp


@app.route("/delete_result", methods=["POST"])
@validate('api_schema', 'default')
def delete_result():
    result_name = request.json['name']
    try:
        results_provider.delete_result(result_name)
    except:
        return jsonify({'message': 'Delete result did not succeed'}), 500
    else:
        return jsonify({'message': 'Result {} has been deleted'.format(result_name)}), 200

if __name__ == "__main__":
    app.run(**config)
