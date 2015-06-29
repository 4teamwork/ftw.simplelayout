suite("idHelper", function() {
  "use strict";

  var idHelper;

  suiteSetup(function(done) {
    require(["app/simplelayout/idHelper"], function(_idHelper) {
      idHelper = _idHelper;
      done();
    });
  });

  test("generates a new id from a hash with sorted numeric keys", function() {
    var nextId = idHelper.generateFromHash({1: "a", 2: "b", 5: "c", 123: "d"});
    assert.equal(nextId, 124);
  });

  test("generates a new id from a hash with unsorted numeric keys", function() {
    var nextId = idHelper.generateFromHash({127: "a", 724: "b", 34: "c", 1158: "d", 95: "e"});
    assert.equal(nextId, 1159);
  });

  test("generates a new id from a empty hash", function() {
    var nextId = idHelper.generateFromHash({});
    assert.equal(nextId, 0);
  });

});
