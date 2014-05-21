
GRUNT = ./node_modules/grunt-cli/bin/grunt
NODE_PATH = ./node_modules

bootstrap: clean
	mkdir build
	npm  link --prefix=$(NODE_PATH)
	GRUNT

test:
	GRUNT

watch:
	GRUNT watch

clean:
	rm -rf build
	rm -rf node_modules