define([], function() {

  "use strict";

  return {
    generateFromHash: function(hash) {
      if($.isEmptyObject(hash)) {
        return 0;
      }
      var keys = Object.keys(hash).sort(function(a, b) {
        return parseInt(a) - parseInt(b);
      });
      var lastKey = keys[parseInt(keys.length - 1)];
      return parseInt(lastKey) + 1;
    }
  };

});
