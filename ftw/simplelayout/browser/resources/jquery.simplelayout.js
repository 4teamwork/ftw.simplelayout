/**********************************************
Simplaylout jQuery plugin
----------------------------
Version: 1.0a1
Author: Mathias Leimgruber
Dependencies:
  - jQuery Masonry v2.1.08
  - jQuery UI v1.8
    - jQuery UI sortable
    - jQuery UI resize

Usage:

Initialize...
  $(SELECTOR).simplelayout();
  $(SELECTOR).simplelayout(options);
  $(SELECTOR).simplelayout('init', options);

Arrange blocks...
  $(SELECTOR).simplelayout('layout')

Save block states...
  $(SELECTOR).simplelayout('save')

Destroy... (If you want)
  $(SELECTOR).simplelayout('destroy')

Default configuration:
  {blocks: '.sl-block',
   columns: 2,
   contentarea: '#content',
   contentwidth: 960,
   resizeheightstep: 10}

Private methods:
  - get_grid (calculates the grid size)
  - controls (Loads edit /
              delete action for each block)

**********************************************/

(function($){

    // Private functions

    function get_grid(settings){
        return settings.contentwidth / settings.columns;
    }

    function send_file_to_server(form_data, $block){
      // Example from http://hayageek.com/drag-and-drop-file-upload-jquery
      var upload_url = './sl-ajax-image-upload';

      var $xhr = $.ajax({
        xhr: function(){
          var xhrobj = $.ajaxSettings.xhr();
          // Implement Progressbar
          return xhrobj;
        },
        url: upload_url,
        type: 'POST',
        contentType: false,
        processData: false,
        cache: false,
        data: form_data,
        success: function(data){
          var uuid = JSON.parse(data).uuid;

          $('.block-view-wrapper', $block).load(
            './@@sl-ajax-reload-block-view', {uuid: uuid}, function(data){
              $block.data('uuid', uuid);
              $block.removeClass('sl-add-block');
              $block.closest('.simplelayout').masonry('reload').simplelayout('save');
              blockcontrols($block);
            });
        },

        error: function(xhr, status, error){
          alert(status, error);
        }


      });

    }

    function blockcontrols($blocks){

      // Menu
      var $toggler = $('.sl-controls-toggler', $blocks);
      $toggler.bind('click', function(){
        var $this = $(this);
        if (!$this.next().hasClass('sl-controls')){

          var $block = $this.closest('.sl-block');
          var uuid = $block.data('uuid');
          $.get('./sl-ajax-block-controls', {uuid: uuid}, function(data){
            $this.after(data);

              // Edit
              $('.sl-edit a', $block).prepOverlay({
                subtype: 'ajax',
                filter: "#content",
                formselector: 'form',
                noform:function(data, overlay){
                  var $block = overlay.source.closest('.sl-block');
                  var uuid = $block.data('uuid');
                  $('.block-view-wrapper', $block).load('./@@sl-ajax-reload-block-view',
                              {uuid: uuid});
                  // hide menu
                  $('.sl-controls-toggler', $block).next().hide();
                  return 'close';
                  },

                closeselector: '[name="form.button.cancel"]',
                config: {
                  onLoad: function () {
                    if (window.initTinyMCE) {
                      window.initTinyMCE(document);
                    }
                  }
                }
              });

              // Delete
              $('.sl-delete a').prepOverlay({
                subtype:'ajax',
                urlmatch:'$',urlreplace:' #content > *',
                formselector:'[action*="delete_confirmation"]',
                noform:function(data, overlay){
                  var $container = overlay.source.closest('.simplelayout');
                  overlay.source.closest('.sl-block').remove();
                  $container.masonry('reload');
                  return 'close';
                  },
                'closeselector':'[name="form.button.Cancel"]'
                });
          });

        } else {
          $this.next().toggle();
        }

      });

    }

    function addblock($container){
      var settings = $container.data('simplelayout');
      var $addlink = $container.prev();

      $addlink.bind('click', function(e){
        e.stopPropagation();
        e.preventDefault();

        if ($container.find('.sl-add-block').length !== 0){
          // Only one add block is allowed
          return;
        }

        var $block = $(
          '<div style="width:' + settings.contentwidth + 'px" ' +
               'class="sl-add-block '+ settings.blocks.slice(1) + '">'+
          '</div>');
        $container.prepend($block);
        $block.load('./@@addable-blocks-view', function(data){

          $('.sl-addable-blocks a').prepOverlay({
            subtype: 'ajax',
            filter: "#content",
            formselector: 'form',
            noform: function(data, overlay){
              var $newblock = $('.sl-block', data).eq(-1);
              $newblock.attr('style', $block.attr('style'));
              $('.sl-add-block', $container).replaceWith($newblock);

              $container.masonry('reload');
              $container.simplelayout('save');
              blockcontrols($newblock);
              return 'close';
            },
            closeselector: '[name="form.buttons.cancel"]',
            afterpost: function(data, overlay){
              console.info('afterpost');
            },
            config: {
              onLoad: function () {
                if (window.initTinyMCE) {
                  window.initTinyMCE(document);
                }
              }

            }


          });

          $container.simplelayout('layout');
          $container.masonry('reload');
        });

      });


    }

    // Public functions

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

                // Load controls
                blockcontrols((settings.blocks, $this));
                addblock($this);

                /******** THIS IS SOME FANCY IMAGE UPLOAD STUFF - JUST PLAYING ARROUND *************/

                var counter = 0;
                $this.on('dragenter', function (e){
                  e.stopPropagation();
                  e.preventDefault();

                  if (counter === 0) {
                    console.info('entered the page');
                  }
                  counter++;


                  if ($('.sl-add-block', $this).length === 0){
                    var files = e.originalEvent.dataTransfer.items;
                    $.each(files, function(index, file){
                      var $block = $(
                        '<div style="width:' + get_grid(settings) + 'px" ' +
                             'class="sl-add-block '+ settings.blocks.slice(1) + '">'+
                                '<span class="ui-icon ui-icon-document sl-controls-toggler">' +
                                '<!-- --></span>' +

                             '<div class="block-wrapper">' +
                               '<div class="block-view-wrapper">' + file + '</div>' +
                             '</div>' +
                        '</div>');
                      $this.prepend($block);
                    });

                    $this.masonry('reload');
                  }
                });

                $this.on('drop', function(e){
                  e.stopPropagation();
                  e.preventDefault();

                  var files = e.originalEvent.dataTransfer.files;
                  var $blocks = $('.sl-add-block', $(this));

                  $.each(files, function(index, file){
                    var $block = $blocks.eq(index);
                    $('.block-view-wrapper', $block).html('uploading... ' + file.name);

                    var data = new FormData();
                    data.append('image', file);
                    data.append('filename', file.name);

                    send_file_to_server(data, $block);
                  });

                });

                $this.on('dragleave', function (e) {

                  if (--counter === 0) {
                    console.info('leave');
                    $('.sl-add-block', $this).remove();
                    $this.masonry('reload');

                  }
                });

                $(document).on('dragover', function (e)
                {
                  e.stopPropagation();
                  e.preventDefault();
                  //obj.css('border', '2px dotted #0B85A1');
                });

                /************************************************************/

            });
        },

        destroy: function(options) {
          return $(this).each(function() {
            var $this = $(this);
            var settings = $this.data('simplelayout');

            if(typeof(settings) == 'undefined'){
              console.info('Initialize plugin first, using $("SELECTOR").simplelayout("init", options)');
              return;
            }

            var $blocks = $(settings.blocks, $this);

            $this.removeData('simplelayout');
            $this.masonry('destroy');
            $this.sortable('destroy');
            $blocks.resizable('destroy');
          });
        },

        add: function(options){
          return this.each(function(){
            var $this = $(this);
            var settings = $this.data('simplelayout');

            if(typeof(settings) == 'undefined'){
              console.info('Initialize plugin first, using $("SELECTOR").simplelayout("init", options)');
              return;
            }

            $this.prev().click();

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

            if ($this.find('.sl-add-block').length !== 0){
              // The user is currently adding a new block - do store nothing.
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
