import Layout from "simplelayout/Layout";
import Block from "simplelayout/Block";
import EventEmitter from "simplelayout/EventEmitter";
import Element from "simplelayout/Element";
import transactional from "simplelayout/transactional";
import $ from "jquery";

const EE = EventEmitter.getInstance();

export default function Layoutmanager() {

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
    EE.trigger("layoutInserted", [layout]);
    return layout;
  };

  this.deleteLayout = function(id) {
    var layout = this.layouts[id];
    delete this.layouts[id];
    EE.trigger("layoutDeleted", [layout]);
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

  this.getInsertedLayouts = function() {
    return $.grep($.map(this.layouts, function(layout) { return layout; }), function(layout) {
      return !layout.committed;
    });
  };

  this.getCommittedLayouts = function() {
    return $.grep($.map(this.layouts, function(layout) { return layout; }), function(layout) {
      return layout.committed;
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
