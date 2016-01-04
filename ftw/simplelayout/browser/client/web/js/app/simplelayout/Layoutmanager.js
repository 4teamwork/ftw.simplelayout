define([
      "app/simplelayout/Layout",
      "app/simplelayout/Block",
      "app/simplelayout/EventEmitter",
      "app/simplelayout/Element",
      "app/simplelayout/transactional",
      "app/helpers/template_range"
    ],
    function(
      Layout,
      Block,
      EventEmitter,
      Element,
      transactional) {

  "use strict";

  var Layoutmanager = function() {

    if (!(this instanceof Layoutmanager)) {
      throw new TypeError("Layoutmanager constructor cannot be called as a function.");
    }

    var template = "<div class='sl-simplelayout'></div>";

    Element.call(this, template);

    this.name = "layoutmanager";

    this.create();

    this.layouts = {};

    this.attachTo = function(target) {
      $(target).append(this.element);
      return this;
    };

    this.insertLayout = function(columns) {
      var layout = new Layout(columns);
      layout.parent = this;
      layout.data({ parent: this });
      this.layouts[layout.id] = layout;
      EventEmitter.trigger("layoutInserted", [layout]);
      return layout;
    };

    this.deleteLayout = function(id) {
      var layout = this.layouts[id];
      delete this.layouts[id];
      EventEmitter.trigger("layoutDeleted", [layout]);
      return layout;
    };

    this.hasLayouts = function() { return Object.keys(this.layouts).length > 0; };

    this.getInsertedBlocks = function() {
      return $.map(this.layouts, function(layout) {
        return layout.getInsertedBlocks();
      });
    };

    this.getCommittedBlocks = function() {
      return $.map(this.layouts, function(layout) {
        return layout.getCommittedBlocks();
      });
    };

    this.moveBlock = function(block, target) {
      block.parent.moveBlock(block, target);
      return this;
    };

    this.restore = function(restoreElement, represents) {
      var self = this;
      Layoutmanager.prototype.restore.call(this, restoreElement, null, represents);
      this.commit();
      $(".sl-layout", restoreElement).each(function() {
        self.insertLayout().restore(this, self, $(".sl-column", this).length);
      });
    };

    this.toJSON = function() { return { layouts: this.layouts, represents: this.represents }; };

  };

  Element.call(Layoutmanager.prototype);
  transactional.call(Layoutmanager.prototype);

  return Layoutmanager;

});
