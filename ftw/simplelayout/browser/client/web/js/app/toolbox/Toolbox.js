define([], function() {

  "use strict";

  function Toolbox(_options) {

    if (!(this instanceof Toolbox)) {
      throw new TypeError("Toolbox constructor cannot be called as a function.");
    }

    if (!_options || !_options.layouts || _options.layouts.length === 0) {
      throw new Error("No layouts defined.");
    }

    var options = $.extend({
      components: {}
    }, _options || {});

    var normalizeCompare = function(a, b) {
      return a.localeCompare(b, "de", {caseFirst: "lower"});
    };

    var template = $.templates(
      /*eslint no-multi-str: 0 */
      "<div id='sl-toolbox' class='sl-toolbox'> \
          <div class='components'> \
            <a class='sl-toolbox-header components'> \
              <i></i> \
            </a> \
              <div class='sl-toolbox-components'> \
                {{for components}} \
                  <a class='sl-toolbox-component' data-type='{{:contentType}}' data-form_url='{{:formUrl}}'> \
                    <i class='icon-{{:contentType}}'></i> \
                    <span class='description'>{{:title}}</span> \
                  </a> \
                {{/for}} \
              </div> \
              <a class='sl-toolbox-header layouts'> \
                <i></i> \
              </a> \
              <div class='sl-toolbox-layouts'> \
                {{props layouts}} \
                  <a class='sl-toolbox-layout' data-columns='{{>prop}}'>{{>prop}}</a> \
                {{/props}} \
              </div> \
          </div> \
        </div>");

    var blocks = [];
    var layoutActions = [];
    if (!$.isEmptyObject(options.components)) {
      blocks = $.map(options.components.addableBlocks, function(component) { return component; }).sort(function(a, b) {
        return normalizeCompare(a.title, b.title);
      });
      if(options.components.layoutActions) {
        layoutActions = $.map(options.components.layoutActions.actions, function(action) { return action; }).sort(function(a, b) {
          return normalizeCompare(a.title, b.title);
        });
      }
    }

    options.layoutActions = layoutActions;

    var data = {
      "components": blocks,
      "layouts": options.layouts
    };

    var element = $(template.render(data));

    $(".sl-toolbox-handle", element).on("click", function() { $(".addables").toggleClass("close"); });

    return {

      options: options,

      element: element,

      disableComponents: function() { $(".sl-toolbox-components", this.element).addClass("disabled"); },

      enableComponents: function() { $(".sl-toolbox-components", this.element).removeClass("disabled"); },

      attachTo: function(target) {
        target.append(element);
      }

    };

  }
  return Toolbox;

});
