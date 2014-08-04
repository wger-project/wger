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
    $scope.config = {max_deadlift: 100,
                     max_bench: 100,
                     max_squat: 100,
                     round_to: 1.25,
                     name: ''};

    $scope.routineResource = $resource(dataUrl + ':name/',
                                        {
                                            name: 'korte',
                                            max_deadlift: 100,
                                            max_bench: 100,
                                            max_squat: 100,
                                            round_to: 2.5
                                        },
                                        {'query': {isArray: false}}
                                );

    $scope.showRoutine = function () {
        $scope.config.name = $routeParams['name'];
        $scope.data = $scope.routineResource.query( {
                                            name: 'korte',
                                            max_deadlift: $scope.config.max_deadlift,
                                            max_bench: $scope.config.max_bench,
                                            max_squat: $scope.config.max_squat,
                                            round_to: 2.5
                                        });
        $scope.data.$promise.then(function (data) {
            //console.log(data);
        });
    }

    $scope.showRoutine();
});
