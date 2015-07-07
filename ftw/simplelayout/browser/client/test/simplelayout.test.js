suite("Simplelayout", function() {
  "use strict";

  var Simplelayout;
  var Toolbox;
  var simplelayout;
  var manager;
  var toolbox;

  suiteSetup(function(done) {
    require(["app/simplelayout/Simplelayout", "app/toolbox/Toolbox"], function(_Simplelayout, _Toolbox) {
      Toolbox = _Toolbox;
      toolbox = new Toolbox({
        layouts: [1, 2, 4],
        components: {
          textblock: {
            title: "Textblock",
            description: "can show text",
            contentType: "textblock",
            formUrl: "http://www.bing.com",
            actions: {
              edit: {
                class: "edit",
                description: "Edit this block"
              },
              move: {
                class: "move",
                description: "Move this block"
              }
            }
          }
        }
      });
      Simplelayout = _Simplelayout;
      done();
    });
  });

  setup(function(done) {
    simplelayout = new Simplelayout({toolbox: toolbox});
    manager = simplelayout.insertManager();
    done();
  });

  test("is a constructor function", function() {
    assert.throw(Simplelayout, TypeError, "Simplelayout constructor cannot be called as a function.");
  });

  test("manager stores information", function() { assert.deepEqual(manager.element.data("container"), 0); });

  test("layout stores information", function() {
    manager.insertLayout(4);
    var data = $.map(manager.layouts[0].element, function(e) {
      e = $(e);
      return { container: e.data().container, layoutId: e.data().layoutId };
    });
    assert.deepEqual(data, [{ container: 0, layoutId: 0 }]);
  });

  test("column stores information", function() {
    manager.insertLayout(4);
    var data = $.map(manager.layouts[0].columns, function(e) {
      data = e.element.data();
      return { container: data.container, layoutId: data.layoutId, columnId: data.columnId };
    });
    assert.deepEqual(data, [
      { container: 0, layoutId: 0, columnId: 0 },
      { container: 0, layoutId: 0, columnId: 1 },
      { container: 0, layoutId: 0, columnId: 2 },
      { container: 0, layoutId: 0, columnId: 3 }
    ]);
  });

  test("block stores information", function() {
    manager.insertLayout(4);
    manager.insertBlock(0, 0, null, "textblock");
    var data = $.map(manager.layouts[0].columns[0].blocks, function(e) {
      data = e.element.data();
      return { container: data.container, layoutId: data.layoutId, columnId: data.columnId, blockId: data.blockId };
    });
    assert.deepEqual(data, [
      { container: 0, layoutId: 0, columnId: 0, blockId: 0 } ]);
  });

  test("can move a layout", function() {
    var manager2 = simplelayout.insertManager();
    var layout = manager.insertLayout(4);
    manager.insertLayout(4);
    manager2.insertLayout(4);
    manager2.insertLayout(4);
    var block = manager.insertBlock(0, 0, null, "textblock");
    manager.insertBlock(0, 1, null, "textblock");
    manager.insertBlock(0, 2, null, "textblock");
    manager2.insertBlock(1, 0, null, "textblock");
    manager2.insertBlock(1, 1, null, "textblock");
    manager2.insertBlock(1, 2, null, "textblock");
    simplelayout.moveLayout(layout, manager2.element.data("container"));
    assert.deepEqual(layout.element.data(), { container: 1, layoutId: 2 });
    assert.deepEqual(block.element.data(), { blockId: 0, type: "textblock", columnId: 0, layoutId: 2, container: 1 });
  });

  test("can move a block", function() {
    var manager2 = simplelayout.insertManager();
    manager.insertLayout(4);
    manager2.insertLayout(4);
    var block = manager.insertBlock(0, 0, null, "textblock");
    block.commit();
    simplelayout.moveBlock(block, 1, 0, 0);
    var blocks = $.map(manager2.getCommittedBlocks(), function(e) {
      return e.element.data();
    });
    assert.deepEqual(blocks, [{ blockId: 0, type: "textblock", columnId: 0, layoutId: 0, container: 1 }]);
  });

  test("can get committed blocks", function() {
    var layout = manager.insertLayout(4);
    var block = layout.insertBlock(0, null, "textblock");
    assert.deepEqual([], $.map(simplelayout.getCommittedBlocks(), function(e) {
        return e.committed;
      }), "should have no committed blocks.");
    block.commit();
    assert.deepEqual([true], $.map(simplelayout.getCommittedBlocks(), function(e) {
        return e.committed;
      }), "should have one committed blocks.");
  });

  test("can get inserted blocks", function() {
    var layout = manager.insertLayout(4);
    var block = layout.insertBlock(0, null, "textblock");
    assert.deepEqual([false], $.map(simplelayout.getInsertedBlocks(), function(e) {
        return e.committed;
      }), "should have one committed block.");
    block.commit();
    assert.deepEqual([], $.map(simplelayout.getInsertedBlocks(), function(e) {
        return e.committed;
      }), "should have no inserted blocks.");
  });

  test("can de- and serialize", function() {
    fixtures.load("simplelayout.html");
    simplelayout.deserialize($(fixtures.body()));
    assert.equal(fixtures.read("simplelayout.json"), simplelayout.serialize());
  });

});
