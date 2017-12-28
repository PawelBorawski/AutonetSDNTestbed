(function() {

    'use strict';


    angular
    .module('AutonetSDNTestbed', ['ngRoute', 'ngAnimate', 'cgBusy', 'ui.codemirror', 'ngMaterial', 'chart.js'])
    .constant('appConfig', {
        'url': "http://0.0.0.0:8181"
    })
    .value('cgBusyDefaults',{
        backdrop: true,
        delay: 300,
        minDuration: 700,
        })
    .config([
        '$locationProvider',
        '$routeProvider',
        function($locationProvider, $routeProvider) {
            $locationProvider.hashPrefix('!');
            // routes
            $routeProvider
                .when("/", {
                    templateUrl: "./partials/overview.html",
                    controller: "OverviewController"
                })
                .otherwise({
                    redirectTo: '/'
                });

            $routeProvider
                .when("/configuration", {
                    templateUrl: "./partials/configuration.html",
                    controller: "ConfigurationController"
                })
                .otherwise({
                    redirectTo: '/'
                });

            $routeProvider
                .when("/scenario", {
                    templateUrl: "./partials/scenario.html",
                    controller: "ScenarioController"
                })
                .otherwise({
                    redirectTo: '/'
                });

            $routeProvider
                .when("/modify", {
                    templateUrl: "./partials/modify.html",
                    controller: "ModifyController"
                })
                .otherwise({
                    redirectTo: '/'
                });

            $routeProvider
                .when("/results", {
                    templateUrl: "./partials/results.html",
                    controller: "NetworkController"
                })
                .otherwise({
                    redirectTo: '/'
                });

            $routeProvider
                .when("/network", {
                    templateUrl: "./partials/network.html",
                    controller: "NetworkController"
                })
                .otherwise({
                    redirectTo: '/'
                });



        }
    ]);

    //Load controller
    var app = angular.module('AutonetSDNTestbed');

    app.controller('MainController', [
        '$scope',
        function($scope) {
            $scope.test = "Testing...";
        }
    ]);

}());
