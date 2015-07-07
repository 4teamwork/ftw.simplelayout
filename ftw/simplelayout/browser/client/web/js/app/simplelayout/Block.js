define(["app/simplelayout/EventEmitter"], function(eventEmitter) {

  "use strict";

  function Block(content, type) {

    if (!(this instanceof Block)) {
      throw new TypeError("Block constructor cannot be called as a function.");
    }

    var frameFixTemplate = $.templates('<div class="iFrameFix"></div>');

    var template = $.templates(
      '<div data-type="{{:type}}" class="sl-block"><div class="sl-block-content">{{:content}}</div></div>'
    );

    return {

      committed: false,

      uid: null,

      toolbar: null,

      type: type,

      element: null,

      create: function() {
        var data = { "content": content, "type": type };
        this.element = $(template.render(data));
        this.fixFrame();
        return this.element;
      },

      fixFrame: function() {
        this.frame = $(frameFixTemplate.render());
        this.element.prepend(this.frame);
      },

      enableFrame: function() { this.frame.show(); },

      disableFrame: function() { this.frame.hide(); },

      content: function(toReplace) { $(".sl-block-content", this.element).html(toReplace); },

      commit: function() {
        this.committed = true;
        eventEmitter.trigger("blockCommitted", [this]);
      },

      attachToolbar: function(toolbar) {
        this.toolbar = toolbar;
        this.element.append(toolbar.element);
      },

      toJSON: function() { return { uid: this.uid, type: this.type }; }
    };

  }
  return Block;

});
