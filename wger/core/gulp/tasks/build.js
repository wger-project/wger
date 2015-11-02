var gulp = require('gulp');
var gutil = require('gulp-util');
var config = require('../config');

gulp.task('build', ['bower', 'clean', 'less', 'assets'], function(){
    global.isBuilding = false;
});
