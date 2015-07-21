define([], function() {

  "use strict";

  return {
    generateFromHash: function(hash) {
      if($.isEmptyObject(hash)) {
        return 0;
      }
      return Math.max.apply(null, Object.keys(hash)) + 1;
    }
  };

});
