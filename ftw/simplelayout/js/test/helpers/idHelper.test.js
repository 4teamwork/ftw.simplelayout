import createGUID from "helpers/idHelper";

describe("idHelper", function() {

  function isUUID(search) {
    return /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/.test(search);
  }

  it("generates a UUID", function() {
    assert.isTrue(isUUID(createGUID()));
  });

});
