import Layout from "simplelayout/Layout";
import Toolbar from "simplelayout/Toolbar";
import $ from "jquery";

describe("Layout", function() {

  var layout;

  beforeEach(function() {
    layout = new Layout(4);
  });

  it("is a constructor function", function() {
    assert.throw(Layout, TypeError, "Layout constructor cannot be called as a function.");
  });

  it("each column of 4 column layout has sl-col-4 class", function() {
    var nodes = $.map(layout.element.find(".sl-column"), function(column) {
      return { tag: column.tagName, classes: column.className };
    });

    assert.deepEqual(nodes, [
      {tag: "DIV", classes: "sl-column sl-col-4" },
      {tag: "DIV", classes: "sl-column sl-col-4" },
      {tag: "DIV", classes: "sl-column sl-col-4" },
      {tag: "DIV", classes: "sl-column sl-col-4" }
    ]);

  });

  it("default layout is 4", function() {
    var emptyLayout = new Layout();

    assert.equal(emptyLayout.columns, 4, "Default layout is not 4");
  });

  it("hasBlocks return true if at least one block is existing on a layout", function() {
    assert(!layout.hasBlocks(), "Layout should not have any blocks");
    layout.insertBlock();
    assert(layout.hasBlocks(), "Layout has blocks");
  });

  it("can attach a toolbar", function() {
    var layoutToolbar = new Toolbar([{move: { title: "move", class: "move"}}], "vertical", "layout");
    layout.attachToolbar(layoutToolbar);
    assert.equal(layout.element.find(".sl-toolbar-layout").length, 1, "Toolbar is not present");
  });

  describe("Block-transactions", function() {

    it("can insert a block", function() {
      var generatedBlock = layout.insertBlock("<p></p>", "textblock");
      var blocks = $.map(layout.blocks, function(block) {
        return {committed: block.committed, id: block.id, type: block.type};
      });

      assert.deepEqual(blocks, [{committed: false, id: generatedBlock.id, type: "textblock"}]);
    });

    it("can delete a block", function() {
      var generatedBlock = layout.insertBlock();
      layout.deleteBlock(generatedBlock.id);

      var blocks = $.map(layout.blocks, function(block) {
        return {committed: block.committed, id: block.id, type: block.type};
      });

      assert.deepEqual(blocks, [], "Should have no blocks after deleting them");
    });

    it("can move a block to another layout", function() {
      var generatedBlock = layout.insertBlock("<p>Test</p>", "textblock").commit();
      var target = new Layout();
      layout.moveBlock(generatedBlock, target);

      assert.equal(layout.getCommittedBlocks(), 0, "Sourcelayout shoult not have any blocks");
      assert.deepEqual([ { id: generatedBlock.id, committed: true, parent: target.id }],
        $.map(target.getCommittedBlocks(), function(block) {
          return { id: block.id, committed: block.committed, parent: block.parent.id };
      }));
    });

    it("block stores parent information", function() {
      var generatedLayout = new Layout();
      var generatedBlock = generatedLayout.insertBlock();

      assert.equal(generatedLayout.id, generatedBlock.parent.id, "Should store parent id");
    });

  });

  describe("Block accessors", function() {

    it("can get committed blocks", function() {
      var block2 = layout.insertBlock();
      layout.insertBlock();
      layout.insertBlock();
      var blocks = $.map(layout.getCommittedBlocks(), function(block) {
        return block.committed;
      });
      assert.deepEqual(blocks, []);
      block2.commit();
      blocks = $.map(layout.getCommittedBlocks(), function(block) {
        return block.committed;
      });
      assert.deepEqual(blocks, [true]);
    });

    it("can get inserted blocks", function() {
      var block2 = layout.insertBlock();
      layout.insertBlock();
      layout.insertBlock();
      var blocks = $.map(layout.getInsertedBlocks(), function(block) {
        return block.committed;
      });
      assert.deepEqual(blocks, [false, false, false]);
      block2.commit();
      blocks = $.map(layout.getInsertedBlocks(), function(block) {
        return block.committed;
      });
      assert.deepEqual(blocks, [false, false]);
    });

    it("block can remove hinself from layout", function() {
      var generatedBlock = layout.insertBlock();
      generatedBlock.delete();

      assert.deepEqual($.map(layout.blocks, function(block) {
        return block.id;
      }), []);
    });

  });

});
