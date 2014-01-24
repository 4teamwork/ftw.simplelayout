(function($){
  $.fn.simplelayout = function(options){
    this.settings = {};

    function get_grid(){
      return this.settings.contentwidth / this.settings.columns;
    }

    function save_state(items){
      var payload = [];

      items.each(function(i, item){
        $item = $(item);
        payload.push({
          'uuid': $item.data('uuid'),
          'position': $item.position(),
          'size': {'width': $item.width(), 'height': $item.height()}
        });
      });

      $.ajax('./sl-ajax-save-state',
             {cache: false,
              data: {'payload': JSON.stringify(payload)},
              dataType:'json',
              type: 'POST',
              success: function(data, textStatus, jqXHR){
                console.info(data);
              },
              error: function(xhr, status,error){
                alert(status, error);
              }
      });
    }


    function init(element, options){

      this.settings = $.extend({
        'blocks': '.sl-block',
        'columns': 2, // default is 2 possible columns
        'contentarea': '#content',
        'contentwidth': 960, // REQUERES A STATIC WIDTH
        'resizeheightstep': 10,
      }, options);

      var $container = $(element);
      var $blocks = $(this.settings.blocks, $container);



      // Simplelayout depends on a fixed with content layout
      $(this.settings.contentarea).css('width', this.settings.contentwidth);

      // masonry
      $container.masonry({
          itemSelector: this.settings.blocks,
          isResizable: true,
          columnWidth: get_grid()
          });

      // resize
      $blocks.resizable({
          grid: [get_grid(), this.settings.resizeheightstep],
          minWidth: get_grid(),
          maxWidth: this.settings.contentwidth,
          resize: function( event, ui ) {
              ui.element.parent().masonry('reload');
          },
          stop: function(event, ui){
              ui.element.parent().masonry('reload', function(){
                save_state(this);
              });
          }

      });

      // sortable
      $container.sortable({
          distance: 1,
          forcePlaceholderSize: true,
          items: this.settings.blocks,
          placeholder: {
              element: function(current_item){
                  var placeholder = $('<div class="block-sortable-placeholder sl-block"></div>'); // use settings.blocks
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
                     ui.item.parent().masonry('reload', function(){
                       save_state(this);
                     });

          }
     });



    }

    return this.each(function(){

          init(this, options);

    });


  };

})(jQuery);
