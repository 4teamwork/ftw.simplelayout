import Transactional from "simplelayout/transactional";
import EventEmitter from "simplelayout/EventEmitter";

const EE = EventEmitter.getInstance();

describe("transactional", function() {

  var transactional = null;

  beforeEach(function() {
    transactional = new Transactional();
  });

  it("initial state is not committed", function() {
    assert.isFalse(transactional.committed);
  });

  it("can commit", function() {
    transactional.commit();
    assert.isTrue(transactional.committed);
  });

  it("committing twice throws an error", function() {
    assert.throw(function() {
      transactional.commit().commit();
    }, Error, "Transaction is already committed");
  });

  it("can rollback transaction", function() {
    transactional.commit().rollback();
    assert.isFalse(transactional.committed);
  });

  it("rollback on an non committed transaction throws an error", function() {
    assert.throw(function() {
      transactional.rollback();
    }, Error, "Transaction on not yet committed");
  });

  it("rollbacking twice throws an error", function() {
    assert.throw(function() {
      transactional.commit().rollback().rollback();
    }, Error, "Transaction on not yet committed");
  });

  it("emits commit event for given name", function() {
    transactional.name = "test";
    EE.on("test-committed", function(eventTransactional) {
      assert.equal(eventTransactional.name, "test");
    });
    transactional.commit();
  });

  it("emits rollback event for given name", function() {
    transactional.name = "test";
    EE.on("test-rollbacked", function(eventTransactional) {
      assert.equal(eventTransactional.name, "test");
    });
    transactional.commit().rollback();
  });

});
