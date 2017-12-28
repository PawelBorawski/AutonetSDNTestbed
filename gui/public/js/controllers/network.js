(function() {

    'use strict';

    var app = angular.module('AutonetSDNTestbed');

    app.controller('NetworkController', NetworkController);

    function NetworkController($scope, $location, $http, $mdDialog, NetworkService) {

        var iperfResultPattern = /.*(\d*\.?\d+)\s+sec\s+(\d*\.?\d+)\s+MBytes\s+(\d*\.?\d+)\s+Mbits/g;

        $scope.network_gui = {
            scenario: null,
            tool: null
        };
        $scope.show_scenario = false;
        $scope.editorOptions = {
		    lineWrapping : true,
		    lineNumbers: false,
		    readOnly: 'nocursor'
	    };

        $scope.client_chart = {
            labels : null,
            series : ['Bandwidth'],
            datasetOverride : [{ yAxisID: 'y-axis-1' }],
            data : [
                [65, 59, 80, 81, 56, 55, 40],
                [28, 48, 40, 19, 86, 27, 90]
            ],
            options : {
                title: {
                    display: true,
                    text: 'Iperf results [CLIENT]'
                },
                scales: {
                    yAxes: [
                        {
                            id: 'y-axis-1',
                            type: 'linear',
                            display: true,
                            position: 'left',
                            ticks: {
                                maxTicksLimit: 30,
                                beginAtZero: true,
                                callback: function (value, index, values) {
                                    return value.toFixed(2) + ' Mbit/sec';
                                }
                            }
                        }
                    ],
                    xAxes: [
                        {
                            display: true,
                            ticks: {
                                maxTicksLimit: 30,
                                callback: function (value, index, values) {
                                    if (isNaN(parseFloat(value)))
                                        return value;
                                    if (values.length === index + 1) {
                                        return 'summary: 0 - ' + value + 's';
                                    }
                                    return value + 's';
                                }
                            }
                        }
                    ]
                }
            }
        };

        $scope.server_chart = {
            labels : null,
            series : ['Bandwidth', 'Jitter', 'Packet Loss'],
            datasetOverride : [{ yAxisID: 'y-axis-1' }, { yAxisID: 'y-axis-2' }, { yAxisID: 'y-axis-3' }],
            data : [
                [65, 59, 80, 81, 56, 55, 40],
                [28, 48, 40, 19, 86, 27, 90]
            ],
            options : {
                title: {
                    display: true,
                    text: 'Iperf results [SERVER]'
                },
                scales: {
                    yAxes: [
                        {
                            id: 'y-axis-1',
                            type: 'linear',
                            display: true,
                            position: 'left',
                            ticks: {
                                maxTicksLimit: 30,
                                beginAtZero: true,
                                callback: function (value, index, values) {
                                    return value.toFixed(2) + ' Mbit/sec';
                                }
                            }
                        },
                        {
                            id: 'y-axis-2',
                            type: 'linear',
                            display: true,
                            position: 'right',
                            ticks: {
                                maxTicksLimit: 30,
                                beginAtZero: true,
                                callback: function (value, index, values) {
                                    return value.toFixed(2) + ' ms';
                                }
                            }
                        },
                        {
                            id: 'y-axis-3',
                            type: 'linear',
                            display: true,
                            position: 'right',
                            ticks: {
                                maxTicksLimit: 30,
                                beginAtZero: true,
                                callback: function (value, index, values) {
                                    return value.toFixed(2) + ' %';
                                }
                            }
                        }
                    ],
                    xAxes: [
                        {
                            display: true,
                            ticks: {
                                maxTicksLimit: 30,
                                callback: function (value, index, values) {
                                    if (isNaN(parseFloat(value)))
                                        return value;
                                    if (values.length === index + 1) {
                                        return 'summary: 0 - ' + value + 's';
                                    }
                                    return value + 's';
                                }
                            }
                        }
                    ]
                }
            }
        };

        NetworkService.checkStatus().then(
            function() { $scope.isTestRunning = false; }
        );

        $scope.tools = [{
            id: 1,
            name: 'iperf'
        }];

        NetworkService.getScenarios().then(function(result) {
            $scope.scenarios = result.data;
        });

        $scope.submit = function() {
            angular.forEach($scope.network_gui, function(value, key) {
                $scope.network[key] = value.name;
            });

            var dataToSend = JSON.stringify($scope.network);
            console.log(dataToSend);

            NetworkService.runNetwork(dataToSend).then(function(result) {
                 $scope.networkPromise = result;
                 if($scope.networkPromise.status == 200) {
                    $scope.isTestRunning = true;
                    showDialog("Status", "Test has been started. Wait until it ends up.");
                    NetworkService.checkStatus().then(
                        function() {
                            $scope.isTestRunning = false;
                            showDialog("Status", "Test has been finished. You can check results");
                        }
                    );
                 };
            });

        };

        $scope.stop = function() {
            NetworkService.stopScenario();
            $scope.isTestRunning = false;
        };

        NetworkService.listResults().then(function(result) {
            $scope.resultsList = result.data;
        });

        $scope.getLogsForResult = function(name) {
            NetworkService.getResult(name).then(function(result) {
                if(result.data.length>0)
                    $scope.resultLogs = [{'name':'Aggregated clients results','id':'aggregated'}]
                $scope.resultLogs = $scope.resultLogs.concat(result.data);
            });
        };

        $scope.deleteResult = function() {
            var name = $scope.result.name;
            NetworkService.deleteResult(name).then(function(result) {
                showDialog("Status", "Result has been deleted.");
            });
        };

        $scope.displayResults = function(id) {
            console.log(id);
            var hosts = {};
  
            angular.forEach($scope.resultLogs.slice(1), function(value) {
                console.log(value.name);
                
                if(id == 'aggregated' ){

                    var host = value.name.split(' ')[4];

                    var lines = value.client.split("\n");
                    var summary = lines[lines.length-1];
                    var transfer = /(\d+(\.\d+)?\s+(MBytes)+|(KBytes)+|(GBytes)+)/g.exec(summary);
                    var band = /(\d+(\.\d+)?\s+(Mbits\/sec)+|(Kbits\/sec)+|(Gbits\/sec)+)/g.exec(summary);
                    if (transfer === null || band === null){
                        summary = lines[lines.length-2];
                        transfer = /(\d+(\.\d+)?\s+(MBytes)+|(KBytes)+|(GBytes)+)/g.exec(summary);
                        band = /(\d+(\.\d+)?\s+(Mbits\/sec)+|(Kbits\/sec)+|(Gbits\/sec)+)/g.exec(summary);
                    }

                    var float_transfer = parseFloat(transfer[0].split(" ")[0]);
                    var float_band = parseFloat(band[0].split(" ")[0]);
                    if (transfer.indexOf("KBytes") > -1)
                        float_transfer = float_transfer/1024;
                    if (band.indexOf("Kbits/sec") > -1)
                        float_band = float_band/1024;
                    if (transfer.indexOf("GBytes") > -1)
                        float_transfer = float_transfer*1024;
                    if (band.indexOf("Gbits/sec") > -1)
                        float_band = float_band*1024;

                    if (hosts[host] === undefined)
                        hosts[host] = {'transfer':float_transfer, 'band':float_band};
                    else {   
                        hosts[host]['transfer'] += float_transfer;
                        hosts[host]['band'] += float_band ;
                    }

                    $scope.client_chart.labels = [];
                    $scope.client_chart.data = [];
                    angular.forEach(hosts, function(value, key) {
                        $scope.client_chart.labels.push(key);
                        $scope.client_chart.data.push(value.band);
                    });
                }

                else if(value.id === id) {
                    console.log(value.name);
                    $scope.resultClient = value.client;
                    $scope.resultServer = value.server;

                    var client_labels = [];
                    var client_transferData = [];
                    var client_bandwidthData = [];
                    angular.forEach($scope.resultClient.split("\n"), function(value) {
                        var result = /(\d*\.\d+)\s+sec\s+(\d+(\.\d+)?)\s+[a-zA-Z]{3,}\s+(\d*\.\d+)/g.exec(value);
                        console.log(result);
                        if (result && result.length > 3) {

                            var seconds = result[1],
                                transfer = result[2],
                                bandwidth = result[4];
                            console.log(seconds);
                            console.log(bandwidth);
                            client_labels.push(parseInt(seconds));
                            client_transferData.push(transfer);
                            client_bandwidthData.push(bandwidth);
                        }
                    });

                    $scope.client_chart.labels = client_labels;
                    $scope.client_chart.data = [client_bandwidthData];

                    var server_labels = [];
                    var server_transferData = [];
                    var server_bandwidthData = [];
                    var server_jitterData = [];
                    var server_packetLossData = [];
                    angular.forEach($scope.resultServer.split("\n"), function(value) {
                        var result = /(\d*\.\d+)\s+sec\s+(\d+(\.\d+)?)\s+[a-zA-Z]{3,}\s+(\d*\.\d+)\s+[a-zA-Z]{3,}\/sec(?:\s+(\d*\.\d+)\s+ms\s+\d*\/\s+\d*\s+\((\d*(\.\d+)?)%\)){0,}/g.exec(value);
                        if (result && result.length > 3) {
                            var seconds = result[1],
                                transfer = result[2],
                                bandwidth = result[4];
                            server_labels.push(parseInt(seconds));
                            server_transferData.push(transfer);
                            server_bandwidthData.push(bandwidth);
                            if(result.length>5) {
                                var jitter = result[5],
                                    packetLoss = result[6];
                                server_jitterData.push(jitter);
                                server_packetLossData.push(packetLoss);
                            }
                        }

                    });

                    $scope.server_chart.labels = server_labels;
                    $scope.server_chart.data = [server_bandwidthData, server_jitterData, server_packetLossData]

                }
            });

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