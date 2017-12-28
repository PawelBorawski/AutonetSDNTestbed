import requests
import json
import time

data = {
    'name': 'FirstTestXXX2222',
    'topology': 'abilene33',
    'link_bandwidth': 1,
    'hosts_num': 1,
    'hosts_distribution': 'RANDOM',
    'min_flows': 1,
    'max_flows': 4,
    'min_bitrate': 0.5,
    'max_bitrate': 1,
    'traffic_type': 'udp',
    'max_delay': 60,
    'max_duration': 120,
    'mobility': True}

data_run = {'scenario': 'FirstTest', 'tool': 1, 'iterations': 1}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
res = requests.post(
    'http://localhost:8181/create',
    data=json.dumps(data),
    headers=headers)

#res = requests.post('http://localhost:5000/run', data=json.dumps(data_run), headers=headers)
print res.headers
print res.text
# time.sleep(200)
#res = requests.post('http://localhost:5000/stop', data=json.dumps(data_run), headers=headers)
# print res
