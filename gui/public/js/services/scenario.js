(function() {
    'use strict';

    var app = angular.module('AutonetSDNTestbed');

    app.factory('ScenarioService', ScenarioService);

    function ScenarioService($http, $q, appConfig) {

        var _saveScenario = function(data){
    		var deferred = $q.defer();

    		var promise = $http.post(appConfig.url + "/create", data);
    		return promise;
    	};

        var _getTopologies = function() {
            var deferred = $q.defer();

            var promise = $http.get(appConfig.url + "/topologies");

            return promise;
        };

    	return {
    		saveScenario:  _saveScenario,
    		getTopologies: _getTopologies
    	};
    }

}());
