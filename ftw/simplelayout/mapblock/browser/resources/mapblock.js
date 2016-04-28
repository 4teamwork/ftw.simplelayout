(function() {

  "use strict";

  $(function() {
    $(document).on("onBeforeClose", ".overlay", function() {
      if ($.fn.collectivegeo) {
        $(".widget-cgmap").filter(":visible").collectivegeo();
      }
    });

    $(document).on("onLoad", ".overlay", function() {
      if ($.fn.collectivegeo) {
        var maps = $(".widget-cgmap").filter(":visible");
        var mapWidgets = $(".map-widget .widget-cgmap").filter(":visible");
        maps.collectivegeo();
        mapWidgets.collectivegeo("add_edit_layer");
        mapWidgets.collectivegeo("add_geocoder");

        // Fix mouse pointer position according to openlayers pointer
        $(mapWidgets.closest(".pb-ajax")).on("scroll", function(){
          mapWidgets.collectivegeo("refresh");
        });

      }
    });
  });
})();

