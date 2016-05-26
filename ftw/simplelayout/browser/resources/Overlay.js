(function($, global) {

  "use strict";

  function FormOverlay(options) {

    options = $.extend({
      disableClose: false,
      cssclass: ""
    }, options);

    var root = $(":root");

    var overlay = {
      formSubmitted: false,
      element: null,
      form: null,
      overlay: null,
      settings: {
        mask: {color: "#fff", loadSpeed: 0, opacity: 0.4},
        left: "center",
        speed: 0,
        closeSpeed: 0,
        fixed: false,
        closeOnClick: false,
        closeOnEsc: false,
        onClose: function() { overlay.unload(); }
      },
      bindCloseEvents: function() {
        var self = this;
        $(document).on("keydown", function(event) {
          if(event.which === $.ui.keyCode.ESCAPE) {
            self.close.call(self);
          }
        });
      },
      unload: function() {
        this.element.remove();
        this.element = null;
        this.overlay = null;
        $(document).off("keydown");
      },
      canClose: function() {
        return !($.isFunction(options.disableClose) ? options.disableClose() : options.disableClose);
      },
      onCancelCallback: function(){},
      onSubmitCallback: function(){},
      open: function() {
        if(this.settings.speed === 0) {
          this.element.show();
        }
        this.overlay.load();
        this.bindCloseEvents();
        this.form.find('input:visible:first').focus();
        root.addClass("overlay-open");
      },
      close: function() {
        if(this.canClose()) {
          this.onCancelCallback();
          if(this.settings.speed === 0) {
            this.element.hide();
          }
          this.overlay.close();
          root.removeClass("overlay-open");
          $(this.element).trigger("overlayCancel", this);
        }
      },
      initializePloneComponents: function() {
        if ($.fn.ploneTabInit) {
          this.element.parent().ploneTabInit();
        }
        if (global.initTinyMCE) {
          global.initTinyMCE(this.form);
        }
        if(global.tinyMCE && global.tinyMCE.triggerSave) {
          global.tinyMCE.triggerSave(true, true);
        }
        // Initialize pat-registry scan for Plone 5.x
        if(global.require) {
          try {
            var registry = require("pat-registry");
            if(registry) {
              registry.scan(this.form);
            }
          } catch(e) {
            console.error("Pattern Registry could not get initialized", e);
          }
        }
      },
      getActionUrl: function() {
        return this.form.attr("action");
      },
      getPayload: function() {
        return options && options.payload;
      },
      loadForm: function(formUrl, payload, callback) {
        var self = this;
        $.getJSON(formUrl, payload, function(data) {
          if(!self.overlay) {
            self.element = $("<div class='overlay'></div>").addClass(options.cssclass);
            self.overlay = self.element.overlay(self.settings).overlay();
            self.element.on("submit", "form", function(event) {
              event.preventDefault();
              self.onFormSubmit.call(self, this);
            });
            self.element.on("click", "#form-buttons-cancel", function(event) {
              event.preventDefault();
              self.onFormCancel.call(self);
            });
            $("body").append(self.element);
          }
          self.element.html(data.content);
          self.form = $("form", self.element);
          self.initializePloneComponents();
          self.open();
          if(callback) { callback.call(self); }
        });
      },
      requestForm: function(action, payload) {
        var self = this;
        payload.append("_authenticator", $('input[name="_authenticator"]').val());
        return $.ajax({
          type: "POST",
          url: action,
          data: payload,
          dataType: "json",
          processData: false,
          contentType: false
        }).done(function(data) { self.onFormRequestDone.call(self, data); });
      },
      onFormRequestDone: function(data) {
        if(data.proceed) {
          this.formSubmitted = true;
          $(this.element).trigger("overlaySubmit", this);
          this.onSubmitCallback.call(overlay, data);
        } else {
          this.element.html(data.content);
          this.element.trigger("OverlayContentReloaded", [this]);
          this.initializePloneComponents();
        }
      },
      onFormCancel: function() {
        overlay.close();
      },
      onFormSubmit: function(formData) {
        var fd = new global.FormData(formData);
        fd.append("form.buttons.save", $("#form-buttons-save").val());
        this.requestForm(formData.action, fd);
      }
    };

    var instance = {
      load: function(formUrl, payload, callback) {
        overlay.loadForm(formUrl, payload, callback);
      },

      onCancel: function(cancelCallback) {
        overlay.onCancelCallback = cancelCallback;
      },

      onSubmit: function(submitCallback) {
        overlay.onSubmitCallback = submitCallback;
      },

      disableClose: function(disable) {
        options.disableClose = disable;
      },

      open: function() {
        overlay.open();
      },

      close: function() {
        overlay.close();
      }
    };

    return instance;
  }

  global.FormOverlay = FormOverlay;

}(jQuery, window));
