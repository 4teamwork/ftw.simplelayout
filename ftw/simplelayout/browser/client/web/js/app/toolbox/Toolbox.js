define(["app/simplelayout/Element", "jsrender"], function(Element) {

  "use strict";

  var Toolbox = function(options) {

    if (!(this instanceof Toolbox)) {
      throw new TypeError("Toolbox constructor cannot be called as a function.");
    }

    var template = $.templates(
      /*eslint no-multi-str: 0 */
      "<div id='sl-toolbox' class='sl-toolbox'> \
          <div class='components'> \
            <a class='sl-toolbox-header components'> \
              <i></i> \
            </a> \
              <div class='sl-toolbox-components'> \
                {{for components}} \
                  <a class='sl-toolbox-component {{:contentType}}' data-type='{{:contentType}}' data-form_url='{{:formUrl}}'> \
                    <i class='icon-{{:contentType}}'></i> \
                    <span class='description'>{{:title}}</span> \
                  </a> \
                {{/for}} \
              </div> \
              {{if canChangeLayout}} \
                <a class='sl-toolbox-header layouts'> \
                  <i></i> \
                </a> \
                <div class='sl-toolbox-layouts'> \
                  {{props layouts}} \
                    <a class='sl-toolbox-layout' data-columns='{{>prop}}'>{{>prop}} \
                      <span class='description'>{{>prop}} {{>#parent.parent.data.labels.labelColumnPostfix}}</span> \
                    </a> \
                  {{/props}} \
                </div> \
              {{/if}} \
          </div> \
          <a class='sl-toolbox-header layouts'> \
            <i></i> \
          </a> \
          {{if canChangeLayout}} \
          <div class='sl-toolbox-layouts'> \
            {{props layouts}} \
              <a class='sl-toolbox-layout' data-columns='{{>prop}}'>{{>prop}} \
                <span class='description'>{{>prop}}{{>#parent.parent.data.labels.labelColumnPostfix}}</span> \
              </a> \
            {{/props}} \
          </div> \
          {{/if}} \
        </div> \
      </div>");

    Element.call(this, template);

    this.options = $.extend({
      layouts: [1, 2, 4],
      blocks: [],
      labels: {},
      layoutActions: {}
    }, options || {});

    this.create({
      blocks: this.options.blocks,
      layouts: this.options.layouts,
      labels: this.options.labels,
      canChangeLayout: this.options.canChangeLayout
    });

    var blockObjects = {};
    $.each(this.options.blocks, function(idx, block) {
      blockObjects[block.contentType] = block;
    });

    this.options.blocks = blockObjects;

    this.attachTo = function(target) { target.append(this.element); };

    this.blocksEnabled = function(state) { $(".sl-toolbox-blocks", this.element).toggleClass("disabled", !state); };

  };

  Element.call(Toolbox.prototype);

  return Toolbox;

});
