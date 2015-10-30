'use strict';
var gulp = require('gulp');
var requireDir = require('require-dir');

// Require all tasks in gulp/tasks, including subfolders
requireDir('./wger/core/gulp/tasks', { recurse: true });

gulp.task('default', ['watch']);
