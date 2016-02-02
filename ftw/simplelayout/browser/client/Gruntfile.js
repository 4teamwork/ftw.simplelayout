module.exports = function(grunt) {

  "use strict";

  grunt.initConfig({

    config: {
      dev: {
        options: {
          variables: {
            "optimize": "none",
            "jsoutput": "dist/simplelayout.js"
          }
        }
      },
      prod: {
        options: {
          variables: {
            "optimize": "uglify",
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
          baseUrl: "web/js/lib",
          // Is being provided
          exclude: ["jquery", "jqueryui"],
          optimize: "<%= grunt.config.get('optimize') %>",
          mainConfigFile: "web/js/app.js",
          include: ["app", "almond/almond"],
          out: "<%= grunt.config.get('jsoutput') %>",
          wrap: {
            startFile: "web/build/start.frag.js",
            endFile: "web/build/end.frag.js"
          }
        }
      }
    },
    watch: {
      scripts: {
        files: ["web/js/app/**/*.js"],
        tasks: ["requirejs"],
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
  grunt.loadNpmTasks("grunt-contrib-watch");
  grunt.loadNpmTasks("grunt-shell");
  grunt.loadNpmTasks("grunt-http-server");
  grunt.loadNpmTasks("grunt-mocha-phantomjs");

  grunt.registerTask("default", ["browser-test"]);
  grunt.registerTask("test", ["http-server:test", "mocha_phantomjs"]);
  grunt.registerTask("browser-test", ["shell:test", "http-server:browserTest"]);
  grunt.registerTask("dev", ["config:dev", "requirejs", "watch"]);
  grunt.registerTask("serve", ["shell:serve", "http-server:serve"]);
  grunt.registerTask("lint", ["eslint"]);
  grunt.registerTask("prod", ["config:prod", "lint", "requirejs"]);

};
