require.config({
  "baseUrl": "js/lib/",
  "paths": {
    "app": "../app",
    "EventEmitter": "eventEmitter/EventEmitter.min",
    "jquery": "jquery/dist/jquery",
    "jqueryui": "jquery-ui/ui/minified/jquery-ui.custom.min",
    "jsrender": "jsrender/jsrender.min"
  },
  "shim": {
    "jsrender": {
      "deps": ["jquery"],
      "exports": "jQuery.fn.template"
    },
    "jqueryui": {
      "deps": ["jquery"]
    }
  }
});

require(["app/simplelayout/Simplelayout", "app/toolbox/Toolbox", "app/simplelayout/EventEmitter", "jsrender", "jquery", "jqueryui"], function(Simplelayout, Toolbox) {

  "use strict";

  $(document).ready(function() {
    var toolbox = new Toolbox({
      layouts: [1, 2, 4],
      blocks: [
        {
          title: "Listingblock",
          description: "can list things",
          contentType: "listingblock",
          formUrl: "http://www.google.com",
          actions: {
            edit: {
              class: "edit",
              description: "Edit this block"
            }
          }
        },
        {
          title: "Textblock",
          description: "can show text",
          contentType: "textblock",
          formUrl: "http://www.bing.com",
          actions: {
            edit: {
              class: "edit",
              description: "Edit this block"
            },
            move: {
              class: "move",
              description: "Move this block"
            }
          }
        }
      ],
      labels: {
        labelColumnPostfix: " - Columns"
      }
    });

    toolbox.attachTo($("body"));
    var simplelayout = new Simplelayout({
      toolbox: toolbox
    });
    window.simplelayout = simplelayout;
    simplelayout.restore();
  });

});
