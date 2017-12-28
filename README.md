# AUTONET Software-Defined Networking (SDN) Testbed

## Overview

AUTONET Testbed is the Mininet-based tool that allows to prototype SDN algorithms and solutions. AUTONET Testbed makes use of:
* **Mininet** to emulate real-world network topologies downloaded from Topology ZOO (http://www.topology-zoo.org/)
* **Iperf** to generate and push traffic between network hosts. 

AUTONET Testbed may be useful for researchers looking for simple and lightweight SDN emulator to test and evaluate their traffic engineering algorithms running on the top of SDN controller.  Our tool provides convenient Graphical User Interface allowing to easily create, modify and run test scenarios as well as view traffic results measured by Iperf. When creating a new scenario you can choose one of network from topology ZOO and define scenario parameters such as range of traffic bandwidth, number of hosts or test duration. 

AUTONET Testbed may be used with any SDN Controller. 

## Installation

Instruction was tested on Ubuntu 16.10. If you face any problems, please check out the troubleshooting section at first.

#### 1. Clone this repo

#### 2. Mininet Scenario Generator (mngen)

* Go to mngen folder:<br>
   `cd mngen`  

* Install prerequisites: Python 2.7 with pip, Mininet:<br>
   `sudo apt-get install python-pip mininet`  

* Install python required modules:<br>
  `pip install -r requirements.txt`  

* mngen is ready to run!

#### 3. GUI

* Go to gui folder:<br>
  `cd gui`  

* Install nodejs and npm:<br>
  `sudo apt-get install nodejs-legacy npm`  

* Install bower, gulp and other dependencies:<br>
  WARNING: don't use sudo with these commands! If you get EACCES error check out the troubleshooting section case 2.  <br> 
  `npm install`
   
* gui is ready to run!

#### Troubleshooting

1. Node not found error while running bower or gulp: `/usr/bin/env: ‘node’: No such file or directory`</b>

   Bower and gulp try to find node folder, while correct folder is nodejs. It can be fixed by a simple link:<br>
   `sudo ln -s /usr/bin/nodejs /usr/bin/node`

   More on this topic: https://github.com/animetosho/Nyuu/issues/14

2. EACCES error while running: `npm -g install`

   In most cases it means that npm doesn't have rights to write in its directory. Check the npm path to confirm that:<br>
   `npm config get prefix`
   
   If you get `/usr/local` you can fix it with the commands:<br>
   `sudo mkdir -p $(npm config get prefix)/{lib/node_modules,bin,share}`<br>
   `sudo chown -R $(whoami) $(npm config get prefix)/{lib/node_modules,bin,share}`
   
   If you get other path or it still doesn't work, try the option 2 from this manual: https://docs.npmjs.com/getting-started/fixing-npm-permissions

3. Error: Cannot find module 'gulp-*' while running: 'gulp dev'

   If you have used option 2 from manual referred in the previous step, you should also link globally installed modules:<br>

   `npm link gulp gulp-connect jshint gulp-jshint gulp-uglify gulp-minify-css gulp-clean run-sequence`


## Running

To run the 'mngen' (server-side) module use below command from 'mngen' directory:

`sudo python mngen_api.py`

To run the GUI just use below command from 'gui' directory:

`node gui.js`

## Usage

### 1. GUI

The preferred interface for working with AUTONET Testbed is Web GUI. You can access GUI at http://localhost:8080/. 

### 2. CLI 

You can also access 'mngen' module services by CLI. Use `./mngen_cli.py --help` command to discover CLI capabilites. 

### 3. REST API

Alternatively, you can invoke 'mngen' module services via REST-based API. This method requires only 'mngen' module to be up and running.  

## Authors
* Tomasz Osiński (osinstom@gmail.com)
* Paweł Borawski (borawpa@gmail.com)
