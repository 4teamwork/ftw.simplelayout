$(function(){
  $(document).on('onBeforeClose', '.overlay', function(){
    if ($.fn.collectivegeo) {
      $('.widget-cgmap').filter(':visible').collectivegeo();
    }
  });

  $(document).on('onLoad', '.overlay', function(){
    if ($.fn.collectivegeo) {
      var maps = $('.widget-cgmap').filter(':visible');
      var map_widgets = $('.map-widget .widget-cgmap').filter(':visible');
      maps.collectivegeo();
      map_widgets.collectivegeo('add_edit_layer');
      map_widgets.collectivegeo('add_geocoder');
    }
  });
});