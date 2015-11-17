suite("Integration", function() {
  "use strict";

  var Toolbox;
  var Simplelayout;
  var simplelayout;
  var manager;

  suiteSetup(function(done) {
    require(["app/toolbox/Toolbox", "app/simplelayout/Simplelayout"], function(_Toolbox, _Simplelayout) {
      Toolbox = _Toolbox;
      Simplelayout = _Simplelayout;
      simplelayout = new Simplelayout({
        toolbox: new Toolbox({
          blocks: [
          {
            title: "Textblock",
            contentType: "textblock",
            formUrl: "URL",
            actions: {
              edit: {"class": "edit", "title": "Can edit this block"},
              move: {"class": "move", "title": "Can edit this block"}
            }
          }],
          layoutActions: {
            edit: {"class": "edit", "title": "Can edit this block"},
            move: {"class": "move", "title": "Can move this block"}
          }
        })
      });
      manager = simplelayout.insertManager();
      done();
    });
  });

  test("creates toolbar on layout with given layoutactions from toolbox", function() {
    var layout = manager.insertLayout().commit();

    assert.deepEqual($.map(layout.element.find(".sl-toolbar-layout a"), function(action) {
      return action.className;
    }), ["edit", "move"]);
  });

  test("creates toolbar on block with given blockactions from toolbox", function() {
    var layout = manager.insertLayout().commit();
    var block = layout.insertBlock("<p></p>", "textblock").commit();

    assert.deepEqual($.map(block.element.find(".sl-toolbar-block a"), function(action) {
      return action.className;
    }), ["edit", "move"]);
  });

  test("does not create toolbar for layouts if layout edit is inactive", function() {
    simplelayout.options.editLayouts = false;
    var layout = manager.insertLayout().commit();
    layout.insertBlock("<p></p>", "textblock").commit();

    assert.deepEqual($.map(layout.element.find(".sl-toolbar-layout a"), function(action) {
      return action.className;
    }), []);

    simplelayout.options.editLayouts = true;
    layout = manager.insertLayout().commit();
    layout.insertBlock("<p></p>", "textblock").commit();

    assert.deepEqual($.map(layout.element.find(".sl-toolbar-layout a"), function(action) {
      return action.className;
    }), ["edit", "move"]);
  });

});
