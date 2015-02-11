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
    .service('Step', function ($rootScope, $resource, dataUrl) {
        "use strict";

        var visitedStepList = [];
        var stepList = [];
        var yourWorkout = [];
        //var timerResource = $resource(dataUrl);
        var processSteps = function () {
            var promise = $resource(dataUrl, {}, {'query': {isArray: false}}).query();
            promise.$promise.then(function (data) {
                //
                var exercises = [];
                angular.forEach(data.set_list, function (set_list) {


                    // Make the workout overview
                    angular.forEach(set_list.exercise_list, function (exercise) {
                        yourWorkout.push({exercise: exercise.obj.name,
                                          reps: exercise.setting_text});
                    });

                    if (set_list.is_superset) {
                        angular.forEach(set_list.exercise_list, function (exercise_list) {
                            var exercise = exercise_list.setting_obj_list[0].exercise;
                            angular.forEach(exercise_list.setting_list, function (reps) {
                                stepList.push({current_step: 123,
                                               step_nr: stepList.length + 1,
                                               step_percent: 0,
                                               exercise: exercise,
                                               type: 'exercise',
                                               reps: reps,
                                               weight: 'the_weight'});
                            });
                        });
                    } else {
                        console.log('is superset');
                    }

                }, exercises);

                $rootScope.$broadcast('yourWorkoutUpdated', {
                    yourWorkout: yourWorkout
                });
            });
        };
        processSteps();

        return {
            setStep: function (step) {
                stepList.push(step);
                //console.log(stepList);
                $rootScope.$broadcast('stepUpdated', {
                    step: step
                });
            },
            getSteps: function () {
                return stepList;
            }
        };
    })
    .controller("timerCtrl", function ($scope, /*$resource,*/ /*$rootScope,*/ /*$http,*/ $routeParams, /*dataUrl,*/ Step) {
        'use strict';
        $scope.data = {};
        $scope.page = $routeParams.step;

        $scope.setCurrentStep = function (step) {
            Step.setStep(step);
        };

        $scope.$on('yourWorkoutUpdated', function (event, args) {
            $scope.yourWorkout = args.yourWorkout;
        });
    });
