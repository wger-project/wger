/* Notes:
   - gulp/tasks/browserSync.js watches and reloads compiled files
*/

var gulp  = require('gulp');
var config = require('../config');
var startBrowserSync = require('../util/startBrowserSync');

gulp.task('watch', ['build'], function() {
  startBrowserSync();
  gulp.watch(config.less.src,   ['less']);
  gulp.watch(config.assets.src, ['assets']);
  gulp.watch(config.clientDir + '/js/**', ['jshint', 'test']);
});

