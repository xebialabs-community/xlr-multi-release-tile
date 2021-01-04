/*
Copyright 2021 XEBIALABS
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/
'use strict';

(function () {
    var ReportController = function($http, $scope) {

    $scope.resultCis =[""]
    $scope.submit = function() {
          $http.get('/api/extension/reportlist?folderPath=' + $scope.folderPath).then(
          function success(response) {
              $scope.resultCis = response.data.entity;
              $scope.stdout = response.data.stdout;
              $scope.stderr = response.data.stderr;
              $scope.exception = response.data.exception;
              $scope.response = response.data.entity;
              $scope.status = response.status
          },
          function error(response) {
              $scope.stdout = response.data.stdout;
              $scope.stderr = response.data.stderr;
              $scope.exception = response.data.exception;
              $scope.response = response.data.entity;
              $scope.status = response.status;
          });
    };
    $scope.testreport = function() {
        $http.get('/api/extension/report?folderPath=' + $scope.folderPath + '&type=' + $scope.selectedValue).then(
            function success(response) {
                $scope.stdout = response.data.stdout;
                $scope.stderr = response.data.stderr;
                $scope.exception = response.data.exception;
                $scope.response = response.data.entity;
                $scope.status = response.status;
            },
            function error(response) {
                $scope.stdout = response.data.stdout;
                $scope.stderr = response.data.stderr;
                $scope.exception = response.data.exception;
                $scope.response = response.data.entity;
                $scope.status = response.status;
            });
    };
    $scope.generatecsv = function() {
      console.log("HELLO THERE")
        $http.get('/api/extension/planner').then(
            function success(response) {
                $scope.stdout = response.data.stdout;
                $scope.stderr = response.data.stderr;
                $scope.exception = response.data.exception;
                $scope.status = response.status;
                $scope.csvContent = "data:text/csv;charset=utf-8," + response.data.entity;
                $scope.encodedUri = encodeURI($scope.csvContent);
                window.open($scope.encodedUri);
            //alert($scope.encodedUri);
            },
      function error(response) {
          $scope.stdout = response.data.stdout;
          $scope.stderr = response.data.stderr;
          $scope.exception = response.data.exception;
          $scope.status = response.status;
      });
    };

    $scope.submit();
    }
    ReportController.$inject = ['$http','$scope' ];
    angular.module('extension.report', []);
    angular.module('extension.report').controller('xlrelease.report.ReportController', ReportController);
})();
