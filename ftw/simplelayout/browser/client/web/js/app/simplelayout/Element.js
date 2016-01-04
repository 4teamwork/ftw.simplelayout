define(["app/simplelayout/idHelper", "jsrender"], function(idHelper) {

  "use strict";

  function Element(template, represents) {

    this.template = $.templates(template);
    this.represents = represents;
    this.enabled = true;

    this.create = function(data) {
      this.element = $(this.template.render(data));
      this.id = idHelper.createGUID();
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
      return this;
    };

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

  return Element;

});
