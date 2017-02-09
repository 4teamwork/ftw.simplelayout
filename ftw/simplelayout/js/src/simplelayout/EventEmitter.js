import $ from "jquery";
const EE = require("wolfy87-eventemitter");

var instance = null;
var eventEmitter = null;

export default function EventEmitter(){
  this.trigger = function(eventType, data) {
    $(document).trigger(eventType, data);
    eventEmitter.trigger(eventType, data);
  };

  this.on = function(eventType, callback) { eventEmitter.on(eventType, callback); };

  this.clean = function() {
    var listeners = [];
    $.each(eventEmitter.getListeners(/./g), (i, e) => {
      listeners = listeners.concat(eventEmitter.flattenListeners(e));
    });
    eventEmitter.removeListeners.call(eventEmitter, /./g, listeners);
  }
}

EventEmitter.getInstance = function(){

  if(instance === null){
    eventEmitter = new EE();
    instance = new EventEmitter();
  }

  return instance;
};
