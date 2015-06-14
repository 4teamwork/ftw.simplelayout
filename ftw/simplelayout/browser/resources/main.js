(function(global, $) {
  "use strict";

  $(function() {

    var instance = {
      settings: {
        addableBlocksEndpoint: "./sl-ajax-addable-blocks-view",
        saveStateEndpoint: "./sl-ajax-save-state-view",
        source: ".sl-simplelayout",
        layouts: [1, 2, 4],
        canChangeLayouts: false,
        canEdit: false
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

        if (!this.settings.canEdit) {
          return;
        }

        this.loadComponents(function(components) {
          var toolbox = new global.Toolbox({layouts: self.settings.layouts, components: components});
          self.simplelayout = new global.Simplelayout({source: self.settings.source, toolbox: toolbox});
          toolbox.attachTo($("body"));
          self.simplelayout.deserialize($("#content-core"));
          callback(self.simplelayout);
        });

      },
      loadComponents: function(callback) {
        $.get(this.settings.addableBlocksEndpoint).done(function(data, textStatus, request) {
          var contentType = request.getResponseHeader("Content-Type");
          if(contentType.indexOf("application/json") < 0) {
            throw new Error("Bad response [content-type: " + contentType + "]");
          }
          callback(data);
        });
      },
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
        $.post(this.settings.saveStateEndpoint, { 
          data: JSON.stringify(state),
          _authenticator: $('input[name="_authenticator"]').val()
        });
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
      var activeBlockElement;
      var addOverlay = new global.FormOverlay();
      var deleteOverlay = new global.FormOverlay();
      var editOverlay = new global.FormOverlay();
      var uploadOverlay = new global.FormOverlay();

      if (!instance.settings.canChangeLayouts){
        $(simplelayout.options.source).sortable("disable");
      }

      editOverlay.onSubmit(function(blockData) {
        var activeBlockData = activeBlockElement.data();
        var activeBlock = simplelayout.getManagers()[activeBlockData.container].getBlock(activeBlockData.layoutId, activeBlockData.columnId, activeBlockData.blockId);
        activeBlock.content(blockData.content);
        instance.saveState();
        this.close();
      });

      deleteOverlay.onSubmit(function() {
        var activeBlockData = activeBlockElement.data();
        var managerId = activeBlockData.container;
        var layoutId = activeBlockData.layoutId;
        var columnId = activeBlockData.columnId;
        var blockId = activeBlockData.blockId;
        simplelayout.getManagers()[managerId].deleteBlock(layoutId, columnId, blockId);
        instance.saveState();
        this.close();
      });

      addOverlay.onSubmit(function(newBlockData) {
        currentBlock.element.data("uid", newBlockData.uid);
        currentBlock.element.data("url", newBlockData.url);
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
        activeBlockElement = $(this).parents(".sl-block");
        var config = {"block": activeBlockElement.data("uid")};
        deleteOverlay.load($(this).attr("href"), {"data": JSON.stringify(config)});
      });

      $(global.document).on("click", ".sl-block .edit", function(event) {
        event.preventDefault();
        activeBlockElement = $(this).parents(".sl-block");
        var config = {"block": activeBlockElement.data("uid")};
        editOverlay.load($(this).attr("href"), {"data": JSON.stringify(config)});
      });

      $(global.document).on("click", ".sl-layout .delete", function() {
        var data = $(this).parents(".sl-layout").data();
        var layout = simplelayout.getManagers()[data.container].layouts[data.layoutId];
        if(!layout.hasBlocks()) {
          var managerId = layout.element.data().container;
          simplelayout.getManagers()[managerId].deleteLayout(layout.element.data("layoutId"));
          instance.saveState();
        }
      });

      $(global.document).on("click", ".sl-block .redirect", function(event) {
        event.preventDefault();
        activeBlockElement = $(this).parents(".sl-block");
        window.location.href = activeBlockElement.data("url") + $(this).attr("href");
      });

      $(global.document).on("click", ".sl-block .upload", function(event) {
        event.preventDefault();
        activeBlockElement = $(this).parents(".sl-block");
        var config = {"block": activeBlockElement.data("uid")};
        uploadOverlay.load($(this).attr("href"),{"data": JSON.stringify(config)}, function(){
          var self = this;

          Browser.onUploadComplete = function(){ return; };

          self.element.on("click", "#button-upload-done", function(event) {
            event.preventDefault();
            self.onFormCancel.call(self);
          });

        });

        uploadOverlay.onCancel(function(){
          var payLoad = {};
          var action = $(this);
          var configRequest;
          payLoad.uid = activeBlockElement.data("uid");
          $.extend(payLoad, action.data());
          configRequest = $.post('./sl-ajax-reload-block-view', {"data": JSON.stringify(payLoad)});
          configRequest.done(function(blockContent) {
            var data = activeBlockElement.data();
            var manager = simplelayout.getManagers()[data.container];
            var block = manager.getBlock(data.layoutId, data.columnId, data.blockId);
            block.content(blockContent);
          });
        });
      });

      $(global.document).on("click", ".server-action", function(event) {
        event.preventDefault();
        var payLoad = {};
        var action = $(this);
        var configRequest;
        activeBlockElement = $(this).parents(".sl-block");
        payLoad.uid = activeBlockElement.data("uid");
        var data = activeBlockElement.data();
        var manager = simplelayout.getManagers()[data.container];
        var block = manager.getBlock(data.layoutId, data.columnId, data.blockId);
        $.extend(payLoad, action.data());
        configRequest = $.post(action.attr("href"), {"data": JSON.stringify(payLoad)});
        configRequest.done(function(blockContent) {
          block.content(blockContent);
        });
      });

    });

  });

}(window, jQuery));
