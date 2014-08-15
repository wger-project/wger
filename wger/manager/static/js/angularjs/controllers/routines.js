/*
 * This file is part of wger Workout Manager.
 *
 * wger Workout Manager is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * wger Workout Manager is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 */

angular.module("routineGenerator")
.constant('dataUrl', "/api/v2/routine-generator/")
.controller("routineListCtrl", function ($scope, $resource, $http, dataUrl) {
    $scope.data = {};

    $scope.routinesResource = $resource(dataUrl, {}, {'query': {isArray: false}});
    $scope.listRoutines = function () {
        $scope.routines = $scope.routinesResource.query();
    }

    $scope.listRoutines();
})
.controller("routineDetailCtrl", function ($scope, $http, $resource, $routeParams, dataUrl) {
    $scope.data = {};
    $scope.config = {name: 'korte',
                     max_deadlift: 100,
                     max_bench: 100,
                     max_squat: 100,
                     round_to: 2.5
                    };

    $scope.routineResource = $resource(dataUrl + ':name/', {}, {'query': {isArray: false}});

    $scope.getRoutine = function () {
        $scope.config.name = $routeParams['name'];
        var promise = $scope.routineResource.query({
                                    name: $scope.config.name,
                                    max_deadlift: $scope.config.max_deadlift,
                                    max_bench: $scope.config.max_bench,
                                    max_squat: $scope.config.max_squat,
                                    round_to: $scope.config.round_to
                                });
        promise.$promise.then(function (data) {
            // Move the data into the following format: [week][day][exercise]
            var tmp = {};
            $scope.data = data;
            angular.forEach(data.items, function(value, key) {
                if(angular.isUndefined(tmp[value.week])) {
                    tmp[value.week] = {};
                }

                if(angular.isUndefined(tmp[value.week][value.day])) {
                    tmp[value.week][value.day] = [];
                }

                tmp[value.week][value.day].push(value);
            });

            $scope.data.items = tmp;
        });
    };

    $scope.getRoutine();
});
