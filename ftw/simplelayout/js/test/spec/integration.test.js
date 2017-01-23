import Toolbox from "toolbox/Toolbox";
import Simplelayout from "simplelayout/Simplelayout";
import $ from "jquery";

describe("Integration", function() {

  var simplelayout;
  var manager;

  beforeAll(function() {
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
  });

  it("creates toolbar on layout with given layoutactions from toolbox", function() {
    var layout = manager.insertLayout().commit();

    assert.deepEqual($.map(layout.element.find(".sl-toolbar-layout a"), function(action) {
      return action.className;
    }), ["edit", "move"]);
  });

  it("creates toolbar on block with given blockactions from toolbox", function() {
    var layout = manager.insertLayout().commit();
    var block = layout.insertBlock("<p></p>", "textblock").commit();

    assert.deepEqual($.map(block.element.find(".sl-toolbar-block a"), function(action) {
      return action.className;
    }), ["edit", "move"]);
  });

  it("does not create toolbar for layouts if layout edit is inactive", function() {
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
