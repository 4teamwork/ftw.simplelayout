(function(global, $) {

  "use strict";

  var URLWhiteList = [
    "sl-ajax-reload-block-view",
    "sl-ajax-delete-blocks-view",
    "add_block",
    "sl-ajax-edit-block-view",
    "sl-ajax-upload-block-view",
    "edit.json",
    "tiny_mce_gzip.js"
  ];

  var URLBlackList = [
    "@@z3cform_validate_field"
  ];

  function getParameterByName(name, url) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)");
    var results = regex.exec(url);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
  }

  function Request(url, callback, options) {

    options = $.extend({ threshold: 300 }, options);

    var threshold = getParameterByName("threshold", url) || options.threshold;
    var timer;

    function isThrottled() {
      var spinnerFlag = getParameterByName("spinner", url);
      return spinnerFlag === "" && spinnerFlag !== "false";
    }

    function throttle() {
      if(isThrottled()) {
        timer = global.setTimeout(callback, threshold);
      }
    }

    function cancel() { global.clearTimeout(timer); }

    throttle();

    return Object.freeze({
      throttle: throttle,
      cancel: cancel
    });

  }

  function RequestTracker() {

    var markerClass = "ajax-loading";
    var $document = $(document);
    var root = $(":root");

    var requests = {};

    function checkURL(url) {
      var isWhiteListed = !!$.grep(URLWhiteList, function(whiteListEntry) {
        return url.indexOf(whiteListEntry) >= 0;
      }).length;

      var isBlackListed = !!$.grep(URLBlackList, function(blackListEntry) {
        return url.indexOf(blackListEntry) >= 0;
      }).length;

      return isWhiteListed && !isBlackListed;
    }

    function mark() { root.addClass(markerClass); }

    function unmark() {
      if(!Object.keys(requests).length) {
        root.removeClass(markerClass);
      }
    }

    function track(url) {
      if(checkURL(url)) {
        requests[url] = Request(url, mark);
      }
    }

    function untrack(url) {
      if(requests[url]) {
        requests[url].cancel();
        delete requests[url];
        unmark();
      }
    }

    /*
      Disable kss spinner. In order for this to work, this file must be evaluated after kss-bbb.js.
      As you can see in the lib profile's jsregistry.xml.
    */
    $document.off("ajaxStart");

    $document.on("ajaxSend", function(event, jqxhr, params) { track(params.url); });
    $document.on("ajaxComplete", function(event, jqxhr, params) { untrack(params.url); });

    return Object.freeze({
      track: track,
      untrack: untrack
    });

  }

  RequestTracker();

})(window, window.jQuery);
