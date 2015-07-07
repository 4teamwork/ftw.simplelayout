define(["EventEmitter"], function(EE){

  "use strict";

  var instance = null;

  function EventEmitter(){}

  EventEmitter.getInstance = function(){
    if(instance === null){
      instance = new EE();
    }
    return instance;
  };

  return EventEmitter.getInstance();
});
