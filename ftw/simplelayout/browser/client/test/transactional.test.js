suite("transactional", function() {

  "use strict";

  var Transactional = null;
  var transactional = null;
  var EventEmitter;

  suiteSetup(function(done) {
    require(["app/simplelayout/transactional", "app/simplelayout/EventEmitter"], function(_transactional, _EventEmitter) {
      Transactional = _transactional;
      EventEmitter = _EventEmitter;
      done();
    });
  });

  setup(function(done) {
    transactional = new Transactional();
    done();
  });

  test("initial state is not committed", function() {
    assert.isFalse(transactional.committed);
  });

  test("can commit", function() {
    transactional.commit();
    assert.isTrue(transactional.committed);
  });

  test("committing twice throws an error", function() {
    assert.throw(function() {
      transactional.commit().commit();
    }, Error, "Transaction is already committed");
  });

  test("can rollback transaction", function() {
    transactional.commit().rollback();
    assert.isFalse(transactional.committed);
  });

  test("rollback on an non committed transaction throws an error", function() {
    assert.throw(function() {
      transactional.rollback();
    }, Error, "Transaction on not yet committed");
  });

  test("rollbacking twice throws an error", function() {
    assert.throw(function() {
      transactional.commit().rollback().rollback();
    }, Error, "Transaction on not yet committed");
  });

  test("emits commit event for given name", function() {
    transactional.name = "test";
    EventEmitter.on("test-committed", function(eventTransactional) {
      assert.equal(eventTransactional.name, "test");
    });
    transactional.commit();
  });

  test("emits rollback event for given name", function() {
    transactional.name = "test";
    EventEmitter.on("test-rollbacked", function(eventTransactional) {
      assert.equal(eventTransactional.name, "test");
    });
    transactional.commit().rollback();
  });

});
