define(["app/simplelayout/Layoutmanager", "app/simplelayout/Toolbar", "app/toolbox/Toolbox", "app/simplelayout/EventEmitter"], function(Layoutmanager, Toolbar, Toolbox, eventEmitter) {

  "use strict";

  function Simplelayout(_options) {

    if (!(this instanceof Simplelayout)) {
      throw new TypeError("Simplelayout constructor cannot be called as a function.");
    }

    var options = $.extend({
      toolbox: new Toolbox({layouts: [1, 2, 4]})
    }, _options || {});

    var managers = {};

    var id = 0;

    var moveLayout = function(layout, newManagerId) {
      var layoutData = layout.element.data();
      var manager = managers[layoutData.container];
      var nextLayoutId = Object.keys(managers[newManagerId].layouts).length;
      $.extend(layout.element.data(), { layoutId: nextLayoutId, container: newManagerId });
      delete manager.layouts[layoutData.layoutId];
      managers[newManagerId].layouts[nextLayoutId] = layout;
      managers[newManagerId].moveLayout(layout, nextLayoutId);
      eventEmitter.trigger("layoutMoved", [layout]);
    };

    var moveBlock = function(block, newManagerId, newLayoutId, newColumnId) {
      var blockData = block.element.data();
      var newData = { container: newManagerId, layoutId: newLayoutId, columnId: newColumnId };
      var newManager = managers[newManagerId];
      delete managers[blockData.container].layouts[blockData.layoutId].columns[blockData.columnId].blocks[blockData.blockId];
      var nextBlockId = Object.keys(managers[newManagerId].layouts[newLayoutId].columns[newColumnId].blocks).length;
      $.extend(block.element.data(), newData);
      newManager.setBlock(newLayoutId, newColumnId, nextBlockId, block);
      eventEmitter.trigger("blockMoved", [block]);
    };

    var getCommittedBlocks = function() {
      var committedBlocks = [];
      for(var key in managers) {
        committedBlocks = $.merge(managers[key].getCommittedBlocks(), committedBlocks);
      }
      return committedBlocks;
    };

    var getInsertedBlocks = function() {
      var insertedBlocks = [];
      for(var key in managers) {
        insertedBlocks = $.merge(managers[key].getInsertedBlocks(), insertedBlocks);
      }
      return insertedBlocks;
    };

    var disableFrames = function() {
      $.each(getCommittedBlocks(), function(idx, block) {
        block.disableFrame();
      });
    };

    var enableFrames = function() {
      $.each(getCommittedBlocks(), function(idx, block) {
        block.enableFrame();
      });
    };

    var TOOLBOX_COMPONENT_DRAGGABLE_SETTINGS = { helper: "clone", cursor: "pointer", start: enableFrames, stop: disableFrames };

    var sortableHelper = function(){ return $('<div class="draggableHelper"><div>'); };

    var animatedrop = function(ui){
      ui.item.addClass("animated");
      setTimeout(function(){
        ui.item.removeClass("animated");
      }, 1);
    };

    var toggleActiveLayouts = function(event, ui) {
      var elements = $.map($(event.target).data("ui-sortable").items, function(layout){
        return layout.item[0];
      });
      $(elements).not(ui.item).toggleClass("inactive");
      $(elements).filter(".inactive").animate({"height": "140px"}, 200);

      $(elements).css("height", "auto");
      $(window).scrollTop(ui.item.offset().top);

      $(".sl-simplelayout").sortable("refreshPositions");
    };

    var canMove = true;
    var originalLayout;

    var LAYOUT_SORTABLE = {
      connectWith: ".sl-simplelayout",
      items: ".sl-layout",
      handle: ".sl-toolbar-layout .move",
      placeholder: "layout-placeholder",
      axis: "y",
      forcePlaceholderSize: true,
      helper: sortableHelper,
      receive: function(event, ui) {
        var manager = managers[$(this).data("container")];
        if(originalLayout) {
          moveLayout(originalLayout, $(this).data("container"));
          originalLayout = null;
        } else {
          var item = $(this).find(".ui-draggable");
          var layout = manager.insertLayout({ columns: ui.item.data("columns") });
          layout.element.insertAfter(item);
          item.remove();
        }
        canMove = false;
      },
      remove: function(event, ui) {
        originalLayout = managers[$(this).data("container")].layouts[ui.item.data("layoutId")];
      },
      start: function(event, ui) {
        enableFrames();
        canMove = true;
        toggleActiveLayouts(event, ui);
      },
      stop: function(event, ui) {
        disableFrames();
        animatedrop(ui);
        toggleActiveLayouts(event, ui);
        if(canMove) {
          var itemData = ui.item.data();
          var manager = managers[itemData.container];
          var layout = manager.layouts[itemData.layoutId];
          manager.moveLayout(layout, itemData.layoutId);
        }
      }
    };

    var originalBlock;

    var BLOCK_SORTABLE = {
      connectWith: ".sl-column",
      placeholder: "block-placeholder",
      forcePlaceholderSize: true,
      handle: ".sl-toolbar-block .move",
      helper: sortableHelper,
      tolerance: "pointer",
      receive: function(event, ui) {
        var manager = managers[$(this).data("container")];
        var data = $(this).data();
        if(originalBlock) {
          moveBlock(originalBlock, data.container, data.layoutId, data.columnId);
          originalBlock = null;
        }
        else if(typeof ui.item.data("layoutId") === "undefined") {
          var item = $(this).find(".ui-draggable");
          var type = ui.item.data("type");
          var block = manager.insertBlock(data.layoutId, data.columnId, null, type);
          block.element.insertAfter(item);
          item.remove();
        }
        canMove = false;
      },
      remove: function(event, ui) {
        var itemData = ui.item.data();
        originalBlock = managers[itemData.container].getBlock(itemData.layoutId, itemData.columnId, itemData.blockId);
      },
      start: function() {
        canMove = true;
        enableFrames();
      },
      stop: function(event, ui) {
        disableFrames();
        animatedrop(ui);
        if(canMove) {
          var itemData = ui.item.data();
          var data = $(this).data();
          managers[itemData.container].moveBlock(itemData.layoutId, itemData.columnId, itemData.blockId, data.layoutId, data.columnId);
        }
      }
    };

    var on = function(eventType, callback) { eventEmitter.on(eventType, callback); };

    var bindToolboxEvents = function() {
      options.toolbox.element.find(".sl-toolbox-component, .sl-toolbox-layout").draggable(TOOLBOX_COMPONENT_DRAGGABLE_SETTINGS);
      options.toolbox.element.find(".sl-toolbox-layout").draggable("option", "connectToSortable", ".sl-simplelayout");
      options.toolbox.element.find(".sl-toolbox-component").draggable("option", "connectToSortable", ".sl-column");
    };

    var bindLayoutEvents = function() {
      $(".sl-simplelayout").sortable(LAYOUT_SORTABLE);
      $(".sl-column").sortable(BLOCK_SORTABLE);
      on("layoutCommitted", function(layout) {
        $(".sl-column", layout.element).sortable(BLOCK_SORTABLE);
      });
    };

    bindLayoutEvents();
    bindToolboxEvents();

    on("layoutInserted", function(layout) {
      var layoutToolbar = new Toolbar(options.toolbox.options.layoutActions, "vertical", "layout");
      layout.attachToolbar(layoutToolbar);
    });

    on("blockInserted", function(block) {
      var blockToolbar = new Toolbar(options.toolbox.options.components[block.type].actions, "horizontal", "block");
      block.attachToolbar(blockToolbar);
    });

    return {

      options: options,

      moveLayout: moveLayout,

      moveBlock: moveBlock,

      getManagers: function() { return managers; },

      serialize: function() { return JSON.stringify(managers); },

      deserialize: function(target) {
        managers = {};
        id = 0;
        var self = this;
        $(".sl-simplelayout", target).each(function(idx, e) {
          var manager = self.insertManager({ source: e });
          manager.deserialize();
        });
      },

      insertManager: function(managerOptions) {
        var manager = new Layoutmanager(managerOptions);
        manager.element.data("container", id);
        managers[id] = manager;
        id++;
        return manager;
      },

      getCommittedBlocks: getCommittedBlocks,

      getInsertedBlocks: getInsertedBlocks,

      attachTo: function(target) {
        $.each(managers, function(idx, manager) {
          manager.attachTo(target);
        });
      },

      on: on

    };

  }

  return Simplelayout;

});
