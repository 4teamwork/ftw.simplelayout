define([
      "app/simplelayout/Block",
      "app/simplelayout/EventEmitter",
      "app/simplelayout/transactional",
      "app/simplelayout/Element",
      "app/simplelayout/Toolbar",
      "app/helpers/template_range"
    ],
    function(
      Block,
      EventEmitter,
      transactional,
      Element,
      Toolbar) {

  "use strict";

  var Layout = function(columns) {
    if (!(this instanceof Layout)) {
      throw new TypeError("Layout constructor cannot be called as a function.");
    }

    columns = columns || 4;

    var template = "<div class='sl-layout'>{{range start=1 end=columns ~columns=columns}}<div class='sl-column sl-col-{{:~columns}}'></div>{{/range}}</div>";

    Element.call(this, template);

    this.name = "layout";

    this.create({ columns: columns });

    this.columns = columns;

    this.blocks = {};

    this.toolbar = new Toolbar();

    this.hasBlocks = function() { return Object.keys(this.blocks).length > 0; };

    this.delete = function() { return this.parent.deleteLayout(this.id); };

    this.insertBlock = function(content, type) {
      var block = new Block(content, type);
      block.parent = this;
      block.data({ parent: this });
      this.blocks[block.id] = block;
      EventEmitter.trigger("blockInserted", [block]);
      return block;
    };

    this.deleteBlock = function(id) {
      var block = this.blocks[id];
      delete this.blocks[id];
      EventEmitter.trigger("blockDeleted", [block]);
      return block;
    };

    this.getCommittedBlocks = function() {
      return $.grep($.map(this.blocks, function(block) { return block; }), function(block) {
        return block.committed;
      });
    };

    this.getInsertedBlocks = function() {
      return $.grep($.map(this.blocks, function(block) { return block; }), function(block) {
        return !block.committed;
      });
    };

    this.moveBlock = function(block, target) {
      EventEmitter.trigger("beforeBlockMoved", [block]);
      this.deleteBlock(block.id);
      block.parent = target;
      block.data({ parent: target });
      target.blocks[block.id] = block;
      EventEmitter.trigger("blockMoved", [block]);
      return this;
    };

    this.restore = function(restoreElement, restoreParent, restoreColumn, represents) {
      var self = this;
      this.columns = restoreColumn;
      Layout.prototype.restore.call(this, restoreElement, restoreParent, represents);
      this.commit();
      $(".sl-block", restoreElement).each(function() {
        self.insertBlock().restore(this, self, $(this).data().type, $(this).data().uid);
      });
    };

    this.toJSON = function() { return { columns: this.columns, blocks: this.blocks }; };

  };

  transactional.call(Layout.prototype);
  Element.call(Layout.prototype);

  return Layout;

});
