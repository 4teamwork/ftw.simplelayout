import createGUID from "helpers/idHelper";
import $ from "jquery";
import Handlebars from "handlebars";
import EventEmitter from "simplelayout/EventEmitter";

const EE = EventEmitter.getInstance();

export default function Element(template, represents) {

  this.template = Handlebars.compile(template || "");
  this.represents = represents;
  this.enabled = true;

  this.create = function(data) {
    this.element = $(this.template(data));
    this.id = createGUID();
    this.element.data({ id: this.id, object: this });
    return this.element;
  };

  this.data = function(data) {
    if(data) {
      return this.element.data(data);
    }
    return this.element.data();
  };

  this.remove = function() {
    this.element.remove();
    return this;
  };

  this.detach = function() {
    this.element.detach();
    return this;
  };

  this.attachToolbar = function(toolbar) {
    this.toolbar = toolbar;
    this.element.append(toolbar.element);
    this.updateToolbar();
    EE.trigger("toolbar-attached", [this])
    return this;
  };

  // mark options on toolbar according to element state
  this.updateToolbar = function() {};

  this.isEnabled = function(state) {
    this.element.toggleClass("disabled", !state);
    this.enabled = state;
    return this;
  };

  this.restore = function(restoreElement, restoreParent, restoreRepresents) {
    this.element = $(restoreElement);
    this.parent = restoreParent;
    this.data({ id: this.id, object: this, parent: restoreParent, represents: restoreRepresents });
    this.represents = restoreRepresents;
  };

  return this;
}
