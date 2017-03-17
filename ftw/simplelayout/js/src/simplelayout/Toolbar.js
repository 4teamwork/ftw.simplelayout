import Element from "simplelayout/Element";
import $ from "jquery";
import Handlebars from "handlebars";

export default function Toolbar(actions, orientation, type) {

  if (!(this instanceof Toolbar)) {
    throw new TypeError("Toolbar constructor cannot be called as a function.");
  }

  actions = actions || {};

  var template = `
    <ul class='sl-toolbar{{#if type}}-{{type}}{{/if}}{{#if orientation}} {{orientation}}{{/if}}'>
      {{#each actions}}
        <li>
          <a
            {{#each this}}
            {{@key}}="{{this}}"
            {{/each}}
          >
          </a>
        </li>
      {{/each}}
    </ul>
  `;

  Element.call(this, template);

  this.create({ actions: actions, orientation: orientation, type: type });

  this.disable = function(action) { $("." + action, this.element).css("display", "none"); };

  this.enable = function(action) { $("." + action, this.element).css("display", "block"); };

};

Element.call(Toolbar.prototype);
