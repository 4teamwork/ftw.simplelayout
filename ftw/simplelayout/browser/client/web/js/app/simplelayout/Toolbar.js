define([], function() {

  "use strict";

  function Toolbar(_actions, orientation, type) {

    if (!(this instanceof Toolbar)) {
      throw new TypeError("Toolbar constructor cannot be called as a function.");
    }

    var defaultActions = {};

    var actions = $.extend(defaultActions, _actions || {});

    var normalizedActions = [];

    $.each(actions, function(key, value) {
      normalizedActions.push(value);
    });

    var template = $.templates(
      /*eslint no-multi-str: 0 */
      "<ul class='sl-toolbar{{if type}}-{{:type}}{{/if}}{{if orientation}} {{:orientation}}{{/if}}'> \
        {{for actions}} \
          <li> \
            <a {{props}} {{>key}}='{{>prop}}' {{/props}}></a> \
          </li> \
          <li class='delimiter'></li> \
        {{/for}} \
      </ul>");

    var element = $(template.render({
      actions: normalizedActions,
      orientation: orientation,
      type: type
    }));

    var disable = function(action) { $("." + action, element).hide(); };

    var enable = function(action) { $("." + action, element).show(); };

    return {

      element: element,
      disable: disable,
      enable: enable

    };

  }
  return Toolbar;

});
