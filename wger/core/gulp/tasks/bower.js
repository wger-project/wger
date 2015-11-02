var gulp = require('gulp');
var bower = require('gulp-bower');
 
gulp.task('bower', function() {
  return bower()
    .pipe(gulp.dest('wger/core/static/lib/'))
});