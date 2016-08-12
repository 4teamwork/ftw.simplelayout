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

    var sortableHelper = function() { return $('<div class="draggableHelper"><div>'); };

    var LAYOUT_SORTABLE = {
      connectWith: ".sl-simplelayout",
      items: ".sl-layout",
      handle: ".sl-toolbar-layout .move",
      placeholder: "layout-placeholder",
      cursorAt: { left: 50, top: 50 },
      // axis: "y",
      forcePlaceholderSize: true,
      helper: sortableHelper,
      receive: function(event, ui) {
        var layout;
        if(ui.item.hasClass("sl-toolbox-layout")) {
          var item = $(this).find(".ui-draggable");
          layout = $(this).data().object.insertLayout(ui.item.data().columns);
          layout.element.insertAfter(item);
          item.remove();
        } else {
          self.moveLayout($(ui.item).data().object, $(this).data().object);
          self.disableFrames();
        }
      },
      beforeStart: function(event, ui) {
        if(ui.item.hasClass("sl-layout")) {
          self.restrictLayout(ui.item.data().object.columns);
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
      },
      stop: function(event, ui) {
        if(ui.item.hasClass("sl-layout")) {
          self.allowLayout(ui.item.data().object.columns);
        }
        root.removeClass("sl-layout-dragging");
        self.disableFrames();
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
      stop: function() {
        self.disableFrames();
        root.removeClass("sl-block-dragging");
      },
      update: function(event, ui) {
        if(ui.item.parent()[0] === this && !ui.sender) {
          EventEmitter.trigger("blockMoved", [ui.item.data().object]);
        }
      }
    };

    this.options = $.extend({
      toolbox: new Toolbox(),
      editLayouts: true,
      layoutRestrictions: {}
    }, options || {});

    this.managers = {};

    this.insertManager = function() {
      var manager = new Layoutmanager();
      this.managers[manager.id] = manager;
      return manager;
    };

    this.moveLayout = function(layout, target) {
      var source = layout.parent;

      layout.data({ parent: target });
      layout.parent = target;
      target.layouts[layout.id] = layout;

      source.deleteLayout(layout.id);
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

    this.restrictLayout = function(layout) {
      if(this.options.layoutRestrictions[layout]) {
        $.each(this.options.layoutRestrictions[layout], function(idx, managerId) {
          self.managers[managerId].isEnabled(false).element.sortable("disable");
        });
      }
    };

    this.allowLayout = function(layout) {
      if(this.options.layoutRestrictions[layout]) {
        $.each(this.options.layoutRestrictions[layout], function(idx, managerId) {
          self.managers[managerId].isEnabled(true).element.sortable("enable");
        });
      }
    };

    this.on = function(eventType, callback) {
      EventEmitter.on(eventType, callback);
      return this;
    };

    this.serialize = function() { return JSON.stringify(this.managers); };

    this.restore = function(source) {
      this.source = source;
      $(".sl-simplelayout", source).each(function() {
        self.insertManager().restore(this, $(this).attr("id"));
      });
      $(".sl-simplelayout", this.source).sortable(LAYOUT_SORTABLE);
      $(".sl-column", this.source).sortable(BLOCK_SORTABLE);
      return this;
    };

    var TOOLBOX_COMPONENT_DRAGGABLE_SETTINGS = {
      helper: "clone",
      cursor: "pointer",
      beforeStart: function() {
        if($(this).hasClass("sl-toolbox-layout")) {
          self.restrictLayout($(this).data().columns);
        }
      },
      start: function() {
        self.enableFrames();
        if($(this).hasClass("sl-toolbox-block")) {
          root.addClass("sl-block-dragging");
        } else {
          root.addClass("sl-layout-dragging");
        }
      },
      stop: function() {
        self.allowLayout($(this).data().columns);
        self.disableFrames();
        root.removeClass("sl-block-dragging sl-layout-dragging");
      }
    };

    this.on("layout-committed", function(layout) {
      if(self.options.editLayouts) {
        var layoutToolbar = new Toolbar(self.options.toolbox.options.layoutActions, "vertical", "layout");
        layout.attachToolbar(layoutToolbar);
        $(".sl-column", layout.element).sortable(BLOCK_SORTABLE);
      }
    });

    this.on("block-committed", function(block) {
      if(self.options.toolbox.options.blocks[block.type]) {
        var blockToolbar = new Toolbar(self.options.toolbox.options.blocks[block.type].actions, "horizontal", "block");
        block.attachToolbar(blockToolbar);
      }
    });

    this.options.toolbox.element.find(".sl-toolbox-block, .sl-toolbox-layout").draggable(TOOLBOX_COMPONENT_DRAGGABLE_SETTINGS);
    this.options.toolbox.element.find(".sl-toolbox-layout").draggable("option", "connectToSortable", ".sl-simplelayout");
    this.options.toolbox.element.find(".sl-toolbox-block").draggable("option", "connectToSortable", ".sl-column");

    $(".sl-simplelayout").sortable(LAYOUT_SORTABLE);
    $(".sl-column").sortable(BLOCK_SORTABLE);

    root.addClass("simplelayout-initialized");

    /* Patch for registring beforeStart event */
    var oldMouseStart = $.ui.sortable.prototype._mouseStart;
    $.ui.sortable.prototype._mouseStart = function (event, overrideHandle, noActivation) {
        this._trigger("beforeStart", event, this._uiHash());
        oldMouseStart.apply(this, [event, overrideHandle, noActivation]);
    };

  };

  return Simplelayout;

});
