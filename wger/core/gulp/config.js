var argv = require('yargs').argv;
var production = !!argv.production;

var dest = "./wger/core/static/build";
var src = "./wger/core/static";

var lessSource = src + "/less/app.less";
var lessDestination = dest + "/css";
var assetsSource = src + "/assets/**";
var assetsDestination = dest + "/assets";
var imagesSource = src + "/images/**/*.{gif,jpg,jpeg,tiff,png,svg}";
var imagesDestination = src + "/assets/img";

module.exports = {

  dest: dest,
  clientDir: src,

  browserSyncMode: "proxy",
  browserSyncDebug: false,

  browserSync: {
    all: {
      port: process.env.PORT || 3000,
      // open browser window on start
      open: false
    },
    debug: {
      logFileChanges: true,
      logLevel: "debug"
    },
    serverOptions: {
      server: {
        baseDir: dest
      },
      files: [
        dest + "/**",
        // Exclude Map files
        "!" + dest + "/**.map"
      ],
    },
    proxyOptions: {
      proxy: 'localhost:8000'
    }
  },

  less: {
    src: lessSource,
    dest: lessDestination
  },

  assets: {
    src: assetsSource,
    dest: assetsDestination,
    processImages: /\.(gif|jpg|jpeg|tiff|png)$/i,
    imageminOptions: {
      progressive: true,
      svgoPlugins: [{removeViewBox: false}],
      // png optimization
      optimizationLevel: 1
    },
    imgSrc: imagesSource,
    imgDest: imagesDestination
  },

  jshint: {
    src: [
      'gulpfile.js',
      './client/js/index.js',
      './client/js/**/*.js'
    ]
  },

  test: {
    src: './client/**/*test.js',
    mochaOptions: {
      'ui': 'bdd',
      'reporter': 'spec'
    }
  }
};
