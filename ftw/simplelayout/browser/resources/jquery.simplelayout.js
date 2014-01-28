(function($){

    function get_grid(settings){
        return settings.contentwidth / settings.columns;
    }

    var methods = {
        init: function(options){
            return this.each(function(){
                var $this = $(this);
                var settings = $this.data('simplelayout');

                if(typeof(settings) == 'undefined') {
                    var defaults = {
                        blocks: '.sl-block',
                        columns: 2, // default is 2 possible columns
                        contentarea: '#content',
                        contentwidth: 960, // REQUERES A STATIC WIDTH
                        resizeheightstep: 10};

                        settings = $.extend({}, defaults, options);
                } else {
                    settings = $.extend({}, settings, options);
                }

                $this.data('simplelayout', settings);

            });
        },

        layout: function(options){

          return this.each(function(){
            var $this = $(this);
            var settings = $this.data('simplelayout');

            if(typeof(settings) == 'undefined'){
              console.info('Initialize plugin first, using $("SELECTOR").simplelayout("init", options)');
              return;
            }

            var $blocks = $(settings.blocks, $this);
            var grid = get_grid(settings);

            // masonry
            $this.masonry({
                itemSelector: settings.blocks,
                isResizable: true,
                columnWidth: grid
                });

            // resize
            $blocks.resizable({
                grid: [grid, settings.resizeheightstep],
                minWidth: grid,
                maxWidth: settings.contentwidth,
                resize: function( event, ui ) {
                    ui.element.parent().masonry('reload');
                },
                stop: function(event, ui){
                    ui.element.parent().masonry('reload', function(){
                      $this.simplelayout('save');
                    });
                }

            });

            // sortable
            $this.sortable({
                distance: 1,
                forcePlaceholderSize: true,
                items: settings.blocks,
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
                             $this.simplelayout('save');
                           });

                }
            });
          });
        },

        save: function(options){
          return this.each(function(){
            var $this = $(this);
            var settings = $this.data('simplelayout');

            if(typeof(settings) == 'undefined'){
              console.info('Initialize plugin first, using $("SELECTOR").simplelayout("init", options)');
              return;
            }

            var $blocks = $(settings.blocks, $this);
            var payload = [];

            $blocks.each(function(i, item){
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
          });

        }

    };



    $.fn.simplelayout = function(options){

      var method = arguments[0];

      if(methods[method]) {
        method = methods[method];
        arguments = Array.prototype.slice.call(arguments, 1);
      } else if( typeof(method) == 'object' || !method ) {
        method = methods.init;
      } else {
        $.error( 'Method ' +  method + ' does not exist on jQuery.pluginName' );
        return this;
      }

      return method.apply(this, arguments);

    };
})(jQuery);
