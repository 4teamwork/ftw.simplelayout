suite("Column", function() {
  "use strict";

  var Column;
  var column;

  suiteSetup(function(done) {
    require(["app/simplelayout/Column"], function(_Column) {
      Column = _Column;
      done();
    });
  });

  setup(function(done) {
    column = new Column(2);
    column.create();
    done();
  });

  test("is a constructor function", function() {
    assert.throw(Column, TypeError, "Column constructor cannot be called as a function.");
  });

  test("can create column with sl-col-2 class", function() {
    var node = $.map(column.element, function(columnNode) {
      return {tag: columnNode.tagName, classes: columnNode.className};
    });

    assert.deepEqual(node, [{tag: "DIV", classes: "sl-column sl-col-2"}]);
  });

  test("defining an empty column raises an exeption", function() {
    assert.throws(function() {
      column = new Column();
      column();
    }, Error, "Columns are not defined.");
  });

  suite("Block-transactions", function() {

    test("can insert a block", function() {
      column.insertBlock( { content: "<p>Test</p>", type: "textblock"} );

      var blocks = $.map(column.blocks, function(block) {
        return {committed: block.committed, blockId: block.element.data("block-id"), type: block.type};
      });

      assert.deepEqual(blocks, [{committed: false, blockId: 0, type: "textblock"}]);
    });

    test("can delete a block", function() {
      var block = column.insertBlock("<p>Test</p>", "textblock");
      column.deleteBlock(block.element.data("blockId"));

      var blocks = $.map(column.blocks, function(e) {
        return {committed: e.committed, blockId: e.element.data("block-id"), type: e.type};
      });

      assert.deepEqual(blocks, [], "Should have no blocks after deleting them");
    });

    test("can commit a block", function() {
      column.insertBlock("<p>Test</p>", "textblock");
      column.commitBlocks();
      var blocks = $.map(column.getCommittedBlocks(), function(block) {
        return {committed: block.committed};
      });

      assert.deepEqual(blocks, [{committed: true}]);

    });

    test("inserting and deleting blocks does not commit them", function() {
      column.insertBlock("<p>Test</p>", "textblock");
      var block = column.insertBlock("<p>Test</p>", "textblock");
      column.deleteBlock(block.element.data("blockId"));

      assert.deepEqual(column.getCommittedBlocks(), [], "Should have no committed blocks without commit");
    });

    test("delete a non inseted block raises an exception", function() {
      assert.throws(function() {
        column.deleteBlock(2);
      }, Error, "No block with id 2 inserted.");
    });

    test("commit non inserted blocks raises exception", function() {
      assert.throws(function() {
        column.commitBlocks();
      }, Error, "No blocks inserted.");
    });

  });

});
