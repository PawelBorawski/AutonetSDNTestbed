(function() {
    'use strict';

    var app = angular.module('AutonetSDNTestbed');

    app.factory('NetworkService', NetworkService);

    function NetworkService($http, $q, $timeout, appConfig) {

    	var _runNetwork = function(data) {
    	    var deferred = $q.defer();

    		var promise = $http.post(appConfig.url + "/run", data);
    		return promise;
    	};

    	var _getScenarios = function() {
            var deferred = $q.defer();

    		var promise = $http.get(appConfig.url + "/scenarios");
    		return promise;
    	};

        var _getScenarioDetails = function(id) {
            var deferred = $q.defer();

            var promise = $http.get(appConfig.url + "/scenario_details?id="+id);
            return promise;
        };

        var _stopScenario = function() {
            var deferred = $q.defer();

            var promise = $http.post(appConfig.url + "/stop");
            return promise;
        };

        var _checkStatus = function() {
            var defer = $q.defer();

            (function fetchStatus(){
                $http.get(appConfig.url + "/status").then(function(result){
                        console.log("Not busy");
                        defer.resolve();
                    }, function(error) {
                        if(error.status == 486) {
                            $timeout(fetchStatus, 10000);
                        }
                    }
                )

            })()

            return defer.promise;
        };

        var _modifyScenario = function(data) {
            var deferred = $q.defer();

            var promise = $http.post(appConfig.url + "/modify", data);
            return promise;
        };

        var _deleteScenario = function(data) {
            var deferred = $q.defer();

            var promise = $http.post(appConfig.url + "/delete", data);
            return promise;
        };

        var _getResult = function(scenario) {
            var deferred = $q.defer();

            var promise = $http.get(appConfig.url + "/get_result?name="+scenario);
            return promise;
        };

        var _listResults = function() {
            var deferred = $q.defer();

            var promise = $http.get(appConfig.url + "/list_results");
            return promise;
        };

        var _deleteResult = function(name) {
            var deferred = $q.defer();

            var promise = $http.post(appConfig.url + "/delete_result", {'name':name});
            return promise;
        };

    	return {
    		runNetwork: _runNetwork,
            getScenarios: _getScenarios,
            getScenarioDetails: _getScenarioDetails,
            stopScenario: _stopScenario,
            checkStatus: _checkStatus,
            modifyScenario: _modifyScenario,
            deleteScenario: _deleteScenario,
            getResult: _getResult,
            listResults: _listResults,
            deleteResult: _deleteResult
    	};
    }

}());
