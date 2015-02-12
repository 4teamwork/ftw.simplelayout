(function(global, $) {
  "use strict";

  $(function() {

    var componentRequest = $.get("./sl-ajax-addable-blocks-view"),
      simplelayout,
      toolbox,
      block,
      formUrl,
      saveState = function() {
        var config = simplelayout.getLayoutmanager().serialize();
        var saveRequest = $.post("./sl-ajax-save-state-view", {
          "data": config
        });
        saveRequest.done(function(data) {
          global.console.log(data);
        });
        saveRequest.fail(function(data, textStatus) {
          global.console.error(textStatus);
        });
      },
      cleanBlock = function(event) {
        if(event.type !== "onBeforeClose") {
          var currentBlockData = block.element.data();
          var layoutId = currentBlockData.layoutId;
          var columnId = currentBlockData.columnId;
          var blockId = currentBlockData.blockId;
          simplelayout.getLayoutmanager().deleteBlock(layoutId, columnId, blockId);
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
      loadForm = function() {
        var overlay = this;
        $("form", this.getOverlay()).on("submit", function(event) {
          event.preventDefault();
          global.tinyMCE.triggerSave(true, true);
          var saveButton = $("#form-buttons-save", this);
          var formData = new global.FormData(this);
          formData.append(saveButton.attr("name"), saveButton.val());
          var addBlockRequest = $.ajax({
            type: "POST",
            url: this.action,
            data: formData,
            processData: false,
            contentType: false
          });
          addBlockRequest.done(function(newBlock) {
            block.element.data("uid", newBlock.uid);
            block.content(global.decodeURIComponent(global.escape(global.atob(newBlock.content))));
            overlay.close();
            saveState();
          });
        });
      },
      dialogSettings = {
        mask: {
          color: "#fff",
          loadSpeed: 200,
          opacity: 0.4
        },
        left: "center",
        fixed: true,
        closeOnClick: false,
        load: true,
        onBeforeClose: cleanBlock,
        onBeforeLoad: loadForm
        //onLoad: initializePloneComponents
      },
      updateDelete = function(config, callback) {
        var saveRequest = $.post("./sl-ajax-delete-blocks-view", {"data": JSON.stringify(config)});
        saveRequest.done(function(data) {
          if (callback) {
            callback.call(null, data);
          }
        });
        saveRequest.fail(function(data, textStatus) {
          global.console.error(textStatus);
        });
      };

    componentRequest.done(function(data) {
      simplelayout = new global.Simplelayout({
        source: "#simplelayout"
      });

      toolbox = new global.Toolbox({
        layouts: [1, 2, 4],
        components: data
      });

      toolbox.attachTo($("body"));
      simplelayout.attachToolbox(toolbox);
      simplelayout.getLayoutmanager().deserialize();

      simplelayout.getToolbox().element.find(".sl-toolbox-component").on("dragstart", function(e) {
        formUrl = $(e.target).data("form_url");
      });

      simplelayout.on("blockInserted", function(event, layoutId, columnId, blockId) {
        block = simplelayout.getLayoutmanager().getBlock(layoutId, columnId, blockId);
      });

      simplelayout.on("blocksCommitted", function() {
        $("#formOverlay").load(formUrl, function() {
          $(this).overlay(dialogSettings).load();
          initializePloneComponents(this);
        });
      });

      simplelayout.on("blockMoved", function() {
        saveState();
      });

      $(global.document).on("click", ".server-action", function(event) {
        event.preventDefault();
        var payLoad = {};
        var action = $(this);
        payLoad.uid = simplelayout.getCurrentBlock().element.data("uid");
        $.extend(payLoad, action.data());
        var configRequest = $.post(action.attr("href"), {"data": JSON.stringify(payLoad)});
        configRequest.done(function(blockContent) {
          simplelayout.getCurrentBlock().content(blockContent);
        });
        configRequest.fail(function(configFailData) {
          global.console.error(configFailData);
        });
      });

      $(global.document).on("click", ".remove", function() {
        var currentBlockData = simplelayout.getCurrentBlock().element.data();
        var layoutId = currentBlockData.layoutId;
        var columnId = currentBlockData.columnId;
        var blockId = currentBlockData.blockId;
        var currentUID = simplelayout.getLayoutmanager().getBlock(layoutId, columnId, blockId).element.data("uid");
        var blockUIDs = [];
        blockUIDs.push(currentUID);
        var config = {"blocks": blockUIDs};
        var confirmed;
        updateDelete(config, function(deleteData) {
          confirmed = global.confirm(JSON.parse(deleteData).msg);
          if (confirmed) {
            config.confirmed = confirmed;
            updateDelete(config, function() {
              simplelayout.getLayoutmanager().deleteBlock(layoutId, columnId, blockId);
              saveState();
            });
          }
        });
      });

    });
  });

}(window, jQuery));
