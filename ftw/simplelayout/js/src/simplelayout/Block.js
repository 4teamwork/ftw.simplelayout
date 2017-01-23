import EventEmitter from "simplelayout/EventEmitter";
import transactional from "simplelayout/transactional";
import Element from "simplelayout/Element";
import $ from "jquery";
import Handlebars from "handlebars";

const EE = EventEmitter.getInstance();

export default function Block(content, type) {

  if (!(this instanceof Block)) {
    throw new TypeError("Block constructor cannot be called as a function.");
  }

  this.name = "block";

  this.type = type;

  var frame = $(Handlebars.compile('<div class="iFrameFix"></div>')());

  var template = `<div data-type="{{type}}" class="sl-block {{type}}"><div class="sl-block-content">{{{content}}}</div></div>`;

  Element.call(this, template);

  this.create({ type: type, content: content });

  this.content = function(toReplace) {
    $(".sl-block-content", this.element).html(toReplace);
    EE.trigger("blockReplaced", [this]);
    return this;
  };

  this.delete = function() { return this.parent.deleteBlock(this.id); };

  this.fixFrame = function() {
    this.element.prepend(frame);
    return this;
  };

  this.fixFrame();

  this.enableFrame = function() {
    frame.css("display", "block");
    return this;
  };

  this.disableFrame = function() {
    frame.css("display", "none");
    return this;
  };

  this.restore = function(restoreElement, restoreParent, restoreType, represents) {
    this.type = restoreType;
    Block.prototype.restore.call(this, restoreElement, restoreParent, represents);
    this.fixFrame();
    this.commit();
  };

  this.toJSON = function() { return { represents: this.represents, type: this.type }; };

};

transactional.call(Block.prototype);
Element.call(Block.prototype);
