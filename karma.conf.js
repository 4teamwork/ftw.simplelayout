"use strict";

module.exports = function(karma) {
  karma.set({

    frameworks: [ "jasmine", "browserify", "chai", "fixture" ],

    files: [
      { pattern: "./ftw/simplelayout/js/test/setup.js", watched: false, included: true },
      { pattern: "./ftw/simplelayout/js/test/**/*.js", watched: false, included: true },
      { pattern: "./ftw/simplelayout/js/test/fixtures/**/*.html" }
    ],

    reporters: [ "dots" ],

    colors: true,

    preprocessors: {
      "./ftw/simplelayout/js/test/**/*.js": "browserify",
      "./ftw/simplelayout/js/test/fixtures/**/*.html": "html2js"
    },

    browserify: {
      debug: true,
      paths: ["./ftw/simplelayout/js/src"],
      transform: [ ["babelify", { presets: ["es2015"] }] ]
    },

    browsers: [ "PhantomJS" ],

    singleRun: false,
    autoWatch: true
  });

};
