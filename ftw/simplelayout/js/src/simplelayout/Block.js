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

  this.content = function(toReplace, id) {
    $(".sl-block-content", this.element).attr('id', id).html(toReplace);
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

  this.updateToolbar = function() {
    // check if configuration on block indicates that button is active
    $(".block-server-action", this.toolbar.element).toArray().forEach(function(e) {
      var buttonParameter = $(e).data();
      var active = Object.keys(buttonParameter).every(function(propertyName) {
        return (propertyName in this.data() &&
                buttonParameter[propertyName] == this.data()[propertyName]);
      }, this);
      $(e).toggleClass("active", active);
    }.bind(this));
  };

  this.toJSON = function() { return { represents: this.represents, type: this.type }; };

};

transactional.call(Block.prototype);
Element.call(Block.prototype);
