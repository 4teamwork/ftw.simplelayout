(function($){
  $.fn.simplelayout = function(options){

    // Defaults extended by given options
    var settings = $.extend({
      'blocks': '.sl-block',
      'columns': 2, // default is 2 possible columns
      'contentarea': '#content',
      'contentwidth': 960, // REQUERES A STATIC WITH
    }, options);

    function get_grid(){
      return settings.contentwidth / settings.columns;
    }

    function init($container, $blocks){
      // Simplelayout depends on a fixed with content layout
      $(settings.contentarea).css('width', settings.contentwidth);
      $blocks.css('width', settings.contentwidth);

      // masonry
      console.info(settings.contentwidth / settings.columns);
      $container.masonry({
          itemSelector: settings.blocks,
          isResizable: true
          //columnWidth: get_grid()
          });

      // resize
      $blocks.resizable({
          grid: [ get_grid(), 10 ],
          minWidth: get_grid(),
          maxWidth: settings.contentwidth,
          resize: function( event, ui ) {
              ui.element.parent().masonry('reload');
          }
      });

      // sortable
      $container.sortable({
          distance: 12,
          forcePlaceholderSize: true,
          items: settings.blocks,
          placeholder: {
              element: function(current_item){
                  var placeholder = $('<li class="block-sortable-placeholder sl-block"></li>'); // use settings.blocks
                  placeholder.css('width', current_item.css('width'));
                  placeholder.css('height', current_item.css('height'));
                  return placeholder[0];
              },
              update: function(container, p){return;}
          },
          tolerance: 'pointer',

          start:  function(event, ui) {
              ui.item.addClass('dragging').removeClass('sl-block');
              if ( ui.item.hasClass('bigun') ) {
                   ui.placeholder.addClass('bigun');
                   }
                     ui.item.parent().masonry('reload');
                  },
          change: function(event, ui) {
                     ui.item.parent().masonry('reload');
                  },
          stop:   function(event, ui) {
                     ui.item.removeClass('dragging').addClass('sl-block');
                     ui.item.parent().masonry('reload');
          }
     });



    }

    return this.each(function(){
          var $container = $(this);
          var $blocks = $(settings.blocks, $container);

          init($container, $blocks);

    });


  };

})(jQuery);
