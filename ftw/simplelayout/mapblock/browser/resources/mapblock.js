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

    // XXX - Since I'm not able to set the map zoom level correct in any other way
    // XXX - This satanic option is my most economic solution so far.
    $(window).on('maploadend', function(event, map){
      setTimeout(function(){
          map.map.setCenter(map.map.center, map.settings.zoom);
        }, 200);


        // Set base layer based on settings
        var maplayer = $(map.trigger).data('maplayer');
        if (maplayer) {
          var initLayer = map.map.getLayersByName(maplayer);
          map.map.setBaseLayer(initLayer[0]);
        }

    });

    function initEdit(mapWidgets) {

      if (mapWidgets.length === 0) {
        return;
      }

      mapWidgets.collectivegeo();
      mapWidgets.collectivegeo("add_edit_layer");
      mapWidgets.collectivegeo("add_geocoder");

      var ol_map = mapWidgets.data('collectivegeo').mapwidget.map;
      ol_map.events.register('zoomend', ol_map, function(event){
        var zoom = event.object.zoom;
        var zoomField = $('#form-widgets-zoomlevel');

        if (zoomField !== undefined) {
          zoomField.val(zoom);
        }
      });

      ol_map.events.register('changebaselayer', ol_map, function(event){
        var layer = event.object.baseLayer.name;
        var layerField = $('#form-widgets-maplayer');
        if (layerField !== undefined) {
          layerField.val(layer);
        }
      });

      // Fix mouse pointer position according to openlayers pointer
      $(mapWidgets.closest(".pb-ajax")).on("scroll", function(){
        mapWidgets.collectivegeo("refresh");
      });
    }

    window.MapBlockEditInitializer = function() {
      if ($.fn.collectivegeo) {
        var mapWidgets = $(".map-widget .blockwidget-cgmap").filter(":visible");
        initEdit(mapWidgets);

        if (mapWidgets.data('collectivegeo') === undefined) {
          // No widget initialized
          // Get hidden maps (maps with no size yet)
          if ($('.blockwidget-cgmap').filter(':hidden').length > 0) {
              var tabs = $('select.formTabs, ul.formTabs');
              tabs.bind("onClick", function (e, index) {
                initGoogleMaps();
                var curpanel = $(this).data('tabs').getCurrentPane();
                initEdit(curpanel.find('.blockwidget-cgmap'));
              });
          }
          return;
        }
      }
    };

    $(document).on("onLoad", ".overlay", function() {

      if (typeof google === 'object' && typeof google.maps === 'object'){
        window.MapBlockEditInitializer();
      } else {
        initGoogleMaps('MapBlockEditInitializer');
      }

    });
  });

  $(window).on('load', function(){
    initGoogleMaps();
    window.MapBlockEditInitializer();
  });

})();

