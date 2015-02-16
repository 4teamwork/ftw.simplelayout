(function(global, $) {
  "use strict";

  $(function() {

    var addableBlocksEndpoint = "./sl-ajax-addable-blocks-view",
      saveStateEndpoint = "./sl-ajax-save-state-view",
      deleteBlockEndpoint = "./sl-ajax-delete-blocks-view",
      componentRequest = $.get(addableBlocksEndpoint),
      simplelayout,
      toolbox,
      currentBlock,
      formOverlay = $("#formOverlay"),
      formUrl,
      deleteOverlay,
      blockSaved = false,
      saveState = function() {
        var config = simplelayout.getLayoutmanager().serialize();
        var saveRequest = $.post(saveStateEndpoint, {"data": config});
        saveRequest.done(function() {/*:Wip*/});
        saveRequest.fail(function() {/*:Wip*/});
      },
      cleanBlock = function() {
        if(!blockSaved) {
          var currentBlockData = currentBlock.element.data();
          var layoutId = currentBlockData.layoutId;
          var columnId = currentBlockData.columnId;
          var blockId = currentBlockData.blockId;
          simplelayout.getLayoutmanager().deleteBlock(layoutId, columnId, blockId);
          blockSaved = false;
        }
      },
      initializePloneComponents = function(form) {
        if ($.fn.ploneTabInit) {
          $(form).ploneTabInit();
        }
        if (global.initTinyMCE) {
          global.initTinyMCE(form);
        }
      },
      loadAddForm = function() {
        var overlay = this;
        $("#form-buttons-cancel", overlay.getOverlay()).on("click", function(event) {
          event.preventDefault();
          overlay.close();
        });
        $("form", overlay.getOverlay()).on("submit", function(event) {
          event.preventDefault();
          global.tinyMCE.triggerSave(true, true);
          var formData = new global.FormData(this),
            addBlockRequest;
          addBlockRequest = $.ajax({
            type: "POST",
            url: this.action,
            data: formData,
            processData: false,
            contentType: false
          });
          addBlockRequest.done(function(newBlockResponse) {
            currentBlock.element.data("uid", newBlockResponse.uid);
            currentBlock.content(global.decodeURIComponent(global.escape(global.atob(newBlockResponse.content))));
            blockSaved = true;
            overlay.close();
            saveState();
          });
          addBlockRequest.fail(function() {/*:Wip*/});
        });
      },
      deleteOverlaySettings = {
        mask: {color: "#fff", loadSpeed: 200, opacity: 0.4},
        left: "center",
        fixed: true,
        closeOnClick: false,
        load: true
      },
      loadDeleteForm = function(config, callback) {
        formOverlay.load(deleteBlockEndpoint, {"data": JSON.stringify(config)}, function() {
          deleteOverlay = formOverlay.overlay(deleteOverlaySettings).load();
          var formElement = $("form", formOverlay),
            formData = formElement.serialize();
          $("#form-buttons-cancel", formOverlay).on("click", function(cancelEvent) {
            cancelEvent.preventDefault();
            formOverlay.overlay().close();
          });
          $(formElement).on("submit", function(submitEvent) {
            submitEvent.preventDefault();
            var deleteBlockRequest = $.post(this.action,  formData);
            deleteBlockRequest.done(function(data) {
              if(callback) {
                callback.call(this, data);
              }
            });
            deleteBlockRequest.fail(function() {/*:Wip*/});
          });
        });
      },
      addOverlaySettings = {
        mask: {color: "#fff", loadSpeed: 200, opacity: 0.4},
        left: "center",
        fixed: true,
        closeOnClick: false,
        load: true,
        onBeforeClose: cleanBlock,
        onBeforeLoad: loadAddForm
      };

    componentRequest.done(function(components) {
      simplelayout = new global.Simplelayout({source: "#simplelayout"});

      toolbox = new global.Toolbox({layouts: [1, 2, 4], components: components});

      toolbox.attachTo($("body"));
      simplelayout.attachToolbox(toolbox);
      simplelayout.getLayoutmanager().deserialize();
      $(".sl-column").matchHeight();
      $.fn.matchHeight._maintainScroll = true;

      simplelayout.getToolbox().element.find(".sl-toolbox-component").on("dragstart", function(e) {
        formUrl = $(e.target).data("form_url");
      });

      simplelayout.on("blockInserted", function(event, layoutId, columnId, blockId) {
        currentBlock = simplelayout.getLayoutmanager().getBlock(layoutId, columnId, blockId);
        $.fn.matchHeight._update();
      });

      simplelayout.on("blocksCommitted", function() {
        formOverlay.load(formUrl, function() {
          $(this).overlay(addOverlaySettings).load();
          initializePloneComponents(this);
        });
      });

      simplelayout.on("blockMoved", function() {
        saveState();
        $.fn.matchHeight._update();
      });

      $(global.document).on("click", ".server-action", function(event) {
        event.preventDefault();
        var payLoad = {},
          action = $(this),
          configRequest;
        payLoad.uid = simplelayout.getCurrentBlock().element.data("uid");
        $.extend(payLoad, action.data());
        configRequest = $.post(action.attr("href"), {"data": JSON.stringify(payLoad)});
        configRequest.done(function(blockContent) {
          simplelayout.getCurrentBlock().content(blockContent);
          $.fn.matchHeight._update();
        });
        configRequest.fail(function() {/*:Wip*/});
      });

      $(global.document).on("click", ".sl-layout .delete", function() {
        var hasBlocks = false;
        $.each(simplelayout.getCurrentLayout().columns, function(columnIdx, column) {
          if(Object.keys(column.blocks).length > 0) {
            hasBlocks = true;
            return false;
          }
        });
        if(!hasBlocks) {
          simplelayout.getLayoutmanager().deleteLayout(simplelayout.getCurrentLayout().element.data("layoutId"));
          saveState();
        }
      });

      $(global.document).on("click", ".sl-block .delete", function(event) {
        event.preventDefault();
        var currentBlockData = simplelayout.getCurrentBlock().element.data(),
          layoutId = currentBlockData.layoutId,
          columnId = currentBlockData.columnId,
          blockId = currentBlockData.blockId,
          currentUID = simplelayout.getLayoutmanager().getBlock(layoutId, columnId, blockId).element.data("uid"),
          blockUIDs = [],
          config;
        blockUIDs.push(currentUID);
        config = {"blocks": blockUIDs};
        loadDeleteForm(config, function(data) {
          if(data !== "") {
            loadDeleteForm();
          } else {
            deleteOverlay.overlay().close();
            simplelayout.getLayoutmanager().deleteBlock(layoutId, columnId, blockId);
            saveState();
            $.fn.matchHeight_update();
          }
        });
      });

    });
  });

}(window, jQuery));
