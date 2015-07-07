module.exports = function(grunt) {

  "use strict";

  grunt.initConfig({

    config: {
      dev: {
        options: {
          variables: {
            "optimize": "none",
            "sass-style": "expanded",
            "sourcemap": "inline",
            "cssoutput": "dist/simplelayout.css",
            "jsoutput": "dist/simplelayout.js"
          }
        }
      },
      prod: {
        options: {
          variables: {
            "optimize": "uglify",
            "sass-style": "compressed",
            "sourcemap": "none",
            "cssoutput": "dist/simplelayout.min.css",
            "jsoutput": "dist/simplelayout.min.js"
          }
        }
      }
    },
    "mocha_phantomjs": {
      all: {
      options: {
        urls: ["http://localhost:8282/test/test.html"]
        }
      }
    },
    requirejs: {
      compile: {
        options: {
          almond: true,
          name: "almond/almond",
          baseUrl: "web/js/lib",
          // Is being provided
          exclude: ["jquery", "jqueryui"],
          optimize: "<%= grunt.config.get('optimize') %>",
          mainConfigFile: "web/js/app.js",
          include: ["app", "jsrender"],
          out: "<%= grunt.config.get('jsoutput') %>",
          wrap: true
        }
      }
    },
    sass: {
      dist: {
        options: {
          style: "<%= grunt.config.get('sass-style') %>",
          sourcemap: "<%= grunt.config.get('sourcemap') %>"
        },
        files: {
          "<%= grunt.config.get('cssoutput') %>": "web/styles/scss/main.scss"
        }
      }
    },
    watch: {
      scripts: {
        files: ["web/styles/scss/**/*.scss", "web/js/app/**/*.js"],
        tasks: ["sass", "requirejs"],
        options: {
          spawn: false
        }
      }
    },
    eslint: {
      target: ["Gruntfile.js", "test/**/*.js", "web/js/*.js", "web/js/app/**/*.js"]
    },
    shell: {
      serve: {
        command: "open http://localhost:8000/web/app.html"
      },
      test: {
        command: "open http://localhost:8282/test/test.html"
      }
    },
    "http-server": {
      serve: {
        port: 8000,
        host: "localhost"
      },
      browserTest: {
        port: 8282,
        host: "localhost"
      },
      test: {
        port: 8282,
        host: "localhost",
        runInBackground: true,
        logFn: function() {}
      }
    }
  });

  grunt.loadNpmTasks("grunt-config");
  grunt.loadNpmTasks("grunt-eslint");
  grunt.loadNpmTasks("grunt-contrib-requirejs");
  grunt.loadNpmTasks("grunt-contrib-sass");
  grunt.loadNpmTasks("grunt-contrib-watch");
  grunt.loadNpmTasks("grunt-shell");
  grunt.loadNpmTasks("grunt-http-server");
  grunt.loadNpmTasks("grunt-mocha-phantomjs");

  grunt.registerTask("default", ["browser-test"]);
  grunt.registerTask("test", ["http-server:test", "mocha_phantomjs"]);
  grunt.registerTask("browser-test", ["shell:test", "http-server:browserTest"]);
  grunt.registerTask("dev", ["config:dev", "sass", "requirejs", "watch"]);
  grunt.registerTask("serve", ["shell:serve", "http-server:serve"]);
  grunt.registerTask("lint", ["eslint"]);
  grunt.registerTask("prod", ["config:prod", "lint", "requirejs", "sass"]);

};
