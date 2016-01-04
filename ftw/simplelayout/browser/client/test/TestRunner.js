(function() {

  "use strict";

  require.config({
    baseUrl: "../test/",
    paths: {
      "jquery": "../web/js/lib/jquery/dist/jquery",
      "jqueryui": "../web/js/lib/jquery-ui/ui/minified/jquery-ui.custom.min",
      "jsrender": "../web/js/lib/jsrender/jsrender",
      "mocha": "../web/js/lib/mocha/mocha",
      "chai": "../web/js/lib/chai/chai",
      "fixtures": "/web/js/lib/fixtures/fixtures",
      "jquery-path": "/web/js/lib/jquery-path/jquery.path",
      "EventEmitter": "/web/js/lib/eventEmitter/EventEmitter",
      "app": "../web/js/app"
    },
    "shim": {
      "jsrender": {
        "deps": ["jquery"],
        "exports": "jQuery.fn.template"
      },
      "jqueryui": {
        "deps": ["jquery"]
      },
      "mocha": {
        "exports": "mocha"
      }
    }
  });

  define(["chai", "fixtures", "mocha", "jquery", "jqueryui", "jsrender"], function(chai, fix) {
    chai = require("chai");
    chai.config.truncateThreshold = 0;
    assert = chai.assert;
    fixtures = fix;
    fixtures.path = "fixtures";
    mocha.setup("tdd");
    require([
      "block.test",
      "layout.test",
      "layoutmanager.test",
      "simplelayout.test",
      "toolbar.test",
      "toolbox.test",
      "idHelper.test",
      "element.test",
      "transactional.test",
      "integration.test"
    ], function() {
      if(window.mochaPhantomJS){
        mochaPhantomJS.run();
      }
      else{
        mocha.run();
      }
    });
  });
})();
