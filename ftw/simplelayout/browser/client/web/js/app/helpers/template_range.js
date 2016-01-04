define(["jsrender"], function() {

  "use strict";

  $.views.tags({
    range: {
      // Inherit from {{for}} tag
      baseTag: "for",

      // Override the render method of {{for}}
      render: function(val) {
        var array = val,
          start = this.tagCtx.props.start || 0,
          end = this.tagCtx.props.end;

        if (start || end) {
          if (!this.tagCtx.args.length) {
            // No array argument passed from tag, so create a computed array of integers from start to end
            array = [];
            end = end || 0;
            for (var i = start; i <= end; i++) {
              array.push(i);
            }
          } else if ($.isArray(array)) {
            // There is an array argument and start and end properties, so render using the array truncated to the chosen range
            array = array.slice(start, end);
          }
        }

        // Call the {{for}} baseTag render method
        return this.base(array);
      },

      // override onArrayChange of the {{for}} tag implementation
      onArrayChange: function() {
        this.refresh();
      }
    }
  });

});
