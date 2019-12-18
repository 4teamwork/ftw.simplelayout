module.exports = function(grunt) {

  "use strict";

  grunt.initConfig({

    pkg: grunt.file.readJSON("package.json"),

    browserify: {
      dist: {
        dest: "./ftw/simplelayout/browser/resources/<%= pkg.name %>.js",
        src: "./ftw/simplelayout/js/src/<%= pkg.name %>.js",
        options: {
          browserifyOptions: {
            standalone: "<%= pkg.name %>",
            paths: ["./ftw/simplelayout/js/src"],
            transform: [
              ["babelify", {
                presets: "es2015"
              }],
              "browserify-shim"
            ]
          }
        }
      }
    },

    requirejs: {
      compile: {
        options: {
          baseUrl: "./ftw/simplelayout/browser/resources",
           paths: {
             jquery: "empty:",
             simplelayout_main: "main",
           },
           name: "bundle",
           out: "./ftw/simplelayout/browser/resources/simplelayout-compiled.js",
           preserveLicenseComments: false,
           // Uncomment the line below for JS development
           // optimize: "none",
        },
      },
    },

    karma: {
      options: {
        configFile: "karma.conf.js"
      },
      dev: {
        browsers: ["PhantomJS"]
      },
      ci: {
        browsers: ["PhantomJS"],
        autoWatch: false,
        singleRun: true
      }
    },

    watch: {
      scripts: {
        files: [
          "./ftw/simplelayout/js/src/**/*.js",
          "./ftw/simplelayout/js/src/*.js",
          "./ftw/simplelayout/browser/resources/*.js",
          "!./ftw/simplelayout/browser/resources/simplelayout-compiled.js",
          "!./ftw/simplelayout/browser/resources/ftw.simplelayout.js",
        ],
        tasks: ["browserify", "requirejs" ]
      }
    }
  });

  grunt.loadNpmTasks("grunt-browserify");
  grunt.loadNpmTasks("grunt-karma");
  grunt.loadNpmTasks("grunt-contrib-watch");
  grunt.loadNpmTasks("grunt-contrib-requirejs");

  grunt.registerTask("default", ["watch"]);
  grunt.registerTask("build", ["browserify", "requirejs"]);
  grunt.registerTask("test", ["karma:dev"]);
  grunt.registerTask("test-ci", ["karma:ci"]);
};
