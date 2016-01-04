define(["app/simplelayout/EventEmitter"], function(EventEmitter) {

  "use strict";

  var transactional = function() {

    this.committed = false;

    this.commit = function() {
      if(this.committed) {
        throw new Error("Transaction is already committed");
      }
      this.committed = true;
      EventEmitter.trigger(this.name + "-committed", [this]);
      return this;
    };

    this.rollback = function() {
      if(!this.committed) {
        throw new Error("Transaction on not yet committed");
      }
      this.committed = false;
      EventEmitter.trigger(this.name + "-rollbacked", [this]);
      return this;
    };

  };

  return transactional;

});
