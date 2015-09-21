define(["app/simplelayout/Element"], function(Element) {

  "use strict";

  var Toolbar = function(actions, orientation, type) {

    if (!(this instanceof Toolbar)) {
      throw new TypeError("Toolbar constructor cannot be called as a function.");
    }

    actions = actions || [];

    var template = $.templates("<ul class='sl-toolbar{{if type}}-{{:type}}{{/if}}{{if orientation}} {{:orientation}}{{/if}}'>{{for actions}}<li><a {{props}} {{>key}}='{{>prop}}' {{/props}}></a></li><li class='delimiter'></li>{{/for}}</ul>");

    Element.call(this, template);

    var normalizedActions = [];

    $.each(actions, function(key, value) {
      normalizedActions.push(value);
    });

    this.create({ actions: normalizedActions, orientation: orientation, type: type });

    this.disable = function(action) { $("." + action, this.element).hide(); };

    this.enable = function(action) { $("." + action, this.element).show(); };

  };

  Element.call(Toolbar.prototype);

  return Toolbar;

});
