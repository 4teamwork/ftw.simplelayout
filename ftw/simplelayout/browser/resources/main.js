(function(global, $) {
  "use strict";

  $(function() {

      var componentRequest = $.get("./addable-blocks.json"),
      simplelayout,
      block,
      dummyAnchor,
      formUrl,
      blockPosted = false,

      saveState = function(config) {
        var saveRequest = $.post("./save_state", config);
        saveRequest.done(function(data) {
          block.element.data("uid", data.uid);
        });
        saveRequest.fail(function(data, textStatus) {
          console.log(textStatus);
        });
      },

      createOverlay = function(target) {
        dummyAnchor = $("<a>").attr("href", target);
        dummyAnchor.prepOverlay({
          subtype: "ajax",
          formselector: "form",
          noform: function(data) {
            var uid = $(".sl-block-content", data).data("uid");
            block.uid = uid;
            block.content($(".sl-block-content", data).html());
            return "close";
          },
          afterpost: function() {
            blockPosted = true;
            saveState(simplelayout.getLayoutmanager().serialize());
          },
          closeselector: "[name='form.buttons.cancel']",
          config: {
            onLoad: function() {
              if (global.initTinyMCE) {
                global.initTinyMCE(global.document);
              }
            },
            onClose: function() {
              if (!blockPosted) {
                var layoutId = block.element.data("layoutId");
                var columnId = block.element.data("columnId");
                var blockId = block.element.data("blockId");
                simplelayout.getLayoutmanager().deleteBlock(layoutId, columnId, blockId);
              }
              blockPosted = false;
            }

          }
        });
      };

    componentRequest.done(function(data) {
      simplelayout = new global.Simplelayout({
        source: "#simplelayout"
      });

      var toolbox = new global.Toolbox({
        layouts: [1, 2, 4],
        components: data
      });

      toolbox.attachTo($("body"));
      simplelayout.attachToolbox(toolbox);
      simplelayout.getLayoutmanager().deserialize();

      simplelayout.getToolbox().element.find(".sl-toolbox-component").on("dragstart", function(e) {
        formUrl = $(e.target).data("form_url");
      });

      simplelayout.getLayoutmanager().element.on("blockInserted", function(event, layoutId, columnId, blockId) {
        block = simplelayout.getLayoutmanager().getBlock(layoutId, columnId, blockId);
      });

      simplelayout.getLayoutmanager().element.on("blocksCommitted", function() {
        createOverlay(formUrl);
        dummyAnchor.trigger("click");
      });
    });

    componentRequest.fail(function(textStatus) {
      console.error(textStatus);
    });
  });

}(window, jQuery));
