import Toolbox from "toolbox/Toolbox";
import $ from "jquery";

describe("Toolbox", function() {

  it("is a constructor function", function() {
    assert.throw(Toolbox, TypeError, "Toolbox constructor cannot be called as a function.");
  });

  it("default layouts are [1, 2, 4]", function() {
    var defaultToolbox = new Toolbox();
    assert.deepEqual(defaultToolbox.options.layouts, [1, 2, 4]);
  });

  it("attaches to target container", function() {
    var toolbox = new Toolbox();
    var target = $("<div></div>");

    toolbox.attachTo(target);

    var addedNodes = $.map(target.children(), function(e) {
      return [{tag: e.tagName, id: e.id, classes: e.className}];
    });
    assert.deepEqual(addedNodes, [{tag: "DIV", id: "sl-toolbox", classes: "sl-toolbox"}]);
  });

  it("can enable and disable blocks", function() {
    var toolbox = new Toolbox();
    toolbox.blocksEnabled(false);

    assert.equal("sl-toolbox-blocks disabled", toolbox.element.find(".sl-toolbox-blocks")[0].className);

    toolbox.blocksEnabled(true);

    assert.equal("sl-toolbox-blocks", toolbox.element.find(".sl-toolbox-blocks")[0].className);
  });

  describe("addables", function() {
    it("can render blocks", function() {
      var toolbox = new Toolbox({
        blocks: [{ title: "Textblock", contentType: "textblock", formUrl: "URL" }]
      });

      assert.deepEqual($.map(toolbox.element.find(".sl-toolbox-block"), function(block) {
        return {
          tagName: block.tagName,
          formUrl: $(block).data().formUrl,
          contentType: $(block).data().type
        };
      }), [{
        tagName: "A",
        formUrl: "URL",
        contentType: "textblock"
      }]);

      assert.deepEqual($.map(toolbox.element.find(".sl-toolbox-blocks .description"), function(description) {
        return { description: description.innerHTML };
      }), [{ description: "Textblock" }]);
    });

    it("can render layouts", function() {
      var toolbox = new Toolbox({
        canChangeLayout: true,
        layouts: [1, 2]
      });

      assert.deepEqual($.map(toolbox.element.find(".sl-toolbox-layout"), function(layout) {
        return { columns: $(layout).data().columns };
      }), [{ columns: 1 }, { columns: 2 }]);

      assert.deepEqual($.map(toolbox.element.find(".sl-toolbox-layout .description"), function(description) {
        return { description: description.innerHTML };
      }), [{ description: "1" }, { description: "2" }]);
    });

    it("can render label for layout description", function() {
      var toolbox = new Toolbox({
        canChangeLayout: true,
        layouts: [1, 2],
        labels: {
          labelColumnPostfix: " - Columns"
        }
      });

      assert.deepEqual($.map(toolbox.element.find(".sl-toolbox-layout .description"), function(description) {
        return { description: description.innerHTML };
      }), [{ description: "1 - Columns" }, { description: "2 - Columns" }]);
    });

    it("can render icon", function() {
      var toolbox = new Toolbox({
        blocks: [{ title: "Textblock", contentType: "textblock", formUrl: "URL" }]
      });

      assert.deepEqual($.map(toolbox.element.find(".sl-toolbox-blocks .icon-textblock"), function(icon) {
        return { className: icon.className };
      }), [{ className: "icon-textblock" }]);
    });

    it("creates Object references from blocks", function() {
      var toolbox = new Toolbox({
        layouts: [1, 2, 4],
        canChangeLayout: true,
        blocks: [
          { title: "Textblock", contentType: "textblock", formUrl: "URL" },
          { title: "Listingblock", contentType: "listingblock", formUrl: "URL" }
        ],
        layoutActions: {
          actions: {
            move: {
              class: "iconmove move",
              title: "Move this layout arround."
            },
            delete: {
              class: "icondelete delete",
              title: "Delete this layout."
            }
          }
        },
        labels: {
          labelColumnPostfix: "Column(s)"
        }
      });

      assert.deepEqual(toolbox.options.blocks, {
        textblock: { title: "Textblock", contentType: "textblock", formUrl: "URL" },
        listingblock: { title: "Listingblock", contentType: "listingblock", formUrl: "URL" }
      });
    });

    it("does not reder layout when canChangeLayout is disabled", function() {
      var toolbox = new Toolbox({
        layouts: [1, 2, 4],
        canChangeLayout: false
      });
      var target = $("<div></div>");

      toolbox.attachTo(target);

      assert.equal(toolbox.element.find(".sl-toolbox-layouts").length, 0, "Layouts should not get rendered");

    });

  });

});
