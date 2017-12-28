(function() {

    'use strict';

    var app = angular.module('AutonetSDNTestbed');

    app.controller('HeaderController', HeaderController);

    function HeaderController($scope, $location) {
        $scope.isActive = function(viewLocation) {
            return viewLocation === $location.path();
        };

        $scope.loadOverview = function() {
            $location.url('/');
        };

        $scope.loadConfiguration = function() {
            $location.url('/configuration');
        };

        $scope.loadScenario = function() {
            $location.url('/scenario');
        };

        $scope.loadModify = function() {
            $location.url('/modify');
        };

        $scope.loadNetwork = function() {
            $location.url('/network');
        };

        $scope.loadResults = function() {
            $location.url('/results');
        };

    }

}());
