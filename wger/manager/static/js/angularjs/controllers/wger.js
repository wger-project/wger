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
.controller("routineListCtrl", function ($scope, $http, dataUrl) {
    $scope.data = {};

    $http.get(dataUrl)
        .success(function (data) {
            $scope.data.routines = data
        })
        .error(function (error) {
            $scope.data.error = error;
        });
})
.controller("routineDetailCtrl", function ($scope, $http, $routeParams, dataUrl) {
    $scope.data = {};

    $scope.$on("$routeChangeSuccess", function (){

        $http.get(dataUrl + $routeParams['name'] + '/?max_deadlift=100&max_bench=100&max_squat=100&round_to=2.5')
            .success(function (data) {
                console.log(data);
                $scope.data.routine = data
            })
            .error(function (error) {
                $scope.data.error = error;
            });

    });

});
