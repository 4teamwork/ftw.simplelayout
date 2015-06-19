(function(global, $) {
  "use strict";

  $(function() {

    var instance = {
      settings: {
        addableBlocksEndpoint: "./sl-ajax-addable-blocks-view",
        saveStateEndpoint: "./sl-ajax-save-state-view",
        source: ".sl-simplelayout",
        layouts: [1, 2, 4],
        canChangeLayouts: false
      },
      simplelayout: null,
      init: function(callback) {
        var self = this;
        var source = $(this.settings.source);
        if (source.length === 0){
          return;
        }
        var settings = source.data("slSettings") || {};
        this.settings = $.extend(this.settings, settings);
        this.loadComponents(function(components) {
          var toolbox = new global.Toolbox({layouts: self.settings.layouts, components: components});
          self.simplelayout = new global.Simplelayout({source: self.settings.source, toolbox: toolbox});
          toolbox.attachTo($("body"));
          self.simplelayout.deserialize($("#content-core"));
          callback(self.simplelayout);
        });

      },
      loadComponents: function(callback) { $.get(this.settings.addableBlocksEndpoint).done(callback); },
      saveState: function() {
        var state = {};
        $(".sl-simplelayout").each(function(manIdx, manager) {
          state[manager.id] = [];
          $(".sl-layout", manager).each(function(layIdx, layout) {
            state[manager.id][layIdx] = {};
            state[manager.id][layIdx].cols = [];
            $(".sl-column", layout).each(function(colIdx, column) {
              state[manager.id][layIdx].cols[colIdx] = { blocks: [] };
              $(".sl-block", column).each(function(bloIdx, block) {
                state[manager.id][layIdx].cols[colIdx].blocks[bloIdx] = { uid: $(block).data("uid") };
              });
            });
          });
        });
        $.post(this.settings.saveStateEndpoint, { data: JSON.stringify(state) });
      },
      cleanup: function() {
        var blocks = this.simplelayout.getInsertedBlocks();
        var self = this;
        $.each(blocks, function(idx, block) {
          var data = block.element.data();
          var managerId = data.container;
          var layoutId = data.layoutId;
          var columnId = data.columnId;
          var blockId = data.blockId;
          self.simplelayout.getManagers()[managerId].deleteBlock(layoutId, columnId, blockId);
        });
      }
    };

    instance.init(function(simplelayout) {
      var addFormUrl;
      var currentBlock;
      var addOverlay = new global.FormOverlay();
      var deleteOverlay = new global.FormOverlay();
      var editOverlay = new global.FormOverlay();

      if (!instance.settings.canChangeLayouts){
        $(simplelayout.options.source).sortable("disable");
      }

      editOverlay.onSubmit(function(blockData) {
        simplelayout.getActiveBlock().content(blockData.content);
        instance.saveState();
        this.close();
      });

      deleteOverlay.onSubmit(function() {
        var currentBlockData = simplelayout.getActiveBlock().element.data();
        var managerId = currentBlockData.container;
        var layoutId = currentBlockData.layoutId;
        var columnId = currentBlockData.columnId;
        var blockId = currentBlockData.blockId;
        simplelayout.getManagers()[managerId].deleteBlock(layoutId, columnId, blockId);
        instance.saveState();
        this.close();
      });

      addOverlay.onSubmit(function(newBlockData) {
        currentBlock.element.data("uid", newBlockData.uid);
        currentBlock.content(newBlockData.content);
        currentBlock.commit();
        instance.saveState();
        this.close();
      });

      addOverlay.onCancel(function() {
        instance.cleanup();
      });

      simplelayout.options.toolbox.element.find(".sl-toolbox-component").on("dragstart", function(e) {
        addFormUrl = $(e.target).data("form_url");
      });

      simplelayout.on("blockInserted", function(block) {
        currentBlock = block;
        addOverlay.load(addFormUrl);
      });

      simplelayout.on("blockMoved", function() { instance.saveState(); });

      simplelayout.on("layoutMoved", function() { instance.saveState(); });

      simplelayout.on("layoutInserted", function(layout) {
        layout.commit();
        simplelayout.options.toolbox.enableComponents();
      });

      simplelayout.on("layoutDeleted", function(layout) {
        if(!simplelayout.getManagers()[layout.element.data("container")].hasLayouts()) {
          simplelayout.options.toolbox.disableComponents();
        }
      });

      $(global.document).on("click", ".sl-block .delete", function(event) {
        event.preventDefault();
        var currentBlockUUID = simplelayout.getActiveBlock().element.data().uid;
        var config = {"block": currentBlockUUID};
        deleteOverlay.load($(this).attr("href"), {"data": JSON.stringify(config)});
      });

      $(global.document).on("click", ".sl-block .edit", function(event) {
        event.preventDefault();
        var currentBlockUUID = simplelayout.getActiveBlock().element.data().uid;
        var config = {"block": currentBlockUUID};
        editOverlay.load($(this).attr("href"), {"data": JSON.stringify(config)});
      });

      $(global.document).on("click", ".sl-layout .delete", function() {
        var activeLayout = simplelayout.getActiveLayout();
        if(!activeLayout.hasBlocks()) {
          var managerId = activeLayout.element.data().container;
          simplelayout.getManagers()[managerId].deleteLayout(simplelayout.getActiveLayout().element.data("layoutId"));
          instance.saveState();
        }
      });

      $(global.document).on("click", ".server-action", function(event) {
        event.preventDefault();
        var payLoad = {};
        var action = $(this);
        var configRequest;
        payLoad.uid = simplelayout.getActiveBlock().element.data("uid");
        $.extend(payLoad, action.data());
        configRequest = $.post(action.attr("href"), {"data": JSON.stringify(payLoad)});
        configRequest.done(function(blockContent) {
          simplelayout.getActiveBlock().content(blockContent);
        });
      });

    });

  });

}(window, jQuery));
