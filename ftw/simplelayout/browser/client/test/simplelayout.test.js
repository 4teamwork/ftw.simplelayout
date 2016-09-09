suite("Simplelayout", function() {
  "use strict";

  var Simplelayout;
  var simplelayout;

  suiteSetup(function(done) {
    require(["app/simplelayout/Simplelayout"], function(_Simplelayout) {
      Simplelayout = _Simplelayout;
      done();
    });
  });

  setup(function(done) {
    simplelayout = new Simplelayout();
    done();
  });

  test("is a constructor function", function() {
    assert.throw(Simplelayout, TypeError, "Simplelayout constructor cannot be called as a function.");
  });

  test("can insert a manager", function() {
    var generatedManager = simplelayout.insertManager();
    assert.deepEqual($.map(simplelayout.managers, function(manager) {
      return { id: manager.id };
    }), [ { id: generatedManager.id } ]);
  });

  test("can manage restrictions for given layout", function() {
    var testStructure = fixtures.read("simplelayout.html");
    var simplelayout2 = new Simplelayout();
    simplelayout2.restore($(testStructure));
    var managers = $.map(simplelayout2.managers, function(manager) { return manager; });
    var manager1 = managers[0];
    var manager2 = managers[1];
    simplelayout2.options.layoutRestrictions = {
      2: [manager1.id],
      4: [manager2.id]
    };

    simplelayout2.restrictLayout(2);
    assert.deepEqual($.map(simplelayout2.managers, function(manager) {
      return manager.enabled;
    }), [false, true]);

    simplelayout2.restrictLayout(4);
    simplelayout2.restrictLayout(2);
    assert.deepEqual($.map(simplelayout2.managers, function(manager) {
      return manager.enabled;
    }), [false, false]);

    simplelayout2.allowLayout(4);
    assert.deepEqual($.map(simplelayout2.managers, function(manager) {
      return manager.enabled;
    }), [false, true]);

    simplelayout2.allowLayout(2);
    assert.deepEqual($.map(simplelayout2.managers, function(manager) {
      return manager.enabled;
    }), [true, true]);
  });

  suite("Element transactions", function () {
    test("can move a layout", function() {
      var manager1 = simplelayout.insertManager();
      var manager2 = simplelayout.insertManager();

      var layout1 = manager1.insertLayout().commit();
      var layout2 = manager1.insertLayout().commit();
      var layout3 = manager2.insertLayout().commit();

      simplelayout.moveLayout(layout1, manager2);

      assert.deepEqual($.map(manager1.layouts, function(layout) {
        return { id: layout.id, committed: layout.committed };
      }), [ { id: layout2.id, committed: true } ]);

      assert.deepEqual($.map(manager2.layouts, function(layout) {
        return { id: layout.id, committed: layout.committed, data: layout.data() };
      }), [ { id: layout3.id, committed: true, data: layout3.data() },
            { id: layout1.id, committed: true, data: layout1.data() } ]);

    });
  });

  test("can get committed blocks", function() {
    var manager1 = simplelayout.insertManager();
    var layout1 = manager1.insertLayout();
    var generatedBlock = layout1.insertBlock("<p></p>", "textblock");

    assert.deepEqual([], $.map(simplelayout.getCommittedBlocks(), function(block) {
      return block.committed;
    }), "should have no committed blocks.");

    generatedBlock.commit();

    assert.deepEqual([true], $.map(simplelayout.getCommittedBlocks(), function(block) {
      return block.committed;
    }), "should have one committed blocks.");
  });

  test("can get inserted blocks", function() {
    var manager1 = simplelayout.insertManager();
    var layout1 = manager1.insertLayout();
    var generatedBlock = layout1.insertBlock("<p></p>", "textblock");

    assert.deepEqual([false], $.map(simplelayout.getInsertedBlocks(), function(block) {
      return block.committed;
    }), "should have one committed block.");

    generatedBlock.commit();

    assert.deepEqual([], $.map(simplelayout.getInsertedBlocks(), function(block) {
      return block.committed;
    }), "should have no inserted blocks.");
  });

  test("can restore DOM structure", function() {
    fixtures.load("simplelayout.html");
    simplelayout.restore($(fixtures.body()));
    var data = $.map(simplelayout.managers, function(manager) {
      return {
        committed: manager.committed,
        represents: manager.represents,
        layouts: $.map(manager.layouts, function(layout) {
          return {
            committed: layout.committed,
            columns: layout.columns,
            blocks: $.map(layout.blocks, function(block) {
              return {
                committed: block.committed,
                represents: block.represents,
                type: block.type
              };
            })
          };
        })
       };
    });
    assert.deepEqual(data,
    [{
      committed: true,
      represents: "slot1",
      layouts: [
      {
        committed: true,
        columns: 4,
        blocks: [
        {
          committed: true,
          represents: "c968b492-563a-11e5-885d-feff819cdc9f",
          type: "textblock"
        },
        {
          committed: true,
          represents: "c968b726-563a-11e5-885d-deff819cdc9f",
          type: "textblock"
        }
        ]
      }
      ]
    },
    {
      committed: true,
      represents: "slot2",
      layouts: [
      {
        committed: true,
        columns: 4,
        blocks: [
        {
          committed: true,
          represents: "c968b816-563a-11e5-885d-feff819cd49f",
          type: "textblock"
        },
        {
          committed: true,
          represents: "c968b492-563a-11e5-885d-fedf819cdc9f",
          type: "textblock"
        },
        {
          committed: true,
          represents: "c968b492-563a-11e5-885d-feff8196dc9f",
          type: "textblock"
        }
        ]
      }
      ]
    }]);
  });

});
