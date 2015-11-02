var gulp       = require('gulp');
var imagemin   = require('gulp-imagemin');
var config     = require('../config').assets;


// In place modifications - don't use as a watch task
// It is recommended to stop any watch process you may have
//  running prior to running this task. 
gulp.task('assets:image-optimize', function() {
  return gulp.src(config.imgSrc)
    .pipe(imagemin(config.imageminOptions))
    .pipe(gulp.dest(config.imgDest));
});
