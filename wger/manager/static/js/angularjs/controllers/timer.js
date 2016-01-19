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
    .constant('WORKOUT_LOG_URL', "/api/v2/workoutlog/")
    .constant('WORKOUT_SESSION_URL', "/api/v2/workoutsession/")
    .constant('USER_PROFILE_URL', "/api/v2/userprofile/")
    .directive("progressBar", function ($timeout) {
        return {
            restrict: "EA",
            scope: {
                total: '=total',
                complete: '=complete',
                barClass: '@barClass',
                completedClass: '=?'
            },
            transclude: true,
            link: function (scope, elem, attrs) {

                scope.label = attrs.label;
                scope.completedClass = (scope.completedClass) || 'progress-bar-danger';

                scope.$watch('complete', function () {

                  //change style at 100%
                  var progress = scope.complete / scope.total;
                  if (progress >= 1) {
                    $(elem).find('.progress-bar').addClass(scope.completedClass);
                  }
                  else if (progress < 1) {
                    $(elem).find('.progress-bar').removeClass(scope.completedClass);
                  }

                });

            },
            template:
                "<span class='small'>{{ label }}</span>" +
                "<div class='progress'>"+
          "   <div class='progress-bar {{ barClass }}' title='{{ complete / total * 100 | number:0 }}%' style='width:{{ complete / total * 100 }}%;'>{{ complete | number:0 }} / {{ total }}</div>" +
                "</div>"
        };
    })
    .service('Step', function ($rootScope, $resource, $q, dataUrl, USER_PROFILE_URL, WORKOUT_SESSION_URL) {
        "use strict";

        var dayCanonicalRepr;
        var userProfile;
        var stepList = [];
        var yourWorkout = [];
        var deferred = $q.defer();

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
                        var exercise = exercise_list.obj;
                        var reps = exercise_list.setting_list[i];
                        angular.forEach(exercise_list.setting_obj_list, function (set) {
                            stepList.push({step_percent: 0,
                                           exercise: exercise,
                                           type: 'exercise',
                                           reps: set.reps,
                                           weight: set.weight ? set.weight : 0});

                            if (userProfile.timer_active) {
                                stepList.push({step_percent: 0,
                                               type: 'pause',
                                               time: userProfile.timer_pause});
                            }
                        });
                    });
                }
            });

            deferred.resolve(stepList);
        };

        var getDayCanonical = $resource(dataUrl, {}, {'query': {isArray: false}}).query().$promise;
        getDayCanonical.then(function (data) {
            dayCanonicalRepr = data;
        });

        var getProfile = $resource(USER_PROFILE_URL, {}, {'query': {isArray: false}}).query().$promise;
        getProfile.then(function (data) {
            userProfile = data.results[0];
        });

        var finish = $resource(WORKOUT_SESSION_URL, {}, {'query': {isArray: false}});

        $q.all([getDayCanonical, getProfile]).then(function () {
            processSteps();
        });

        return {
            getSteps: function () {
                return deferred.promise;
            },
            finish: function () {
                return finish;
            }
        };
    })
    .controller("workoutOverviewCtrl", function ($scope, Step) {
        'use strict';

        $scope.$on('todaysWorkoutUpdated', function (event, args) {
            $scope.yourWorkout = args.yourWorkout;
        });
    })
    .controller("timerCtrl", function ($scope, $routeParams, $interval, Step, WORKOUT, DASHBOARD) {
        'use strict';

        var allSteps = [];
        var intervalTimer;
        var yourWorkout;

        $scope.data = {};
        $scope.page = parseInt($routeParams.step);
        $scope.stepData = null;
        $scope.currentTimer = 0;
        $scope.totalTimer = 0;
        $scope.nbOfSteps = 0;
        $scope.isCompleted = false;
        $scope.formData = {
            workout: WORKOUT,
            date: new Date()
        };

        function startTimer(time) {
            $scope.currentTimer = parseInt(time);

            intervalTimer = $interval(function () {
                var diff = time ? -1 : 1
                $scope.currentTimer += diff;
                $scope.totalTimer += Math.abs(diff); // Total timer need amount of time

                // If we are going downwards, we need a way to skip once there's no time left
                if ($scope.currentTimer <= 0) {
                    $scope.skip();
                }
            }, 1000);
        }

        function clearTimer() {
            if (intervalTimer) {
                $interval.cancel(intervalTimer);
            }
        }

        function loadPage(page) {
            clearTimer();

            // Check if workout is done
            if (page >= allSteps.length) {
                $scope.page--;
                $scope.isCompleted = true;

                $scope.formData.time_end = new Date();
                $scope.formData.time_start = new Date($scope.formData.time_end);
                $scope.formData.time_start.setSeconds($scope.formData.time_start.getSeconds() - $scope.totalTimer);
            } else {
                $scope.stepData = allSteps[page];

                startTimer($scope.stepData.type === 'pause' ? $scope.stepData.time : null);
            }
        }

        function formatDate(d) {
            return d.getFullYear() + "-" + (d.getMonth()+1) + "-" + d.getDate();
        }

        function formatTime(d) {
            return d.getHours() + ":" + d.getMinutes();
        }

        /*
         * Load the steps
         */
        $scope.getSteps = function () {
            if($scope.page) {
                Step.getSteps().then(function (steps) {
                    allSteps = steps;
                    $scope.nbOfSteps = allSteps.length;
                    loadPage($scope.page-1);
                });
            }
        };
        $scope.getSteps();

        $scope.skip = function () {
            $scope.page++;
            loadPage($scope.page-1);
        };

        $scope.save = function () {
            $scope.page++;
            loadPage($scope.page-1);
        };

        $scope.finish = function () {
            $scope.formData.date = formatDate($scope.formData.date);
            $scope.formData.time_start = formatTime($scope.formData.time_start);
            $scope.formData.time_end = formatTime($scope.formData.time_end);

            Step.finish().save($scope.formData).$promise.then(function () {
                window.location.href = DASHBOARD;
            });
        };

        $scope.reduceTimer = function () {
            $scope.currentTimer -= 10;
        };

        $scope.increaseTimer = function () {
            $scope.currentTimer += 10;
        };

    });
