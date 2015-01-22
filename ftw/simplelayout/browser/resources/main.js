$(document).ready(function() {

  var target = $('#content-core'),
  componentRequest = $.get('./addable-blocks.json'),
  toolbox,
  simplelayout,
  formHtml,
  block,
  dummyAnchor,
  formUrl,
  blockPosted = false,

  createOverlay = function(target) {
    dummyAnchor = $('<a>').attr('href', target);
    dummyAnchor.prepOverlay({
      subtype: 'ajax',
      formselector: 'form',
      noform: function(data, overlay) {
        var uid = $('.sl-block-content', data).data('uid');
        block.uid = uid;
        block.content($('.sl-block-content', data).html());
        return 'close';
      },
      afterpost: function() {
        blockPosted = true;
      },
      closeselector: '[name="form.buttons.cancel"]',
      config: {
        onLoad: function() {
          if (window.initTinyMCE) {
            window.initTinyMCE(document);
          }
        },
        onClose: function() {
          if (!blockPosted) {
            var layoutId = block.getElement().data('layoutId');
            var columnId = block.getElement().data('columnId');
            var blockId = block.getElement().data('blockId');
            simplelayout.getLayoutmanager().deleteBlock(layoutId, columnId, blockId);
          }
          blockPosted = false;
        }

      }
    });
  };

  componentRequest.done(function(data) {
    toolbox = new Toolbox({
      layouts: [1, 2, 4],
      components: data
    });
    simplelayout = new Simplelayout({
      width: '900px'
    });
    simplelayout.attachTo(target);
    toolbox.attachTo(target);
    simplelayout.attachToolbox(toolbox);

    simplelayout.getToolbox().getElement().find('.sl-toolbox-component').on('dragstart', function(e) {
      formUrl = $(e.target).data('form_url');
    });

    simplelayout.getLayoutmanager().getElement().on('blockInserted', function(event, layoutId, columnId, blockId) {
      block = simplelayout.getLayoutmanager().getLayouts()[layoutId].getColumns()[columnId].getBlocks()[blockId];
    });

    simplelayout.getLayoutmanager().getElement().on('blocksCommitted', function(event, layoutId, columnId) {
      createOverlay(formUrl);
      dummyAnchor.trigger('click');
    });
  });

  componentRequest.fail(function(textStatus) {
    console.error(textStatus);
  });
});
