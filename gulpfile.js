const gulp = require('gulp');
const eslint = require('gulp-eslint');
const flake8 = require('@petervanderdoes/gulp-flake8');

gulp.task('lint-js', function () {
  // ESLint ignores files with "node_modules" paths.
  // So, it's best to have gulp ignore the directory as well.
  // Also, Be sure to return the stream from the task;
  // Otherwise, the task may end before the stream has finished.
  return gulp.src(['**/*.js'])
  // eslint() attaches the lint output to the "eslint" property
  // of the file object so it can be used by other modules.
    .pipe(eslint())
    // eslint.format() outputs the lint results to the console.
    // Alternatively use eslint.formatEach() (see Docs).
    .pipe(eslint.format())
    // To have the process exit with an error code (1) on
    // lint error, return the stream and pipe to failAfterError last.
    .pipe(eslint.failAfterError());
});

gulp.task('lint-python', function () {
  return gulp.src(['**/*py',
    '!**/extras/**',
    '!**/build/**',
    '!**/dist/**',
    '!**/node_modules/**',
    '!**/migrations/**',
    '!**/docs/**',
    '!settings.py'])
    .pipe(flake8())
    .pipe(flake8.reporter())
    .pipe(flake8.failOnError());
});

gulp.task('lint', ['lint-js', 'lint-python']);

gulp.task('default', ['lint'], function () {
  // This will only run if the lint task is successful...
});
