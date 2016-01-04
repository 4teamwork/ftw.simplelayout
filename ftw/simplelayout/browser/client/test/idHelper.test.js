suite("idHelper", function() {
  "use strict";

  var idHelper;

  suiteSetup(function(done) {
    require(["app/simplelayout/idHelper"], function(_idHelper) {
      idHelper = _idHelper;
      done();
    });
  });

  function isUUID(search) {
    return /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/.test(search);
  }

  test("generates a UUID", function() {
    assert.isTrue(isUUID(idHelper.createGUID()));
  });

});
