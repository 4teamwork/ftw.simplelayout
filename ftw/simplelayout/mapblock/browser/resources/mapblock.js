(function() {

  "use strict";

    var setMapHeight = function(maps){
      maps.each(function(index, map){
        $(map).css('height', $(map).width() / 3 * 2);
      });
    };

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

              setMapHeight(maps);
              maps.collectivegeo();
            }

          });
        }
      }
    };

    $(window).on('load', function(){
      initGoogleMaps();
    });

    $(document).on('blockMoved', function(event, data){
      var map = data.element.find('.blockwidget-cgmap');
      setMapHeight(map);
      map.collectivegeo('refresh');
    });


  $(function() {
    $(document).on("onBeforeClose", ".overlay", function() {
      if ($.fn.collectivegeo) {
        var map = $(".blockwidget-cgmap").filter(":visible");
        setMapHeight(map);
        map.collectivegeo();
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

          // get hidden maps (maps with no size yet)
          maps = $('.blockwidget-cgmap').filter(':hidden');
          if (maps.length > 0) {
              var tabs = $('select.formTabs, ul.formTabs');
              tabs.bind("onClick", function (e, index) {
                  var curpanel = $(this).data('tabs').getCurrentPane();
                  curpanel.find('.blockwidget-cgmap').collectivegeo(); // refresh
                  curpanel.find('.map-widget .blockwidget-cgmap').collectivegeo('add_edit_layer');
                  curpanel.find('.map-widget .blockwidget-cgmap').collectivegeo('add_geocoder');
              });
          }

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

