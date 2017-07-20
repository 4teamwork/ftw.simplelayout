import Block from "simplelayout/Block";
import Toolbar from "simplelayout/Toolbar";
import $ from "jquery";

describe("Block", function() {
  var block;

  beforeEach(function() {
    block = new Block("<p>Test</p>", "textblock");
  });

  it("is a constructor function", function() {
    assert.throw(Block, TypeError, "Block constructor cannot be called as a function.");
  });

  it("can create a block", function() {
    var node = $.map(block.element, function(blockNode) {
      return { tagName: blockNode.tagName, content: blockNode.innerHTML, type: blockNode.dataset.type };
    });

    assert.deepEqual(node, [{tagName: "DIV", content: '<div class="iFrameFix"></div><div class="sl-block-content"><p>Test</p></div>', type: "textblock"}]);
  });

  it("can set block-content", function() {
    block.content("<p>Hallo</p>");

    var node = $.map(block.element, function(blockNode) {
      return {tagName: blockNode.tagName, content: blockNode.innerHTML, type: blockNode.dataset.type};
    });

    assert.deepEqual(node, [{tagName: "DIV", content: '<div class="iFrameFix"></div><div class="sl-block-content"><p>Hallo</p></div>', type: "textblock"}]);
  });

  it("should set id on block content when adding a new block", () => {
    block.content("<p>hallo</p>", "block-id");

    var node = $.map(block.element, function(blockNode) {
      return {tagName: blockNode.tagName, content: blockNode.innerHTML, type: blockNode.dataset.type };
    });

    assert.deepEqual(node, [
      {
        tagName: "DIV",
        content: '<div class="iFrameFix"></div><div class="sl-block-content" id="block-id"><p>hallo</p></div>',
        type: "textblock",
      }
    ]);
  });

  it("can attach a toolbar", function() {
    var toolbar = new Toolbar();

    block.attachToolbar(toolbar);

    var node = $.map($(".sl-toolbar", block.element), function(toolbarNode) {
      return { tagName: toolbarNode.tagName, classes: toolbarNode.className };
    });
    assert.deepEqual(node, [{tagName: "UL", classes: "sl-toolbar"}]);
  });

  it("prepends frameFix", function() {
    var frameFixElement = $.map($(".iFrameFix", block.element), function(frame) {
      return { classes: frame.className, tagName: frame.tagName };
    });
    assert.deepEqual(frameFixElement, [{ classes: "iFrameFix", tagName: "DIV" }]);
  });

  it("can enable and disable frameFix", function() {
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
