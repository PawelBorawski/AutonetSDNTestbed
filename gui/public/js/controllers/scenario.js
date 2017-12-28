(function() {

    'use strict';

    var app = angular.module('AutonetSDNTestbed');

    app.controller('ScenarioController', ScenarioController);

    function ScenarioController($scope, $location, $http, $mdDialog, ScenarioService) {

        $scope.scenario_gui = {}

        ScenarioService.getTopologies().then(function(result) {
            $scope.topologies = result.data;
        });

        $scope.hostsDistribution = [{
            name: 'UNIFORM'
        }, {
            name: 'RANDOM'
        }];

        $scope.trafficTypes = [{
                name: "TCP"
            }, {
                name: "UDP"
            }, {
                name: "Random"
            }
        ];

        $scope.submit = function() {

            angular.forEach($scope.scenario_gui, function(value, key) {
                if(value!==null) {
                    $scope.scenario[key] = value.name;
                }
            });

            var dataToSend = JSON.stringify({ 'scenario': $scope.scenario });
            ScenarioService.saveScenario(dataToSend).then(function(result) {
                    $scope.scenarioPromise = result;
                    showDialog("Status", result.data.message);
                }).catch(function (error) {
                    $scope.scenarioPromise = error;
                    showDialog("ERROR !!!", error.data.message);
                });
        };

        $scope.topologyChanged = function(name) {
            $scope.topologyImage = 'http://topology-zoo.org/maps/' + name + '.jpg';
        };

        var showDialog = function(status, message) {
            $mdDialog.show(
               $mdDialog.alert()
               .title(status)
               .textContent(message)
               .ok('OK'));
        };



    }

}());
