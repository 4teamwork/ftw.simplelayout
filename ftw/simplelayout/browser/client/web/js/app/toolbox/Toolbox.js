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
            <div class='addables'> \
              <a class='sl-toolbox-header'>Komponenten</a> \
                <div class='sl-toolbox-components'> \
                  {{for components}} \
                    <a class='sl-toolbox-component' title='{{:description}}' data-type='{{:contentType}}' data-form_url='{{:formUrl}}'> \
                      <i class='icon-{{:contentType}}'></i>{{:title}} \
                    </a> \
                  {{/for}} \
                </div> \
              <a class='sl-toolbox-header'>Layout</a> \
                {{props layouts}} \
                  <a class='sl-toolbox-layout' data-columns='{{>prop}}'> \
                    <i class='icon-layout'></i>{{>prop}} - Spalten Layout \
                  </a> \
                 {{/props}} \
            </div> \
            <a class='sl-toolbox-header sl-toolbox-handle'>Toolbox</a> \
          </div> \
        </div>");

    var components = {};
    if (!$.isEmptyObject(options.components)) {
      components = $.map(options.components.addable_blocks, function(component) { return component; }).sort(function(a, b) {
        return normalizeCompare(a.title, b.title);
      });
    }
    var data = {
      "components": components,
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
