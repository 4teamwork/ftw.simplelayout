(function($, global) {

  "use strict";

  function FormOverlay(options) {

    var overlay = {
      formSubmitted: false,
      element: null,
      form: null,
      overlay: null,
      settings: {
        mask: {color: "#fff", loadSpeed: 200, opacity: 0.4},
        left: "center",
        fixed: false,
        closeOnClick: false,
        onBeforeClose: function() { overlay.onCancel.call(overlay); }
      },
      onCancelCallback: function(){},
      onSubmitCallback: function(){},
      open: function() {
        this.overlay.load();
      },
      close: function() {
        this.overlay.close();
        this.element.remove();
        this.element = null;
        this.overlay = null;
      },
      onCancel: function() {
        if(!this.formSubmitted) {
          this.onCancelCallback();
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
            self.element = $("<div class='overlay'></div>");
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
          this.onSubmitCallback.call(instance, data);
        } else {
          this.element.html(data.content);
          this.element.trigger("OverlayContentReloaded", [this]);
          this.initializePloneComponents();
        }
      },
      onFormCancel: function(event) {
        this.close();
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
