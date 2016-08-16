(function() {

  "use strict";

    var initGoogleMaps = function(callback){
      var widget = $('.blockwidget-cgmap, .map-widget');
      if (widget.length > 0) {
        var googleJS = widget.data('googlejs');
        if (callback !== undefined) {
          $.getScript(googleJS + '&callback=' + callback);

        } else {
          $.getScript(googleJS, function(){
            if ($.fn.collectivegeo) {
              var maps = $(".blockwidget-cgmap").filter(":visible");
              maps.collectivegeo();
            }

          });
        }
      }
    };

    $(window).on('load', function(){
      initGoogleMaps();
    });

  $(function() {
    $(document).on("onBeforeClose", ".overlay", function() {
      if ($.fn.collectivegeo) {
        $(".blockwidget-cgmap").filter(":visible").collectivegeo();
      }
    });


    $(document).on("onLoad", ".overlay", function() {

      window.MapBlockEditInitializer = function() {
        if ($.fn.collectivegeo) {
          var maps = $(".blockwidget-cgmap").filter(":visible");
          var mapWidgets = $(".map-widget .blockwidget-cgmap").filter(":visible");
          maps.collectivegeo();
          mapWidgets.collectivegeo("add_edit_layer");
          mapWidgets.collectivegeo("add_geocoder");

          // Fix mouse pointer position according to openlayers pointer
          $(mapWidgets.closest(".pb-ajax")).on("scroll", function(){
            mapWidgets.collectivegeo("refresh");
          });

        }

      };

      if (typeof google === 'object' && typeof google.maps === 'object'){
        window.MapBlockEditInitializer();
      } else {
        initGoogleMaps('MapBlockEditInitializer');
      }

    });
  });
})();

