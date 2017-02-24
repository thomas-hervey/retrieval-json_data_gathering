// gulpfile.js
var requireDir = require('require-dir');
requireDir('./gulp/tasks', { recurse: true });


'use strict';

// requirements
var browserSync = require('browser-sync').create(),
    cache = require('gulp-cache'),
    cssnano = require('gulp-cssnano'),
    del = require('del'),
    gulp = require('gulp'),
        gulpBrowser = require("gulp-browser"),
    imagemin = require('gulp-imagemin'),
    reactify = require('reactify'),
    runSequence = require('run-sequence'),
    sass = require('gulp-sass'),
    size = require('gulp-size'),
    useref = require('gulp-useref'),
    uglify = require('gulp-uglify'),
    gulpIf = require('gulp-if');


//
// // tasks
//
gulp.task('transform', function () {
    return gulp.src('./app/static/scripts/jsx/*.js')
        .pipe(gulpBrowser.browserify({transform: ['reactify']}))
        .pipe(gulp.dest('./app/static/scripts/js/'))
        .pipe(size());
});
//
// gulp.task('del', function () {
//     return del(['./app/static/scripts/js']);
// });
//
// gulp.task('default', ['del'], function () {
//     gulp.start('transform');
//     gulp.watch('./app/static/scripts/jsx/*.js', ['transform']);
// });
//
//
//
//
//
// // gulp.task('sass', function () {
// //   return gulp.src('./sass/**/*.scss')
// //     .pipe(sass.sync().on('error', sass.logError))
// //     .pipe(gulp.dest('./css'));
// // });
//
// // gulp.task('sass:watch', function () {
// //   gulp.watch('./sass/**/*.scss', ['sass']);
// // });
//
//
//
//
//
//
//
//
//
//
// // Static server
// gulp.task('browser-sync', function() {
//     browserSync.init({
//         server: {
//             baseDir: "./"
//         }
//     });
// });
//
// // or...
//
// gulp.task('browser-sync', function() {
//     browserSync.init({
//         proxy: "yourlocal.dev"
//     });
// });

gulp.task('default', function (callback) {
  runSequence(['sass','browserSync', 'watch'],
    callback
  )
});

gulp.task('sass', function(){
  return gulp.src('app/static/scss/**/*.scss')
    .pipe(sass()) // Converts Sass to CSS with gulp-sass
    .pipe(gulp.dest('app/static/css'))
      .pipe(browserSync.reload({
          stream: true
      }))
});

gulp.task('browserSync', function () {
    browserSync.init({
        // server: {
        //     baseDir: 'app/templates'
        // },
        proxy: 'http://localhost:5000/'

    })
});

gulp.task('watch', ['browserSync', 'sass'], function () {
    gulp.watch('app/templates/*.html', browserSync.reload);
    gulp.watch('app/static/scss/**/*.+(scss|sass)', ['sass']);
    gulp.watch('app/static/js/**/*.js', browserSync.reload);
    gulp.watch('app/*.py', browserSync.reload);
});




gulp.task('build', function (callback) {
  runSequence('clean:dist',
    ['sass', 'useref', 'images', 'fonts'],
    callback
  )
});

gulp.task('clean:dist', function() {
  return del.sync('dist');
});

gulp.task('useref', function(){
  return gulp.src('app/templates/*.html')
    .pipe(useref())
    .pipe(gulpIf('*.js', uglify()))
    // Minifies only if it's a CSS file
    .pipe(gulpIf('*.css', cssnano()))
    .pipe(gulp.dest('dist'))
});

gulp.task('images', function(){
  return gulp.src('app/images/**/*.+(png|jpg|jpeg|gif|svg)')
  // Caching images that ran through imagemin
  .pipe(cache(imagemin({
      interlaced: true
    })))
  .pipe(gulp.dest('dist/images'))
});

gulp.task('fonts', function() {
  return gulp.src('app/fonts/**/*')
  .pipe(gulp.dest('dist/fonts'))
});