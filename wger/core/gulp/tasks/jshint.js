var gulp = require('gulp');
var jshint = require('gulp-jshint');
var config = require('../config').jshint;

gulp.task('jshint', function() {
    return gulp.src(config.src)
        .pipe(jshint())
        .on('error', function() {
            beep();
        });
});
