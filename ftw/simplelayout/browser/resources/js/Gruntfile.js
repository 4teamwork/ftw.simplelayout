module.exports = function(grunt) {
    grunt.initConfig({

        pkg: grunt.file.readJSON('package.json'),

        watch: {
            js: {
                options: {
                    spawn: true,
                    interrupt: true,
                    debounceDelay: 250,
                },
                files: ['Gruntfile.js', './*.js', 'tests/*.js'],
                tasks: ['mocha']
            }
        },

        mocha: {
            test: {
                src: ['tests/testrunner.html'],
                options: {
                    reporter: 'Progress',
                },
            },
            // all: {
            //     src: ['tests/testrunner.html']
            // },
            options: {
                run: true,
            }
        },
        uglify: {
            options: {
                banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
            },
            build: {
                src: './<%= pkg.name %>.js',
                dest: 'build/<%= pkg.name %>.min.js'
            }
        }
    });

    grunt.loadNpmTasks('grunt-mocha');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-uglify');

    grunt.registerTask('default', ['mocha']);
};