import EventEmitter from "simplelayout/EventEmitter";

const EE = EventEmitter.getInstance();

export default function transactional() {

  this.committed = false;

  this.commit = function() {
    if(this.committed) {
      throw new Error("Transaction is already committed");
    }
    this.committed = true;
    EE.trigger(this.name + "-committed", [this]);
    return this;
  };

  this.rollback = function() {
    if(!this.committed) {
      throw new Error("Transaction on not yet committed");
    }
    this.committed = false;
    EE.trigger(this.name + "-rollbacked", [this]);
    return this;
  };

};
