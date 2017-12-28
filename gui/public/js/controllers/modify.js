(function() {

    'use strict';

    var app = angular.module('AutonetSDNTestbed');

    app.controller('ModifyController', ModifyController);


    function ModifyController($scope, $location, $http, $filter, $mdDialog, NetworkService) {

        $scope.gui = {}

        // XML Web editor options
        $scope.editorOptions = {
		    lineWrapping : true,
		    lineNumbers: false,
		    mode: 'xml',
	    };

	    // get all available scenarios from server
        NetworkService.getScenarios().then(function(result) {
            $scope.scenarios = result.data;
        });

        // load new XML scenario data when new scenario has been chosen
        $scope.scenarioChanged = function() {
            if($scope.gui.scenario === null || $scope.gui.scenario.id === null)
                return;

            NetworkService.getScenarioDetails($scope.gui.scenario.id).then(function(result) {
                $scope.xmlScenario = result.data.content;
            });

        }

        $scope.deleteScenario = function() {

            var confirm = $mdDialog.confirm()
                .title('Would you like to delete scenario?')
                .textContent('This will remove scenario XML description')
                .ok('DELETE')
                .cancel('CANCEL');

            $mdDialog.show(confirm).then(function() {
                var scenario = JSON.stringify({ 'name': $scope.gui.scenario.name });
                NetworkService.deleteScenario(scenario);
                clean();
            });

        }

        // send request mn_scenario_gen to modify scenario on its local db
        $scope.submit = function() {
            var data = {'name': $scope.gui.scenario.name, 'scenario' : $scope.xmlScenario};
            NetworkService.modifyScenario(data).then(function(result) {
                $mdDialog.show(
                    $mdDialog.alert()
                    .title('Status')
                    .textContent(result.data.message)
                    .ok('OK')
                );
            }, function(error) {
                $mdDialog.show(
                    $mdDialog.alert()
                    .title('ERROR !!!')
                    .textContent(error.data.message)
                    .ok('OK')
                );
            });
        }

        // reset all changes in XML scenario description
        $scope.reset = function() {
            // TODO: implement logic
            console.log("reset");
        }

        // draw scenario graph function
        $scope.drawScenario = function() {

            if($scope.gui.scenario === null || $scope.gui.scenario.id === null || $scope.xmlScenario === null)
                return;

                var parser = new DOMParser();
                var xmlDoc = parser.parseFromString($scope.xmlScenario, "application/xml");
                var switches = xmlDoc.getElementsByTagName("switch");
                var links = xmlDoc.getElementsByTagName("link");
                var hosts = xmlDoc.getElementsByTagName("host");

                var nodes = [];
                var edges = [];

                angular.forEach(switches, function(value, key) {
                    nodes.push({id: value.attributes.id.nodeValue, label: value.attributes.name.nodeValue, color: '#2196F3', font:{size: 20, color:'#ffffff'}});
                });
                angular.forEach(hosts, function(value, key) {
                    nodes.push({id: value.attributes.id.nodeValue, label: value.attributes.name.nodeValue, color: '#c0c0c0', shape: 'box'});
                });
                angular.forEach(links, function(value, key) {
                    edges.push({from: value.attributes.src.nodeValue, to: value.attributes.dst.nodeValue});
                });

                // create an array with nodes
                var nodesDataset = new vis.DataSet(nodes);

                // create an array with edges
                var edgesDataset = new vis.DataSet(edges);

                // create a network
                var container = document.getElementById('scenario_graph');

                // provide the data in the vis format
                var data = {
                    nodes: nodesDataset,
                    edges: edgesDataset
                };
                var options = {height:'120%', width: '120%'};

                // initialize your network!
                var network = new vis.Network(container, data, options);

        };

        var clean = function() {
            $scope.gui.scenario = '';
            $scope.xmlScenario = '';
            var container = document.getElementById('scenario_graph');
            container.innerHTML = "";
            NetworkService.getScenarios().then(function(result) {
                $scope.scenarios = result.data;
            });
        };

    }

}());