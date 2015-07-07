suite("Layoutmanager", function() {
  "use strict";

  var Layoutmanager;
  var layoutmanager;
  var target;

  suiteSetup(function(done) {
    require(["app/simplelayout/Layoutmanager"], function(_Layoutmanager) {
      Layoutmanager = _Layoutmanager;
      done();
    });
  });

  setup(function(done) {
    layoutmanager = new Layoutmanager();
    target = $("<div></div>");
    layoutmanager.attachTo(target);
    done();
  });

  test("is a constructor function", function() {
    assert.throw(Layoutmanager, TypeError, "Layoutmanager constructor cannot be called as a function.");
  });

  test("can be added to a target node.", function() {
    var addedNodes = $.map(target.children(), function(e) {
      return [{tag: e.tagName, classes: e.className}];
    });

    assert.deepEqual(addedNodes, [{tag: "DIV", classes: "sl-simplelayout"}]);
  });

  test("default width is 100%", function() {
    assert.equal(layoutmanager.options.width, "100%");
  });

  suite("Layout-transactions", function() {

    test("can insert a Layout.", function() {
      layoutmanager.insertLayout(4);

      var addedNodes = $.map(layoutmanager.layouts, function(e) {
        return e.committed;
      });

      assert.deepEqual(addedNodes, [false]);
    });

    test("can delete a Layout.", function() {
      var layout = layoutmanager.insertLayout(4);
      layoutmanager.deleteLayout(layout.element.data("layoutId"));

      var addedNodes = $.map(target.find(".sl-layout"), function(e) {
        return {tag: e.tagName, classes: e.className};
      });

      assert.deepEqual(addedNodes, []);
    });

    test("can commit a Layout.", function() {
      layoutmanager.insertLayout(4);

      layoutmanager.commitLayouts();

      var addedNodes = $.map(layoutmanager.layouts, function(e) {
        return {committed: e.committed};
      });

      assert.deepEqual(addedNodes, [{committed: true}]);
    });

    test("can move a block", function() {
      var layout1 = layoutmanager.insertLayout(4);
      var layout2 = layoutmanager.insertLayout(4);
      layoutmanager.commitLayouts();
      var block = layout1.insertBlock(0, "<p>Test</p>", "textblock");
      layout1.commitBlocks(0);

      layoutmanager.moveBlock(layout1.element.data("layoutId"), 0, block.element.data("blockId"), layout2.element.data("layoutId"), 0);
      var blocksOnOriginalLayout = layout1.columns[0].blocks;
      var blocksOnMovedLayout = layout2.columns[0].blocks;

      var nodesOnOriginalLayout = $.map(blocksOnOriginalLayout, function(e) {
        return {layoutId: e.element.data("layoutId"), columnId: e.element.data("columnId"), blockId: e.element.data("blockId")};
      });
      assert.deepEqual(nodesOnOriginalLayout, []);

      var nodesOnMovedLayout = $.map(blocksOnMovedLayout, function(e) {
        return {layoutId: e.element.data("layoutId"), columnId: e.element.data("columnId"), blockId: e.element.data("blockId")};
      });
      assert.deepEqual(nodesOnMovedLayout, [{layoutId: layout2.element.data("layoutId"), columnId: 0, blockId: 0}]);
    });

    test("can get inserted and committed blocks", function() {
      var layout1 = layoutmanager.insertLayout(4);
      var layout2 = layoutmanager.insertLayout(4);
      layoutmanager.commitLayouts();
      layout1.insertBlock(0, null, "textblock");
      layout2.insertBlock(0, null, "textblock");
      assert.deepEqual([false, false], $.map(layoutmanager.getInsertedBlocks(), function(block) {
        return block.committed;
      }), "should have two inserted blocks.");
      assert.deepEqual([], $.map(layoutmanager.getCommittedBlocks(), function(block) {
        return block.committed;
      }), "all blocks should be inserted.");
      layout1.commitBlocks(0);
      layout2.commitBlocks(0);
      assert.deepEqual([true, true], $.map(layoutmanager.getCommittedBlocks(), function(block) {
        return block.committed;
      }), "should have two committed");
      assert.deepEqual([], $.map(layoutmanager.getInsertedBlocks(), function(block) {
        return block.committed;
      }), "all blocks should be committed.");
    });

  });

  suite("Delegates adding and removing blocks to Layouts", function() {

    var columnId = 0;
    var type = "textblock";
    var content = "<p>Test</p>";

    test("can add a block into a specific Layout", function() {
      var layout = layoutmanager.insertLayout(4);
      layoutmanager.commitLayouts();

      var block = layout.insertBlock(columnId, content, type);

      var blocks = $.map(layout.columns[columnId].blocks, function(e) {
        return {committed: e.committed, layoutId: e.element.data("layoutId"), columnId: e.element.data("columnId"), blockId: e.element.data("blockId"), type: e.element.data("type")};
      });

      assert.deepEqual(blocks, [{committed: false, layoutId: layout.element.data("layoutId"), columnId: columnId, blockId: block.element.data("blockId"), type: type}]);
    });

    test("can delete a specific block from a specific layout", function() {
      var layout = layoutmanager.insertLayout(4);
      layoutmanager.commitLayouts();

      var block1 = layout.insertBlock(columnId, content, type);
      var block2 = layout.insertBlock(columnId, content, type);

      layout.deleteBlock(columnId, block1.element.data("blockId"));

      var blocks = $.map(layout.columns[columnId].blocks, function(e) {
        return {committed: e.committed, layoutId: e.element.data("layoutId"), columnId: e.element.data("columnId"), blockId: e.element.data("blockId"), type: e.element.data("type")};
      });

      assert.deepEqual(blocks, [{committed: false, layoutId: layout.element.data("layoutId"), columnId: columnId, blockId: block2.element.data("blockId"), type: type}]);
    });

    test("can commit blocks", function() {
      var layout = layoutmanager.insertLayout(4);
      layoutmanager.commitLayouts();

      var block = layout.insertBlock(columnId, content, type);
      layout.commitBlocks(columnId);

      var blocks = $.map(layout.columns[columnId].getCommittedBlocks(), function(e) {
        return {committed: e.committed, layoutId: e.element.data("layoutId"), columnId: e.element.data("columnId"), blockId: e.element.data("blockId"), type: e.element.data("type")};
      });

      assert.deepEqual(blocks, [{committed: true, layoutId: layout.element.data("layoutId"), columnId: columnId, blockId: block.element.data("blockId"), type: type}]);
    });

    test("default layout is 4", function() {
      var layout = layoutmanager.insertLayout();
      var columns = $.map(layout.columns, function(e) {
        return e.element.data().columnId;
      });
      assert.deepEqual(columns, [0, 1, 2, 3]);
    });

    test("adding a layout with undefined source takes layoutoptions", function() {
      var layout = layoutmanager.insertLayout({ columns: 2 });
      var columns = $.map(layout.columns, function(e) {
        return e.element.data().columnId;
      });
      assert.deepEqual(columns, [0, 1]);
    });

    test("adding a layout with source takes columncount from source", function() {
      var layoutSource = $(fixtures.read("layoutSource.html"));
      var layout = layoutmanager.insertLayout({ source: layoutSource });
      var columns = $.map(layout.columns, function(e) {
        return e.element.data().columnId;
      });
      assert.deepEqual(columns, [0, 1]);
    });

  });
});
