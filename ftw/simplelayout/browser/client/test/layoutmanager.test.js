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

  test("hasLayouts returns true if layouts are inserted", function() {
    assert.isFalse(layoutmanager.hasLayouts(), "Should have no layouts inserted");

    layoutmanager.insertLayout();

    assert.isTrue(layoutmanager.hasLayouts(), "Should have layouts inserted");
  });

  suite("Layout-transactions", function() {

    test("can insert a Layout.", function() {
      layoutmanager.insertLayout();

      var addedNodes = $.map(layoutmanager.layouts, function(e) {
        return e.committed;
      });

      assert.deepEqual(addedNodes, [false]);
    });

    test("can delete a Layout.", function() {
      var layout = layoutmanager.insertLayout();
      layoutmanager.deleteLayout(layout.id);

      var addedNodes = $.map(target.find(".sl-layout"), function(e) {
        return {tag: e.tagName, classes: e.className};
      });

      assert.deepEqual(addedNodes, []);
    });

    test("layout stores parent information", function() {
      var generatedLayout = layoutmanager.insertLayout();
      assert.equal(layoutmanager.id, generatedLayout.parent.id, "Should store parent id");
    });

    test("layout can remove hinself from manager", function() {
      var generatedLayout = layoutmanager.insertLayout();
      generatedLayout.delete();

      assert.deepEqual($.map(layoutmanager.layouts, function(layout) {
        return layout.id;
      }), []);
    });

    test("can move a block", function() {

      var layout1 = layoutmanager.insertLayout().commit();
      var layout2 = layoutmanager.insertLayout().commit();
      var generatedBlock = layout1.insertBlock().commit();

      layoutmanager.moveBlock(generatedBlock, layout2);

      assert.equal(layout1.getCommittedBlocks(), 0, "Should have no blocks on source layout");
      assert.deepEqual($.map(layout2.getCommittedBlocks(), function(block) {
        return { id: block.id, committed: block.committed, parent: block.parent.id };
      }), [ { id: generatedBlock.id, committed: generatedBlock.committed, parent: layout2.id } ]);

    });

    test("can get inserted and committed blocks", function() {
      var layout1 = layoutmanager.insertLayout().commit();
      var layout2 = layoutmanager.insertLayout().commit();
      var block1 = layout1.insertBlock();
      var block2 = layout2.insertBlock();
      assert.deepEqual([false, false], $.map(layoutmanager.getInsertedBlocks(), function(block) {
        return block.committed;
      }), "should have two inserted blocks.");

      assert.deepEqual([], $.map(layoutmanager.getCommittedBlocks(), function(block) {
        return block.committed;
      }), "all blocks should be inserted.");

      block1.commit();
      block2.commit();

      assert.deepEqual([true, true], $.map(layoutmanager.getCommittedBlocks(), function(block) {
        return block.committed;
      }), "should have two committed blocks");

      assert.deepEqual([], $.map(layoutmanager.getInsertedBlocks(), function(block) {
        return block.committed;
      }), "all blocks should be committed.");

    });

  });

});
