define(["EventEmitter"], function(EE){

  "use strict";

  var eventEmitter = null;
  var instance = null;

  function EventEmitter(){
    this.trigger = function(eventType, data) {
      $(document).trigger(eventType, data);
      eventEmitter.trigger(eventType, data);
    };

    this.on = function(eventType, callback) { eventEmitter.on(eventType, callback); };
  }

  EventEmitter.getInstance = function(){

    if(instance === null){
      eventEmitter = new EE();
      instance = new EventEmitter();
    }

    return instance;
  };

  return EventEmitter.getInstance();
});
