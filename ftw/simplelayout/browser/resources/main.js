(function(global, $) {
  "use strict";

  $(function() {

    var componentRequest = $.get("./addable-blocks.json"),
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

      saveState = function() {
        var config = simplelayout.getLayoutmanager().serialize();
        var saveRequest = $.post("./save_state", {"data": config});
        saveRequest.done(function(data) {
          global.console.log(data);
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
        $("#formDialog").load(formUrl, function() {
          var formDialog = $(this).dialog(dialogSettings);
          $("form", this).on("submit", function(event) {
            event.preventDefault();
            var saveButton = $("#form-buttons-save", this);
            //formData.push({ name: saveButton.attr("name"), value: saveButton.val() });
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


    });
  });

}(window, jQuery));
