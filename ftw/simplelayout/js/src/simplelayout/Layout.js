import Block from "simplelayout/Block";
import EventEmitter from "simplelayout/EventEmitter";
import transactional from "simplelayout/transactional";
import Element from "simplelayout/Element";
import Toolbar from "simplelayout/Toolbar";
import handlebarsTimes from "helpers/handlebars";
import $ from "jquery";
import { getNodeAttributesAsObject } from "../helpers/DOMHelpers";

const EE = EventEmitter.getInstance();

export default function Layout(columns) {
  if (!(this instanceof Layout)) {
    throw new TypeError("Layout constructor cannot be called as a function.");
  }

  columns = columns || 4;

  var template = `
    <div class='sl-layout'>
      <div class='sl-layout-content' data-config='{}'>
        <div class="sl-columns">
          {{#times columns}}
            <div class='sl-column sl-col-{{../columns}}'></div>
          {{/times}}
        </div>
      </div>
    </div>
  `;

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
    EE.trigger("blockInserted", [block]);
    return block;
  };

  this.deleteBlock = function(id) {
    var block = this.blocks[id];
    delete this.blocks[id];
    EE.trigger("blockDeleted", [block]);
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
    EE.trigger("beforeBlockMoved", [block]);
    this.deleteBlock(block.id);
    block.parent = target;
    block.data({ parent: target });
    target.blocks[block.id] = block;
    EE.trigger("blockMoved", [block]);
    return this;
  };

  this.content = function(toReplace) {
    var self = this;
    $(this.element).html(toReplace);
    this.blocks = {};
    $(".sl-block", this.element).each(function() {
      self.insertBlock().restore(this, self, $(this).data().type, $(this).data().uid);
    });
    EE.trigger("layout-committed", [this]);
    return this;
  };

  this.restore = function(restoreElement = this.element, restoreParent = this.parent, restoreColumn = this.columns, represents = this.represents) {
    var self = this;
    this.columns = restoreColumn;
    Layout.prototype.restore.call(this, restoreElement, restoreParent, represents);
    this.commit();
    $(".sl-block", restoreElement).each(function() {
      self.insertBlock().restore(this, self, $(this).data().type, $(this).data().uid);
    });
  };

  this.config = function() { return this.element.find(".sl-layout-content").data('config'); }

  this.toJSON = function() { return { columns: this.columns, blocks: this.blocks }; };

};

transactional.call(Layout.prototype);
Element.call(Layout.prototype);
