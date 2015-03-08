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

angular.module("workoutTimer")
    .constant('workoutLogUrl', "/api/v2/workoutlog/")
    .constant('workoutSessionUrl', "/api/v2/workoutsession/")
    .constant('userprofileUrl', "/api/v2/userprofile/")
    .service('Step', function ($rootScope, $resource, dataUrl, userprofileUrl) {
        "use strict";

        var dayCanonicalRepr;
        var userProfile;
        var stepList = [];
        var yourWorkout = [];

        var getDayCanonical = function () {
            /*
             * Loads the full canonical representation of the current day
             */
            var promise = $resource(dataUrl, {}, {'query': {isArray: false}}).query();
            promise.$promise.then(function (data) {
                dayCanonicalRepr = data;
            });
        };
        getDayCanonical();

        var processSteps = function () {
            /*
             * Process the canonical representation and generate the initial steps
             */
            angular.forEach(dayCanonicalRepr.set_list, function (set_list) {

                // Make the workout overview
                angular.forEach(set_list.exercise_list, function (exercise) {
                    yourWorkout.push({exercise: exercise.obj.name,
                                      reps: exercise.setting_text});
                });
                $rootScope.$broadcast('todaysWorkoutUpdated', {
                    yourWorkout: yourWorkout
                });

                // Make the list of exercise steps
                // Supersets need extra work to group the exercises and reps together
                if (set_list.is_superset) {
                    var total_reps = set_list.exercise_list[0].setting_list.length;
                    for (var i = 0; i <= total_reps; i++) {

                        angular.forEach(set_list.exercise_list, function (exercise_list) {
                            var reps = exercise_list.setting_list[i];
                            var exercise = exercise_list.obj;
                            stepList.push({step_percent: 0,
                                           exercise: exercise,
                                           type: 'exercise',
                                           reps: reps,
                                           weight: 50});

                            if (userProfile.timer_active) {
                                stepList.push({step_percent: 0,
                                               type: 'pause',
                                               time: userProfile.timer_pause});
                            }
                        });
                    }

                } else {
                    angular.forEach(set_list.exercise_list, function (exercise_list) {
                        var exercise = exercise_list.setting_obj_list[0].exercise;
                        var reps = exercise_list.setting_list[i];
                        angular.forEach(exercise_list.setting_list, function (reps) {
                            stepList.push({step_percent: 0,
                                           exercise: exercise,
                                           type: 'exercise',
                                           reps: reps,
                                           weight: 50});

                            if (userProfile.timer_active) {
                                stepList.push({step_percent: 0,
                                               type: 'pause',
                                               time: userProfile.timer_pause});
                            }
                        });
                    });
                }
            });
        };

        var getProfile = function () {
            /*
             * Load the user's profile data, needed for pauses
             */
            var promise = $resource(userprofileUrl, {}, {'query': {isArray: false}}).query();
            promise.$promise.then(function (data) {
                userProfile = data.results[0];
                processSteps();
            });
        };
        getProfile();


        return {
            getStep: function (stepId) {
                console.log(stepId);
                console.log(stepList[stepId]);
                return stepList[stepId];
            },
            getSteps: function () {
                return stepList;
            }
        };
    })
    .controller("workoutOverviewCtrl", function ($scope, Step) {
        'use strict';

        $scope.$on('todaysWorkoutUpdated', function (event, args) {
            $scope.yourWorkout = args.yourWorkout;
        });
    })
    //.controller("timerCtrl", function ($scope, /*$resource,*/ /*$rootScope,*/ /*$http,*/ $routeParams, /*dataUrl,*/ Step) {
    .controller("timerCtrl", function ($scope, $routeParams, Step) {
        'use strict';

        $scope.data = {};
        //$scope.totalPages = Step.getSteps().length;
        $scope.page =  parseInt($routeParams.step);

        /*
         * Load the current step
         */
        $scope.getStep = function () {
            if($scope.page) {
                $scope.stepData = Step.getStep($scope.page);
            }
        };
        $scope.getStep();

    });
