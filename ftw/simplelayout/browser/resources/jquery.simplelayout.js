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
   margin_right: 10,
   resizeheightstep: 10}

Private methods:
  - get_grid (calculates the grid size)
  - controls (Loads edit /
              delete action for each block)

Events:
  - "sl-block-reloaded" This event is triggered after a block has succesfully
    reloaded. An additional data argument is passed if you bind this event.
    The data argument contains the settings and the current simplelayout
    container.

**********************************************/

(function($){

    // Private functions

    function get_grid(settings){
        return settings.contentwidth / settings.columns;
    }

    function get_image_grid(settings){
        return settings.contentwidth / settings.columns / settings.images;
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
        async: false,
        data: form_data,
        success: function(data){
          var uuid = JSON.parse(data).uuid;

          $('.block-view-wrapper', $block).load(
            './@@sl-ajax-reload-block-view', {uuid: uuid}, function(data){
              $block.data('uuid', uuid);
              $block.removeClass('sl-add-block');
              $block.closest('.simplelayout').masonry('reload').simplelayout('save').simplelayout('layout');
              blockcontrols($block);
              imagecontrols($block);
            });
        },

        error: function(xhr, status, error){
          alert(status, error);
        }


      });

    }
    function reload_block(e){
      var $block = $(this);
      var uuid = $block.data('uuid');

      $('.block-view-wrapper', $block).load(
        './@@sl-ajax-reload-block-view',
        {uuid: uuid},
        function(){
          $block.trigger('sl-block-reloaded',
                         {settings: e.data.settings,
                          container: e.data.container});
        });
      return;
    }

    function blockcontrols($blocks){

      // Menu
      var $toggler = $('.sl-controls-toggler', $blocks);
      $toggler.bind('click', function(){
        var $this = $(this);
        var $block = $this.closest('.sl-block');

        if ($('.sl-controls', $block).length === 0){

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
                  $block.trigger('sl-block-reload');
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
          $('.sl-controls', $block).toggle();
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

              $container.masonry('reload').simplelayout('save').simplelayout('layout');
              blockcontrols($newblock);
              return 'close';
            },
            closeselector: '[name="form.buttons.cancel"]',
            appendTopost: function(data, overlay){
              console.info('appendTopost');
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

    function imagecontrols($blocks){
      var floatleft = $('<span class="imagefloat left ui-icon ui-icon-arrowthickstop-1-w" />').hide();
      var floatright = $('<span class="imagefloat right ui-icon ui-icon-arrowthickstop-1-e" />').hide();
      var floatnone = $('<span class="imagefloat none ui-icon ui-icon-arrowthick-2-e-w" />').hide();

      floatright.appendTo($('.sl-img-wrapper', $blocks));
      floatleft.appendTo($('.sl-img-wrapper', $blocks));
      floatnone.appendTo($('.sl-img-wrapper', $blocks));

      function change_image_float($el, direction){
        $block = $el.parents('.sl-block');
        $('.sl-img-wrapper img', $block).css('float', direction);
        $block.parents('.simplelayout').simplelayout('save', function(){
          $block.trigger('sl-block-reload');
        });
      }

      $('.sl-img-wrapper', $blocks).on('mouseenter',
        function(e){
          // Handler in
          e.stopPropagation();
          e.preventDefault();

          var $this = $(this);
          var floatleft = $('.imagefloat.left', $this);
          var floatright = $('.imagefloat.right', $this);
          var floatnone = $('.imagefloat.none', $this);

          floatleft.on('click', function(){change_image_float($(this), 'left');});
          floatright.on('click', function(){change_image_float($(this), 'right');});
          floatnone.on('click', function(){change_image_float($(this), 'none');});

          var $img = $('img', $this);

          var floatcss = $img.css('float');

          if (floatcss === 'none'){
            floatright.css('position', 'absolute')
                      .css('top', $img.height() / 2)
                      .css('left', $img.width() - floatright.width())
                      .show();
            floatleft.css('position', 'absolute')
                      .css('top', $img.height() / 2)
                      .css('left', 0)
                      .show();

          } else if (floatcss === 'left') {
            floatright.css('position', 'absolute')
                      .css('top', $img.height() / 2)
                      .css('left', $img.width() - floatleft.width())
                      .show();
            floatnone.css('position', 'absolute')
                      .css('top', $img.height() / 2)
                      .css('left', $img.width() / 2)
                      .show();

          } else if (floatcss === 'right') {
            floatleft.css('position', 'absolute')
                      .css('top', $img.height() / 2)
                      .css('right', $img.width() - 5) // Fix resizable space
                      .show();
            floatnone.css('position', 'absolute')
                      .css('top', $img.height() / 2)
                      .css('right', $img.width() / 2)
                      .show();
          }

        }).on('mouseleave', function(){
          var $this = $(this);
          var floatleft = $('.imagefloat.left', $this);
          var floatright = $('.imagefloat.right', $this);
          var floatnone = $('.imagefloat.none', $this);

          floatright.hide();
          floatleft.hide();
          floatnone.hide();
        });
    }

    function dndupload($element, settings){
      var counter = 0;
      $element.on('dragenter', function (e){
        e.stopPropagation();
        e.preventDefault();

        if (counter === 0) {
          console.info('entered the page');
        }
        counter++;


        if ($('.sl-add-block', $element).length === 0){
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
            $element.prepend($block);
          });

          $element.masonry('reload');
        }
      });

      $element.on('drop', function(e){
        e.stopPropagation();
        e.preventDefault();

        var files = e.originalEvent.dataTransfer.files;
        var $addblocks = $('.sl-add-block', $(this));

        $.each(files, function(index, file){
          var $block = $addblocks.eq(index);
          $('.block-view-wrapper', $block).html('uploading... ' + file.name);

          var data = new FormData();
          data.append('image', file);
          data.append('filename', file.name);

          send_file_to_server(data, $block);
        });

      });

      $element.on('dragleave', function (e) {

        if (--counter === 0) {
          console.info('leave');
          $('.sl-add-block', $element).remove();
          $element.masonry('reload');

        }
      });

      $(document).on('dragover', function (e)
      {
        e.stopPropagation();
        e.preventDefault();
      });

    }

    // Public functions

    var methods = {
        init: function(options){
            return this.each(function(){
                var $this = $(this);
                var settings = $this.data('simplelayout');

                var local_config = $this.data('simplelayout-config');
                if (local_config !== undefined){
                  options = local_config;
                }

                if(typeof(settings) == 'undefined') {
                    var defaults = {
                        blocks: '.sl-block',
                        columns: 2, // default is 2 possible columns
                        images: 2, // image columns
                        contentarea: '#content',
                        margin_right: 10, // Margin right in px
                        contentwidth: 960, // REQUERES A STATIC WIDTH
                        resizeheightstep: 10,
                        editable: false};

                        settings = $.extend({}, defaults, options);
                } else {
                    settings = $.extend({}, settings, options);
                }

                $this.data('simplelayout', settings);

                // Load controls
                if (settings.editable){
                  var $blocks = $(settings.blocks, $this);
                  blockcontrols($blocks);
                  addblock($this);
                  imagecontrols($blocks);
                  dndupload($this, settings);

                  // Events
                  $blocks.bind(
                    'sl-block-reload',
                    {settings: settings, container: $this},
                    reload_block);

                  $blocks.bind('sl-block-reloaded', function(e, data){
                      var $block = $(this);
                      data.container.simplelayout('layout');
                      imagecontrols($block);
                      // Hide menu
                      $('.sl-controls:visible', $block).hide();

                  });

                }


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

            if (settings.editable){
              $this.sortable('destroy');
              $blocks.resizable('destroy');
              $('.sl-img-wrapper img', $blocks).resizable('destroy');
            }

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

            // Apply padding to all block-view-wrapper
            $('.block-view-wrapper', $blocks).css('margin-right', settings.margin_right);

            // Apply contentwith to container
            $this.css('max-width', settings.contentwidth);

            // masonry
            $this.masonry({
                itemSelector: settings.blocks,
                isResizable: true,
                columnWidth: grid
                });

            if (!settings.editable){
              return;
            }

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

                      var img = ui.element.find('img');
                      var imagegrid = get_image_grid(settings);
                      var orig_with_in_columns = ui.originalSize.width / grid;
                      var new_with_in_columns = ui.element.width() / grid;
                      var diff_in_columns = new_with_in_columns - orig_with_in_columns;
                      var img_width_in_columns = (img.width() + settings.margin_right) / imagegrid;
                      var new_img_width_in_columns = img_width_in_columns + diff_in_columns;
                      var new_img_width;

                      if (new_img_width_in_columns < 1){
                        // The image can not be smaller than one image column.
                        new_img_width = imagegrid - settings.margin_right;

                      } else if (img_width_in_columns / settings.images === orig_with_in_columns){
                        // Special case if the image has the same size as the block.
                        new_img_width = new_with_in_columns * settings.images * imagegrid - settings.margin_right;

                      } else if (new_img_width_in_columns / settings.images > new_with_in_columns) {
                        // The image can not be bigger than the block.
                        new_img_width = new_with_in_columns * settings.images * imagegrid - settings.margin_right;

                      } else {
                        // Asynchronous resize
                        new_img_width = new_img_width_in_columns * imagegrid - settings.margin_right;
                      }
                      img.resizable('disable');

                      img.width(new_img_width).height('auto');
                      img.parent().width(new_img_width).height('auto');
                      img.resizable('enable');

                      $this.simplelayout('save', function(){
                        ui.element.trigger('sl-block-reload');
                      });

                    });
                }
            });

            // Image resize
            var image_grid = get_image_grid(settings);
            $('.sl-img-wrapper img', $blocks).resizable({
                containment: ".block-wrapper",
                handles: "e, w",
                zIndex: 91,
                grid: [image_grid, 1],
                minWidth: image_grid - settings.margin_right,
                resize: function(event, ui){
                  // Set height to preserve img ratio.
                  // Manually, because aspectRatio does not work with grid option.
                  var img = ui.originalElement;
                  var ratio = img.attr('width') / img.attr('height');
                  ui.element.height(ui.element.width() / ratio);
                },
                stop: function(event, ui){
                  var img = ui.originalElement;
                  $this.simplelayout('save', function(){
                    img.parents('.sl-block').trigger('sl-block-reload');
                  });
                }
            });

            // sortable
            $this.sortable({
                distance: 1,
                forcePlaceholderSize: true,
                items: settings.blocks,
                connectWith: '[id^=sl-slot-]',
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
                             ui.item.parent().simplelayout('save');
                           });

                }
            });
          });
        },

        save: function(callback){
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
              var $item = $(item);
              var $img = $('img', $item);
              var imagestyles = false;

              if ($img.length !== 0){
                imagestyles = 'width:' + $img.css('width') + ';float: ' + $img.css('float') + ';';
              }

              payload.push({
                'uuid': $item.data('uuid'),
                'slot': $this.attr('id'),
                'position': $item.position(),
                'size': {'width': $item.width(), 'height': $item.height()},
                'imagestyles': imagestyles
              });
            });

            $.ajax('./sl-ajax-save-state',
                   {cache: false,
                    data: {'payload': JSON.stringify(payload)},
                    dataType:'json',
                    type: 'POST',
                    success: function(data, textStatus, jqXHR){
                      console.info(data);
                      if(typeof callback === 'function'){
                        callback.call(this, data);
                      }
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
