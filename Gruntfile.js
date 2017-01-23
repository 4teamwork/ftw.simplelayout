module.exports = function(grunt) {

  "use strict";

  grunt.initConfig({

    pkg: grunt.file.readJSON("package.json"),

    browserify: {
      dev: {
        dest: "./ftw/simplelayout/browser/resources/<%= pkg.name %>.js",
        src: "./ftw/simplelayout/js/src/<%= pkg.name %>.js",
        options: {
          watch: true,
          keepAlive: true,
          browserifyOptions: {
            debug: true,
            standalone: "<%= pkg.name %>",
            paths: ["./ftw/simplelayout/js/src"],
            transform: [
              ["babelify", {
                presets: "es2015"
              }],
              "browserify-shim"
            ]
          }
        },
      },
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
    }
  });

  grunt.loadNpmTasks("grunt-browserify");
  grunt.loadNpmTasks("grunt-karma");

  grunt.registerTask("dev", ["browserify:dev"]);
  grunt.registerTask("dist", ["browserify:dist"]);
  grunt.registerTask("test", ["karma:dev"]);
  grunt.registerTask("test-ci", ["karma:ci"]);
  grunt.registerTask("default", ["dev"]);

};
