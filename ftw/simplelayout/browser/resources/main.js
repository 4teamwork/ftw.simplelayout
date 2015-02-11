(function(global, $) {
  "use strict";

  $(function() {

    var componentRequest = $.get("./sl-ajax-addable-blocks-view"),
      simplelayout,
      toolbox,
      block,
      formUrl,
      dialogSettings = {
        modal: true,
        width: "auto",
        resizable: false,
        draggable: false
      },

      initializePloneComponents = function(form) {
        if($.fn.ploneTabInit) {
          $(form).parent().ploneTabInit();
        }
        if (global.window.initTinyMCE) {
          global.window.initTinyMCE(form);
        }
      },

      saveState = function() {
        var config = simplelayout.getLayoutmanager().serialize();
        var saveRequest = $.post("./sl-ajax-save-state-view", {"data": config});
        saveRequest.done(function(data) {
          global.console.log(data);
        });
        saveRequest.fail(function(data, textStatus) {
          global.console.error(textStatus);
        });
      },

      updateDelete = function(config, callback) {
        var saveRequest = $.post("./sl-ajax-delete-blocks-view", {"data": JSON.stringify(config)});
        saveRequest.done(function(data) {
          callback.call(null, data);
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
        var formDialog;
        $("#formDialog").load(formUrl, function() {
          formDialog = $(this).dialog(dialogSettings);
          initializePloneComponents(this);
          $("form", this).on("submit", function(event) {
            event.preventDefault();
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
              formDialog.dialog("close");
              saveState();
            });
          });
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
        updateDelete(config, function(msg) {
          confirmed = global.confirm(msg);
          if(confirmed) {
            config.confirmed = confirmed;
            updateDelete(config);
          }
        });
      });

      // simplelayout.on("blockDeleted", function(event, layoutId, columnId, blockId) {

      //   if(currentUID) {
      //     var blockUIDs = [];
      //     blockUIDs.push(currentUID);
      //     var config = {"blocks": blockUIDs, "confirmed": true};

      //   }
      // });

    });
  });

}(window, jQuery));
