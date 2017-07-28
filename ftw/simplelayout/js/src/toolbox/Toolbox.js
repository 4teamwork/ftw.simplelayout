import Element from "simplelayout/Element";
import path from "path";
import Handlebars from "handlebars";
import $ from "jquery";

require("jquery-ui");

export default function Toolbox(options) {

  if (!(this instanceof Toolbox)) {
    throw new TypeError("Toolbox constructor cannot be called as a function.");
  }

  var template = `
  <div id='sl-toolbox' class='sl-toolbox'>
    <div>
      <a class='sl-toolbox-header blocks'>
        <span></span>
      </a>
        <div class='sl-toolbox-blocks'>
          {{#each blocks}}
            <a class='sl-toolbox-block {{contentType}}' data-type='{{contentType}}' data-form-url='{{formUrl}}'>
              <span class='icon-{{contentType}}'></span>
              <span class='description'>{{title}}</span>
            </a>
          {{/each}}
        </div>
        {{#if canChangeLayout}}
          <a class='sl-toolbox-header layouts'>
            <span></span>
          </a>
          <div class='sl-toolbox-layouts'>
            {{#each layouts}}
              <a class='sl-toolbox-layout' data-columns='{{this}}'>
                <span>{{this}}</span>
                <span class='description'>{{this}}{{../labels.labelColumnPostfix}}</span>
              </a>
            {{/each}}
          </div>
        {{/if}}
      </div>
    </div>
    `;

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

  var layoutActions = {};
  $.each(this.options.layoutActions, (name, action) => {
    if(!action.rules) {
      action.rules = this.options.layouts;
    }
    $.each(action.rules, (idx, columns) => {
      layoutActions[columns] = layoutActions[columns] || {};
      layoutActions[columns][name] = action;
    });
  });

  this.options.layoutActions = layoutActions;
  this.options.blocks = blockObjects;

  this.attachTo = function(target) { target.append(this.element); };

  this.blocksEnabled = function(state) { $(".sl-toolbox-blocks", this.element).toggleClass("disabled", !state); };

  /* Patch for registering beforeStart event */
  var oldMouseStart = $.ui.draggable.prototype._mouseStart;
  $.ui.draggable.prototype._mouseStart = function (event, overrideHandle, noActivation) {
      this._trigger("beforeStart", event, this._uiHash());
      oldMouseStart.apply(this, [event, overrideHandle, noActivation]);
  };

};

Element.call(Toolbox.prototype);
