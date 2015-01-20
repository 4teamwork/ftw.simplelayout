$(document).ready(function() {
  var target = $('#content-core');

  var simplelayout = new Simplelayout();
  var toolbox = new Toolbox({
    layouts: [1, 2, 4]
  });

  simplelayout.attachTo(target);
  toolbox.attachTo(target);
  simplelayout.attachToolbox(toolbox);


  var overlay = new Overlay();
  simplelayout.getLayoutmanager().getElement().on('blockInserted', function(event, layoutId, columnId, blockId) {
    var block = simplelayout.getLayoutmanager().getLayouts()[layoutId].getColumns()[columnId].getBlocks()[blockId];
    simplelayout.getLayoutmanager().getElement().off('blocksCommitted').on('blocksCommitted', function(event, layoutId, columnId) {
      $.post('http://localhost:8080/plattform/testpage/++add++ftw.simplelayout.TextBlock', function(data) {
        var form = $('#form', data);
        var html = $("<div>").append(form.clone()).html();
        overlay.open(html);
        $(document).off('submit').on('submit', form, function(e) {
          e.preventDefault();
          overlay.close();
          console.log(block.getElement().data());
          block.content('<p>content changed</p>');
        });
      });
    });
  });
});
