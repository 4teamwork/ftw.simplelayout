import Toolbox from "toolbox/Toolbox";
import Simplelayout from "simplelayout/Simplelayout";
import $ from "jquery";

describe("Integration", function() {

  var simplelayout;
  var manager;

  beforeEach(function() {
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
            edit: {"class": "edit", "title": "Can edit this block", "rules": [1, 2, 3, 4]},
            move: {"class": "move", "title": "Can move this block", "rules": [1, 2, 3, 4]},
            ratio: {"class": "specific-ratio", "title": "specific ratio", "rules": [2]},
            all: {"class": "all", "title": "all"},
          }
        })
      });
      manager = simplelayout.insertManager();
  });

  it("creates toolbar on block with given blockactions from toolbox", function(done) {
    var layout = manager.insertLayout().commit();

    simplelayout.on("toolbar-attached", (block) => {
      expect($.map(block.element.find(".sl-toolbar-block a"), function(action) {
        return action.className;
      })).toEqual(["edit", "move"]);
      done();
    });

    var block = layout.insertBlock("<p></p>", "textblock").commit();
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
    }), ["edit", "move", "all"]);
  });

  it("should restore all block toolbars containing the layout", (done) => {
    const layout = manager.insertLayout().commit();
    simplelayout.on("toolbar-attached", function() {
      simplelayout.on("toolbar-attached", function() {
        expect($.map(layout.blocks, (block) => {
          return block.element.find(".sl-toolbar-block").length;
        })).toEqual([1, 1]);
        done();
      });
    });

    layout.content(
      "<div data-type='textblock' class='sl-block'></div><div data-type='textblock' class='sl-block'></div>"
    );
  });

  it("a layout should only have its configured actions", () => {
    const layout4 = manager.insertLayout(4).commit();
    const layout2 = manager.insertLayout(2).commit();

    assert.deepEqual($.map(layout2.element.find(".sl-toolbar-layout a"), function(action) {
      return action.className;
    }), ["edit", "move", "specific-ratio", "all"]);

    assert.deepEqual($.map(layout4.element.find(".sl-toolbar-layout a"), function(action) {
      return action.className;
    }), ["edit", "move", "all"]);
  });

  it("an action with no rules should be applied to all layouts", () => {
    const layout1 = manager.insertLayout(1).commit();
    const layout2 = manager.insertLayout(2).commit();
    const layout4 = manager.insertLayout(4).commit();

    assert.deepEqual($.map(layout1.element.find(".sl-toolbar-layout a"), function(action) {
      return action.className;
    }), ["edit", "move", "all"]);

    assert.deepEqual($.map(layout2.element.find(".sl-toolbar-layout a"), function(action) {
      return action.className;
    }), ["edit", "move", "specific-ratio", "all"]);

    assert.deepEqual($.map(layout4.element.find(".sl-toolbar-layout a"), function(action) {
      return action.className;
    }), ["edit", "move", "all"]);
  });

});
