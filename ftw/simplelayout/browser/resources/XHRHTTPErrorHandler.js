(function(global, $) {

  "use strict";

  var URLMapping = [
    "sl-ajax-reload-block-view",
    "sl-toolbox-view",
    "sl-ajax-delete-blocks-view",
    "add_block",
    "sl-ajax-edit-block-view",
    "sl-ajax-upload-block-view",
    "edit.json"
  ];

  // 0 stands for disconnected
  var HTTPErrors = [0, 500, 401, 503];

  function XHRHTTPErrorHandler() {

    var self = this;

    this.checkURL = function(url) {
      return $.grep(URLMapping, function(stack) {
        return url.indexOf(stack) >= 0;
      }).length > 0;
    };

    this.checkErrorCode = function(errorCode) { return $.inArray(errorCode, HTTPErrors) >= 0; };

    this.shout = function(message) {
      global.alert(message);
    };

    this.catch = function(event, xhr, settings) {
      if(!self.checkURL(settings.url)) {
        return false;
      }
      if(self.checkErrorCode(xhr.status)) {
        self.shout(xhr.statusText);
      }
    };

    this.listen = function() { $(global.document).ajaxError(this.catch); };

  }

  var handler = new XHRHTTPErrorHandler();
  handler.listen();

}(window, jQuery));
