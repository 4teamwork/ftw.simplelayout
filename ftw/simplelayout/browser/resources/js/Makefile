
GRUNT = ./node_modules/grunt-cli/bin/grunt
BOWER = ./node_modules/bower/bin/bower
NODE_PATH = ./node_modules

bootstrap-common:
	mkdir -p build

bootstrap: clean bootstrap-common
	npm link --prefix=$(NODE_PATH)

clean:
	mkdir -p build
	rm -rf build
	rm -rf node_modules
	rm -rf bower_components