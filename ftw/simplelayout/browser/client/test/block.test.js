suite("Block", function() {
  "use strict";

  var Block;
  var Toolbar;
  var block;

  suiteSetup(function(done) {
    require(["app/simplelayout/Block", "app/simplelayout/Toolbar"], function(_Block, _Toolbar) {
      Block = _Block;
      Toolbar = _Toolbar;
      done();
    });
  });

  setup(function(done) {
    block = new Block("<p>Test</p>", "textblock");
    done();
  });

  test("is a constructor function", function() {
    assert.throw(Block, TypeError, "Block constructor cannot be called as a function.");
  });

  test("can create a block", function() {
    var node = $.map(block.element, function(blockNode) {
      return { tagName: blockNode.tagName, content: blockNode.innerHTML, type: blockNode.dataset.type };
    });

    assert.deepEqual(node, [{tagName: "DIV", content: '<div class="iFrameFix"></div><div class="sl-block-content"><p>Test</p></div>', type: "textblock"}]);
  });

  test("can set block-content", function() {
    block.content("<p>Hallo</p>");

    var node = $.map(block.element, function(blockNode) {
      return {tagName: blockNode.tagName, content: blockNode.innerHTML, type: blockNode.dataset.type};
    });

    assert.deepEqual(node, [{tagName: "DIV", content: '<div class="iFrameFix"></div><div class="sl-block-content"><p>Hallo</p></div>', type: "textblock"}]);
  });

  test("can attach a toolbar", function() {
    var toolbar = new Toolbar();

    block.attachToolbar(toolbar);

    var node = $.map($(".sl-toolbar", block.element), function(toolbarNode) {
      return { tagName: toolbarNode.tagName, classes: toolbarNode.className };
    });
    assert.deepEqual(node, [{tagName: "UL", classes: "sl-toolbar"}]);
  });

  test("prepends frameFix", function() {
    var frameFixElement = $.map($(".iFrameFix", block.element), function(frame) {
      return { classes: frame.className, tagName: frame.tagName };
    });
    assert.deepEqual(frameFixElement, [{ classes: "iFrameFix", tagName: "DIV" }]);
  });

  test("can enable and disable frameFix", function() {
    block.enableFrame();
    var frameFixElement = $.map(block.element.find(".iFrameFix"), function(frame) {
      return { display: frame.style.display };
    });
    assert.deepEqual(frameFixElement, [{ display: "block" }]);
    block.disableFrame();
    frameFixElement = $.map(block.element.find(".iFrameFix"), function(frame) {
      return { display: frame.style.display };
    });
    assert.deepEqual(frameFixElement, [{ display: "none" }]);
  });

});
