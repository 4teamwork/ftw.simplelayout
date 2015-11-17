define([
  "app/simplelayout/Layoutmanager",
  "app/simplelayout/Toolbar",
  "app/toolbox/Toolbox",
  "app/simplelayout/EventEmitter"
  ],
  function(
    Layoutmanager,
    Toolbar,
    Toolbox,
    EventEmitter) {

  "use strict";

  var Simplelayout = function(options) {

    if (!(this instanceof Simplelayout)) {
      throw new TypeError("Simplelayout constructor cannot be called as a function.");
    }

    var root = $(":root");

    var self = this;

    this.options = $.extend({
      toolbox: new Toolbox()
    }, options || {});

    this.managers = {};

    this.insertManager = function() {
      var manager = new Layoutmanager();
      this.managers[manager.id] = manager;
      return manager;
    };

    this.moveLayout = function(layout, target) {
      var source = layout.parent;
      source.deleteLayout(layout.id);
      target.layouts[layout.id] = layout;
      EventEmitter.trigger("layoutMoved", [layout]);
      return this;
    };

    this.getCommittedBlocks = function() {
      return $.map(this.managers, function(manager) {
        return manager.getCommittedBlocks();
      });
    };

    this.getInsertedBlocks = function() {
      return $.map(this.managers, function(manager) {
        return manager.getInsertedBlocks();
      });
    };

    this.disableFrames = function() {
      $.each(this.getCommittedBlocks(), function(idx, block) {
        block.disableFrame();
      });
      return this;
    };

    this.enableFrames = function() {
      $.each(this.getCommittedBlocks(), function(idx, block) {
        block.enableFrame();
      });
      return this;
    };

    this.on = function(eventType, callback) {
      EventEmitter.on(eventType, callback);
      return this;
    };

    this.serialize = function() { return JSON.stringify(this.managers); };

    this.restore = function(source) {
      $(".sl-simplelayout", source).each(function() {
        self.insertManager().restore(this, $(this).attr("id"));
      });
      return this;
    };

    var sortableHelper = function() { return $('<div class="draggableHelper"><div>'); };

    var TOOLBOX_COMPONENT_DRAGGABLE_SETTINGS = {
      helper: "clone",
      cursor: "pointer",
      start: function() {
        self.enableFrames();
        if($(this).hasClass("sl-toolbox-block")) {
          root.addClass("sl-block-dragging");
        } else {
          root.addClass("sl-layout-dragging");
        }
      },
      stop: function() {
        self.disableFrames();
        root.removeClass("sl-block-dragging sl-layout-dragging");
      }
    };

    var LAYOUT_SORTABLE = {
      connectWith: ".sl-simplelayout",
      items: ".sl-layout",
      handle: ".sl-toolbar-layout .move",
      placeholder: "layout-placeholder",
      axis: "y",
      forcePlaceholderSize: true,
      helper: sortableHelper,
      receive: function(event, ui) {
        var layout;
        if($(ui.item).hasClass("sl-toolbox-layout")) {
          var item = $(this).find(".ui-draggable");
          layout = $(this).data().object.insertLayout(ui.item.data().columns);
          layout.element.insertAfter(item);
          item.remove();
        } else {
          self.moveLayout($(this).data().object, $(this).data().parent);
        }
      },
      start: function() {
        self.enableFrames();
        root.addClass("sl-layout-dragging");
        $(".sl-simplelayout").sortable("refreshPositions");
      },
      update: function(event, ui) {
        if(ui.item.parent()[0] === this && !ui.sender) {
          EventEmitter.trigger("layoutMoved", [ui.item.data().object]);
        }
        self.disableFrames();
        root.removeClass("sl-layout-dragging");
      },
      stop: function() {
        self.disableFrames();
        root.removeClass("sl-layout-dragging");
      }
    };

    var BLOCK_SORTABLE = {
      connectWith: ".sl-column",
      placeholder: "block-placeholder",
      forcePlaceholderSize: true,
      handle: ".sl-toolbar-block .move",
      helper: sortableHelper,
      cursorAt: { left: 50, top: 50 },
      receive: function(event, ui) {
        var block;
        if($(ui.item).hasClass("sl-toolbox-block")) {
          var item = $(this).find(".ui-draggable");
          var layout = $(this).parents(".sl-layout").data().object;
          block = layout.insertBlock("", $(ui.item).data().type);
          block.element.insertAfter(item);
          item.remove();
        } else {
          var sourceLayout = ui.sender.parents(".sl-layout").data().object;
          sourceLayout.moveBlock(ui.item.data().object, $(this).parents(".sl-layout").data().object);
        }
      },
      start: function() {
        self.enableFrames();
        root.addClass("sl-block-dragging");
        $(".sl-column").sortable("refreshPositions");
      },
      update: function(event, ui) {
        if(ui.item.parent()[0] === this && !ui.sender) {
          EventEmitter.trigger("blockMoved", [ui.item.data().object]);
        }
        self.disableFrames();
        root.removeClass("sl-block-dragging");
      },
      stop: function() {
        self.disableFrames();
        root.removeClass("sl-block-dragging");
      }
    };

    this.on("layout-committed", function(layout) {
      var layoutToolbar = new Toolbar(self.options.toolbox.options.layoutActions, "vertical", "layout");
      layout.attachToolbar(layoutToolbar);
      $(".sl-column", layout.element).sortable(BLOCK_SORTABLE);
    });

    this.on("block-committed", function(block) {
      if(self.options.toolbox.options.blocks[block.type]) {
        var blockToolbar = new Toolbar(self.options.toolbox.options.blocks[block.type].actions, "horizontal", "block");
        block.attachToolbar(blockToolbar);
      }
    });

    $(".sl-simplelayout").sortable(LAYOUT_SORTABLE);
    $(".sl-column").sortable(BLOCK_SORTABLE);

    this.options.toolbox.element.find(".sl-toolbox-block, .sl-toolbox-layout").draggable(TOOLBOX_COMPONENT_DRAGGABLE_SETTINGS);
    this.options.toolbox.element.find(".sl-toolbox-layout").draggable("option", "connectToSortable", ".sl-simplelayout");
    this.options.toolbox.element.find(".sl-toolbox-block").draggable("option", "connectToSortable", ".sl-column");

  };

  return Simplelayout;

});
