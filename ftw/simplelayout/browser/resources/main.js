(function(global, $) {
  "use strict";

  $(function() {

    var instance = {
      settings: {
        addableBlocksEndpoint: "./sl-ajax-addable-blocks-view",
        saveStateEndpoint: "./sl-ajax-save-state-view",
        deleteBlockEndpoint: "./sl-ajax-delete-blocks-view",
        editBlockEndpoint: "./sl-ajax-edit-block-view",
        source: "#simplelayout",
        layouts: [1, 2, 4]
      },
      simplelayout: null,
      init: function(callback) {
        var self = this;
        this.loadComponents(function(components) {
          self.simplelayout = new global.Simplelayout({source: self.settings.source});
          var toolbox = new global.Toolbox({layouts: self.settings.layouts, components: components});
          toolbox.attachTo($("body"));
          self.simplelayout.attachToolbox(toolbox);
          self.simplelayout.getLayoutmanager().deserialize();
          callback(self.simplelayout);
        });

      },
      loadComponents: function(callback) {
        $.get(this.settings.addableBlocksEndpoint).done(callback);
      },
      saveState: function() {
        var config = this.simplelayout.getLayoutmanager().serialize();
        $.post(this.settings.saveStateEndpoint, {"data": config});
      },
      cleanup: function(block) {
        var currentBlockData = block.element.data();
        var layoutId = currentBlockData.layoutId;
        var columnId = currentBlockData.columnId;
        var blockId = currentBlockData.blockId;
        this.simplelayout.getLayoutmanager().deleteBlock(layoutId, columnId, blockId);
      },
      matchHeight: function() {
        $.fn.matchHeight._update();
      }
    };

    $.fn.matchHeight._maintainScroll = true;
    $(".sl-column").matchHeight();

    instance.init(function(simplelayout) {
      var addFormUrl;
      var currentBlock;
      var addOverlay = new global.FormOverlay();
      var deleteOverlay = new global.FormOverlay();
      var editOverlay = new global.FormOverlay();

      editOverlay.onSubmit(function(blockData) {
        var currentBlockData = simplelayout.getCurrentBlock().element.data();
        var layoutId = currentBlockData.layoutId;
        var columnId = currentBlockData.columnId;
        var blockId = currentBlockData.blockId;
        simplelayout.getLayoutmanager().getBlock(layoutId, columnId, blockId).content(blockData.content);
        instance.saveState();
        instance.matchHeight();
        this.close();
      });

      deleteOverlay.onSubmit(function() {
        var currentBlockData = simplelayout.getCurrentBlock().element.data();
        var layoutId = currentBlockData.layoutId;
        var columnId = currentBlockData.columnId;
        var blockId = currentBlockData.blockId;
        simplelayout.getLayoutmanager().deleteBlock(layoutId, columnId, blockId);
        instance.saveState();
        instance.matchHeight();
        this.close();
      });

      addOverlay.onSubmit(function(newBlockData) {
        currentBlock.element.data("uid", newBlockData.uid);
        currentBlock.content(newBlockData.content);
        instance.saveState();
        instance.matchHeight();
        this.close();
      });

      addOverlay.onCancel(function() {
        instance.cleanup();
      });

      simplelayout.getToolbox().element.find(".sl-toolbox-component").on("dragstart", function(e) {
        addFormUrl = $(e.target).data("form_url");
      });

      simplelayout.on("blockInserted", function(event, layoutId, columnId, blockId) {
        currentBlock = simplelayout.getLayoutmanager().getBlock(layoutId, columnId, blockId);
        instance.matchHeight();
      });

      simplelayout.on("blocksCommitted", function() {
        addOverlay.load(addFormUrl);
      });

      simplelayout.on("blockMoved", function() {
        instance.saveState();
        instance.matchHeight();
      });

      $(global.document).on("click", ".sl-block .delete", function(event) {
        event.preventDefault();
        var currentBlockUUID = simplelayout.getCurrentBlock().element.data().uid;
        var config = {"block": currentBlockUUID};
        deleteOverlay.load(instance.settings.deleteBlockEndpoint, {"data": JSON.stringify(config)});
      });

      $(global.document).on("click", ".sl-block .edit", function(event) {
        event.preventDefault();
        var currentBlockUUID = simplelayout.getCurrentBlock().element.data().uid;
        var config = {"block": currentBlockUUID};
        editOverlay.load(instance.settings.editBlockEndpoint, {"data": JSON.stringify(config)});
      });

      $(global.document).on("click", ".sl-layout .delete", function() {
        if(!simplelayout.getCurrentLayout().hasBlocks()) {
          simplelayout.getLayoutmanager().deleteLayout(simplelayout.getCurrentLayout().element.data("layoutId"));
          instance.saveState();
        }
      });

      $(global.document).on("click", ".server-action", function(event) {
        event.preventDefault();
        var payLoad = {};
        var action = $(this);
        var configRequest;
        payLoad.uid = simplelayout.getCurrentBlock().element.data("uid");
        $.extend(payLoad, action.data());
        configRequest = $.post(action.attr("href"), {"data": JSON.stringify(payLoad)});
        configRequest.done(function(blockContent) {
          simplelayout.getCurrentBlock().content(blockContent);
          instance.matchHeight();
        });
      });

    });

  });

}(window, jQuery));
