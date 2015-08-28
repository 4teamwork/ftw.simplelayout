(function(window, factory) {
  window.Simplelayout = factory().simplelayout;
  window.Toolbox = factory().toolbox;
}(this, function() {
/**
 * @license almond 0.3.1 Copyright (c) 2011-2014, The Dojo Foundation All Rights Reserved.
 * Available via the MIT or new BSD license.
 * see: http://github.com/jrburke/almond for details
 */
//Going sloppy to avoid 'use strict' string cost, but strict practices should
//be followed.
/*jslint sloppy: true */
/*global setTimeout: false */

var requirejs, require, define;
(function (undef) {
    var main, req, makeMap, handlers,
        defined = {},
        waiting = {},
        config = {},
        defining = {},
        hasOwn = Object.prototype.hasOwnProperty,
        aps = [].slice,
        jsSuffixRegExp = /\.js$/;

    function hasProp(obj, prop) {
        return hasOwn.call(obj, prop);
    }

    /**
     * Given a relative module name, like ./something, normalize it to
     * a real name that can be mapped to a path.
     * @param {String} name the relative name
     * @param {String} baseName a real name that the name arg is relative
     * to.
     * @returns {String} normalized name
     */
    function normalize(name, baseName) {
        var nameParts, nameSegment, mapValue, foundMap, lastIndex,
            foundI, foundStarMap, starI, i, j, part,
            baseParts = baseName && baseName.split("/"),
            map = config.map,
            starMap = (map && map['*']) || {};

        //Adjust any relative paths.
        if (name && name.charAt(0) === ".") {
            //If have a base name, try to normalize against it,
            //otherwise, assume it is a top-level require that will
            //be relative to baseUrl in the end.
            if (baseName) {
                name = name.split('/');
                lastIndex = name.length - 1;

                // Node .js allowance:
                if (config.nodeIdCompat && jsSuffixRegExp.test(name[lastIndex])) {
                    name[lastIndex] = name[lastIndex].replace(jsSuffixRegExp, '');
                }

                //Lop off the last part of baseParts, so that . matches the
                //"directory" and not name of the baseName's module. For instance,
                //baseName of "one/two/three", maps to "one/two/three.js", but we
                //want the directory, "one/two" for this normalization.
                name = baseParts.slice(0, baseParts.length - 1).concat(name);

                //start trimDots
                for (i = 0; i < name.length; i += 1) {
                    part = name[i];
                    if (part === ".") {
                        name.splice(i, 1);
                        i -= 1;
                    } else if (part === "..") {
                        if (i === 1 && (name[2] === '..' || name[0] === '..')) {
                            //End of the line. Keep at least one non-dot
                            //path segment at the front so it can be mapped
                            //correctly to disk. Otherwise, there is likely
                            //no path mapping for a path starting with '..'.
                            //This can still fail, but catches the most reasonable
                            //uses of ..
                            break;
                        } else if (i > 0) {
                            name.splice(i - 1, 2);
                            i -= 2;
                        }
                    }
                }
                //end trimDots

                name = name.join("/");
            } else if (name.indexOf('./') === 0) {
                // No baseName, so this is ID is resolved relative
                // to baseUrl, pull off the leading dot.
                name = name.substring(2);
            }
        }

        //Apply map config if available.
        if ((baseParts || starMap) && map) {
            nameParts = name.split('/');

            for (i = nameParts.length; i > 0; i -= 1) {
                nameSegment = nameParts.slice(0, i).join("/");

                if (baseParts) {
                    //Find the longest baseName segment match in the config.
                    //So, do joins on the biggest to smallest lengths of baseParts.
                    for (j = baseParts.length; j > 0; j -= 1) {
                        mapValue = map[baseParts.slice(0, j).join('/')];

                        //baseName segment has  config, find if it has one for
                        //this name.
                        if (mapValue) {
                            mapValue = mapValue[nameSegment];
                            if (mapValue) {
                                //Match, update name to the new value.
                                foundMap = mapValue;
                                foundI = i;
                                break;
                            }
                        }
                    }
                }

                if (foundMap) {
                    break;
                }

                //Check for a star map match, but just hold on to it,
                //if there is a shorter segment match later in a matching
                //config, then favor over this star map.
                if (!foundStarMap && starMap && starMap[nameSegment]) {
                    foundStarMap = starMap[nameSegment];
                    starI = i;
                }
            }

            if (!foundMap && foundStarMap) {
                foundMap = foundStarMap;
                foundI = starI;
            }

            if (foundMap) {
                nameParts.splice(0, foundI, foundMap);
                name = nameParts.join('/');
            }
        }

        return name;
    }

    function makeRequire(relName, forceSync) {
        return function () {
            //A version of a require function that passes a moduleName
            //value for items that may need to
            //look up paths relative to the moduleName
            var args = aps.call(arguments, 0);

            //If first arg is not require('string'), and there is only
            //one arg, it is the array form without a callback. Insert
            //a null so that the following concat is correct.
            if (typeof args[0] !== 'string' && args.length === 1) {
                args.push(null);
            }
            return req.apply(undef, args.concat([relName, forceSync]));
        };
    }

    function makeNormalize(relName) {
        return function (name) {
            return normalize(name, relName);
        };
    }

    function makeLoad(depName) {
        return function (value) {
            defined[depName] = value;
        };
    }

    function callDep(name) {
        if (hasProp(waiting, name)) {
            var args = waiting[name];
            delete waiting[name];
            defining[name] = true;
            main.apply(undef, args);
        }

        if (!hasProp(defined, name) && !hasProp(defining, name)) {
            throw new Error('No ' + name);
        }
        return defined[name];
    }

    //Turns a plugin!resource to [plugin, resource]
    //with the plugin being undefined if the name
    //did not have a plugin prefix.
    function splitPrefix(name) {
        var prefix,
            index = name ? name.indexOf('!') : -1;
        if (index > -1) {
            prefix = name.substring(0, index);
            name = name.substring(index + 1, name.length);
        }
        return [prefix, name];
    }

    /**
     * Makes a name map, normalizing the name, and using a plugin
     * for normalization if necessary. Grabs a ref to plugin
     * too, as an optimization.
     */
    makeMap = function (name, relName) {
        var plugin,
            parts = splitPrefix(name),
            prefix = parts[0];

        name = parts[1];

        if (prefix) {
            prefix = normalize(prefix, relName);
            plugin = callDep(prefix);
        }

        //Normalize according
        if (prefix) {
            if (plugin && plugin.normalize) {
                name = plugin.normalize(name, makeNormalize(relName));
            } else {
                name = normalize(name, relName);
            }
        } else {
            name = normalize(name, relName);
            parts = splitPrefix(name);
            prefix = parts[0];
            name = parts[1];
            if (prefix) {
                plugin = callDep(prefix);
            }
        }

        //Using ridiculous property names for space reasons
        return {
            f: prefix ? prefix + '!' + name : name, //fullName
            n: name,
            pr: prefix,
            p: plugin
        };
    };

    function makeConfig(name) {
        return function () {
            return (config && config.config && config.config[name]) || {};
        };
    }

    handlers = {
        require: function (name) {
            return makeRequire(name);
        },
        exports: function (name) {
            var e = defined[name];
            if (typeof e !== 'undefined') {
                return e;
            } else {
                return (defined[name] = {});
            }
        },
        module: function (name) {
            return {
                id: name,
                uri: '',
                exports: defined[name],
                config: makeConfig(name)
            };
        }
    };

    main = function (name, deps, callback, relName) {
        var cjsModule, depName, ret, map, i,
            args = [],
            callbackType = typeof callback,
            usingExports;

        //Use name if no relName
        relName = relName || name;

        //Call the callback to define the module, if necessary.
        if (callbackType === 'undefined' || callbackType === 'function') {
            //Pull out the defined dependencies and pass the ordered
            //values to the callback.
            //Default to [require, exports, module] if no deps
            deps = !deps.length && callback.length ? ['require', 'exports', 'module'] : deps;
            for (i = 0; i < deps.length; i += 1) {
                map = makeMap(deps[i], relName);
                depName = map.f;

                //Fast path CommonJS standard dependencies.
                if (depName === "require") {
                    args[i] = handlers.require(name);
                } else if (depName === "exports") {
                    //CommonJS module spec 1.1
                    args[i] = handlers.exports(name);
                    usingExports = true;
                } else if (depName === "module") {
                    //CommonJS module spec 1.1
                    cjsModule = args[i] = handlers.module(name);
                } else if (hasProp(defined, depName) ||
                           hasProp(waiting, depName) ||
                           hasProp(defining, depName)) {
                    args[i] = callDep(depName);
                } else if (map.p) {
                    map.p.load(map.n, makeRequire(relName, true), makeLoad(depName), {});
                    args[i] = defined[depName];
                } else {
                    throw new Error(name + ' missing ' + depName);
                }
            }

            ret = callback ? callback.apply(defined[name], args) : undefined;

            if (name) {
                //If setting exports via "module" is in play,
                //favor that over return value and exports. After that,
                //favor a non-undefined return value over exports use.
                if (cjsModule && cjsModule.exports !== undef &&
                        cjsModule.exports !== defined[name]) {
                    defined[name] = cjsModule.exports;
                } else if (ret !== undef || !usingExports) {
                    //Use the return value from the function.
                    defined[name] = ret;
                }
            }
        } else if (name) {
            //May just be an object definition for the module. Only
            //worry about defining if have a module name.
            defined[name] = callback;
        }
    };

    requirejs = require = req = function (deps, callback, relName, forceSync, alt) {
        if (typeof deps === "string") {
            if (handlers[deps]) {
                //callback in this case is really relName
                return handlers[deps](callback);
            }
            //Just return the module wanted. In this scenario, the
            //deps arg is the module name, and second arg (if passed)
            //is just the relName.
            //Normalize module name, if it contains . or ..
            return callDep(makeMap(deps, callback).f);
        } else if (!deps.splice) {
            //deps is a config object, not an array.
            config = deps;
            if (config.deps) {
                req(config.deps, config.callback);
            }
            if (!callback) {
                return;
            }

            if (callback.splice) {
                //callback is an array, which means it is a dependency list.
                //Adjust args if there are dependencies
                deps = callback;
                callback = relName;
                relName = null;
            } else {
                deps = undef;
            }
        }

        //Support require(['a'])
        callback = callback || function () {};

        //If relName is a function, it is an errback handler,
        //so remove it.
        if (typeof relName === 'function') {
            relName = forceSync;
            forceSync = alt;
        }

        //Simulate async callback;
        if (forceSync) {
            main(undef, deps, callback, relName);
        } else {
            //Using a non-zero value because of concern for what old browsers
            //do, and latest browsers "upgrade" to 4 if lower value is used:
            //http://www.whatwg.org/specs/web-apps/current-work/multipage/timers.html#dom-windowtimers-settimeout:
            //If want a value immediately, use require('id') instead -- something
            //that works in almond on the global level, but not guaranteed and
            //unlikely to work in other AMD implementations.
            setTimeout(function () {
                main(undef, deps, callback, relName);
            }, 4);
        }

        return req;
    };

    /**
     * Just drops the config on the floor, but returns req in case
     * the config return value is used.
     */
    req.config = function (cfg) {
        return req(cfg);
    };

    /**
     * Expose module registry for debugging and tooling
     */
    requirejs._defined = defined;

    define = function (name, deps, callback) {
        if (typeof name !== 'string') {
            throw new Error('See almond README: incorrect module build, no module name');
        }

        //This module may not have dependencies
        if (!deps.splice) {
            //deps is not an array, so probably means
            //an object literal or factory function for
            //the value. Adjust args.
            callback = deps;
            deps = [];
        }

        if (!hasProp(defined, name) && !hasProp(waiting, name)) {
            waiting[name] = [name, deps, callback];
        }
    };

    define.amd = {
        jQuery: true
    };
}());

define("almond/almond", function(){});

/*!
 * EventEmitter v4.2.11 - git.io/ee
 * Unlicense - http://unlicense.org/
 * Oliver Caldwell - http://oli.me.uk/
 * @preserve
 */
(function(){"use strict";function t(){}function i(t,n){for(var e=t.length;e--;)if(t[e].listener===n)return e;return-1}function n(e){return function(){return this[e].apply(this,arguments)}}var e=t.prototype,r=this,s=r.EventEmitter;e.getListeners=function(n){var r,e,t=this._getEvents();if(n instanceof RegExp){r={};for(e in t)t.hasOwnProperty(e)&&n.test(e)&&(r[e]=t[e])}else r=t[n]||(t[n]=[]);return r},e.flattenListeners=function(t){var e,n=[];for(e=0;e<t.length;e+=1)n.push(t[e].listener);return n},e.getListenersAsObject=function(n){var e,t=this.getListeners(n);return t instanceof Array&&(e={},e[n]=t),e||t},e.addListener=function(r,e){var t,n=this.getListenersAsObject(r),s="object"==typeof e;for(t in n)n.hasOwnProperty(t)&&-1===i(n[t],e)&&n[t].push(s?e:{listener:e,once:!1});return this},e.on=n("addListener"),e.addOnceListener=function(e,t){return this.addListener(e,{listener:t,once:!0})},e.once=n("addOnceListener"),e.defineEvent=function(e){return this.getListeners(e),this},e.defineEvents=function(t){for(var e=0;e<t.length;e+=1)this.defineEvent(t[e]);return this},e.removeListener=function(r,s){var n,e,t=this.getListenersAsObject(r);for(e in t)t.hasOwnProperty(e)&&(n=i(t[e],s),-1!==n&&t[e].splice(n,1));return this},e.off=n("removeListener"),e.addListeners=function(e,t){return this.manipulateListeners(!1,e,t)},e.removeListeners=function(e,t){return this.manipulateListeners(!0,e,t)},e.manipulateListeners=function(r,t,i){var e,n,s=r?this.removeListener:this.addListener,o=r?this.removeListeners:this.addListeners;if("object"!=typeof t||t instanceof RegExp)for(e=i.length;e--;)s.call(this,t,i[e]);else for(e in t)t.hasOwnProperty(e)&&(n=t[e])&&("function"==typeof n?s.call(this,e,n):o.call(this,e,n));return this},e.removeEvent=function(e){var t,r=typeof e,n=this._getEvents();if("string"===r)delete n[e];else if(e instanceof RegExp)for(t in n)n.hasOwnProperty(t)&&e.test(t)&&delete n[t];else delete this._events;return this},e.removeAllListeners=n("removeEvent"),e.emitEvent=function(r,o){var e,i,t,s,n=this.getListenersAsObject(r);for(t in n)if(n.hasOwnProperty(t))for(i=n[t].length;i--;)e=n[t][i],e.once===!0&&this.removeListener(r,e.listener),s=e.listener.apply(this,o||[]),s===this._getOnceReturnValue()&&this.removeListener(r,e.listener);return this},e.trigger=n("emitEvent"),e.emit=function(e){var t=Array.prototype.slice.call(arguments,1);return this.emitEvent(e,t)},e.setOnceReturnValue=function(e){return this._onceReturnValue=e,this},e._getOnceReturnValue=function(){return this.hasOwnProperty("_onceReturnValue")?this._onceReturnValue:!0},e._getEvents=function(){return this._events||(this._events={})},t.noConflict=function(){return r.EventEmitter=s,t},"function"==typeof define&&define.amd?define('EventEmitter',[],function(){return t}):"object"==typeof module&&module.exports?module.exports=t:r.EventEmitter=t}).call(this);
define('app/simplelayout/EventEmitter',["EventEmitter"], function(EE){

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

define('app/simplelayout/Block',["app/simplelayout/EventEmitter"], function(eventEmitter) {

  "use strict";

  function Block(content, type) {

    if (!(this instanceof Block)) {
      throw new TypeError("Block constructor cannot be called as a function.");
    }

    var frameFixTemplate = $.templates('<div class="iFrameFix"></div>');

    var template = $.templates(
      '<div data-type="{{:type}}" class="sl-block"><div class="sl-block-content">{{:content}}</div></div>'
    );

    return {

      committed: false,

      uid: null,

      toolbar: null,

      type: type,

      element: null,

      create: function() {
        var data = { "content": content, "type": type };
        this.element = $(template.render(data));
        this.fixFrame();
        return this.element;
      },

      fixFrame: function() {
        this.frame = $(frameFixTemplate.render());
        this.element.prepend(this.frame);
      },

      enableFrame: function() { this.frame.show(); },

      disableFrame: function() { this.frame.hide(); },

      content: function(toReplace) {
        $(".sl-block-content", this.element).html(toReplace);
        eventEmitter.trigger("blockReplaced", [this]);
      },

      commit: function() {
        this.committed = true;
        eventEmitter.trigger("blockCommitted", [this]);
      },

      attachToolbar: function(toolbar) {
        this.toolbar = toolbar;
        this.element.append(toolbar.element);
      },

      toJSON: function() { return { uid: this.uid, type: this.type }; }
    };

  }
  return Block;

});

define('app/simplelayout/idHelper',[], function() {

  "use strict";

  return {
    generateFromHash: function(hash) {
      if($.isEmptyObject(hash)) {
        return 0;
      }
      return Math.max.apply(null, Object.keys(hash)) + 1;
    }
  };

});

define('app/simplelayout/Column',["app/simplelayout/Block", "app/simplelayout/EventEmitter", "app/simplelayout/idHelper"], function(Block, eventEmitter, idHelper) {

  "use strict";

  function Column(column) {
    if (!(this instanceof Column)) {
      throw new TypeError("Column constructor cannot be called as a function.");
    }

    if (!column) { throw new Error("Columns are not defined."); }

    var template = $.templates("<div class='sl-column sl-col-{{:column}}''></div>");

    return {

      blocks: {},

      element: null,

      create: function() {
        this.element = $(template.render({ column: column }));
        return this.element;
      },

      insertBlock: function(blockOptions) {
        blockOptions = $.extend({
          type: "",
          content: ""
        }, blockOptions || {});
        var nextBlockId = idHelper.generateFromHash(this.blocks);
        var block = new Block(blockOptions.content, blockOptions.type);
        var blockElement = block.create();
        blockElement.data("blockId", nextBlockId);
        $.extend(blockElement.data(), this.element.data());
        if(blockOptions.source) {
          var data = $.extend(block.element.data(), $(blockOptions.source).data());
          block.element = $(blockOptions.source);
          $.extend(block.element.data(), data);
          block.type = block.element.data("type");
        }
        this.blocks[nextBlockId] = block;
        eventEmitter.trigger("blockInserted", [block]);
        return block;
      },

      deleteBlock: function(blockId) {
        if (!this.blocks[blockId]) {
          throw new Error("No block with id " + blockId + " inserted.");
        }
        this.blocks[blockId].element.remove();
        delete this.blocks[blockId];
        eventEmitter.trigger("blockDeleted");
      },

      commitBlocks: function() {
        if (Object.keys(this.getCommittedBlocks()).length === Object.keys(this.blocks).length) {
          throw new Error("No blocks inserted.");
        }
        for (var key in this.blocks) {
          this.blocks[key].commit();
        }
      },

      hasBlocks: function() { return Object.keys(this.blocks).length > 0; },

      deserialize: function() {
        var self = this;
        $(".sl-block", this.element).each(function(idx, e) {
          var block = self.insertBlock({ source: e });
          block.commit();
          block.fixFrame();
        });
      },

      getCommittedBlocks: function() {
        var committedBlocks = [];
        for (var key in this.blocks) {
          if (this.blocks[key].committed) {
            committedBlocks.push(this.blocks[key]);
          }
        }
        return committedBlocks;
      },

      getInsertedBlocks: function() {
        var insertedBlocks = [];
        for (var key in this.blocks) {
          if (!this.blocks[key].committed) {
            insertedBlocks.push(this.blocks[key]);
          }
        }
        return insertedBlocks;
      },

      toJSON: function() { return { blocks: this.blocks }; }

    };
  }

  return Column;

});

define('app/simplelayout/Layout',["app/simplelayout/Column", "app/simplelayout/EventEmitter"], function(Column, eventEmitter) {

  "use strict";

  function Layout(columns) {
    if (!(this instanceof Layout)) {
      throw new TypeError("Layout constructor cannot be called as a function.");
    }
    if (!columns) {
      throw new TypeError("Columns are not defined.");
    }

    var template = $.templates("<div class='sl-layout'></div>");

    return {

      committed: false,

      columns: {},

      toolbar: null,

      create: function(id, container) {
        this.element = $(template.render());
        this.element.data("layoutId", id);
        this.element.data("container", container);
        for (var i = 0; i < columns; i++) {
          var column = new Column(columns);
          this.columns[i] = column;
          var columnElement = column.create();
          $.extend(columnElement.data(), { columnId: i, layoutId: id, container: container });
          this.element.append(columnElement);
        }
        return this.element;
      },

      insertBlock: function(columnId, content, type) { return this.columns[columnId].insertBlock({ content: content, type: type }); },

      commit: function() {
        this.committed = true;
        eventEmitter.trigger("layoutCommitted", [this]);
      },

      deleteBlock: function(columnId, blockId) { this.columns[columnId].deleteBlock(blockId); },

      commitBlocks: function(columnId) { this.columns[columnId].commitBlocks(); },

      attachToolbar: function(toolbar) {
        this.toolbar = toolbar;
        this.element.append(toolbar.element);
      },

      getBlocks: function() {
        return $.map(this.columns, function(column) {
          return $.map(column.blocks, function(block) {
            return block;
          });
        });
      },

      getCommittedBlocks: function() {
        var committedBlocks = [];
        for(var key in this.columns) {
          committedBlocks = $.merge(this.columns[key].getCommittedBlocks(), committedBlocks);
        }
        return committedBlocks;
      },

      getInsertedBlocks: function() {
        var insertedBlocks = [];
        for(var key in this.columns) {
          insertedBlocks = $.merge(this.columns[key].getInsertedBlocks(), insertedBlocks);
        }
        return insertedBlocks;
      },

      hasBlocks: function() {
        var hasBlocks = false;
        $.each(this.columns, function(columnIdx, column) {
          if(column.hasBlocks()) {
            hasBlocks = true;
            return false;
          }
        });
        return hasBlocks;
      },

      toJSON: function() { return { columns: this.columns }; },

      deserialize: function() {
        var self = this;
        $(".sl-column", this.element).each(function(idx, e) {
          e = $(e);
          var column = self.columns[idx];
          var data = column.element.data();
          var stylingClass = column.element.attr("class");
          column.element = e;
          column.element.attr("class", stylingClass);
          $.extend(column.element.data(), data);
          column.deserialize();
        });
      }

    };
  }

  return Layout;

});

define('app/simplelayout/Layoutmanager',["app/simplelayout/Layout", "app/simplelayout/EventEmitter", "app/simplelayout/idHelper"], function(Layout, eventEmitter, idHelper) {

  "use strict";

  function Layoutmanager(_options) {

    if (!(this instanceof Layoutmanager)) {
      throw new TypeError("Layoutmanager constructor cannot be called as a function.");
    }

    var options = $.extend({ width: "100%" }, _options || {});

    var element;

    var id = 0;

    if (options.source) {
      element = $(options.source);
      element.addClass("sl-simplelayout");
    } else {
      var template = $.templates("<div class='sl-simplelayout' style='width:{{:width}};''></div>");
      element = $(template.render(options));
    }

    return {

      layouts: {},

      options: options,

      element: element,

      attachTo: function(target) { $(target).append(element); },

      insertLayout: function(layoutOptions) {
        layoutOptions = $.extend({
          columns: 4
        }, layoutOptions || {});
        var columns = layoutOptions.source ? $(".sl-column", layoutOptions.source).length : layoutOptions.columns;
        var layout = new Layout(columns);
        layout.create(id, element.data("container"));
        if(layoutOptions.source) {
          var data = layout.element.data();
          layout.element = layoutOptions.source;
          $.extend(layout.element.data(), data);
        }
        this.layouts[id] = layout;
        eventEmitter.trigger("layoutInserted", [layout]);
        id++;
        return layout;
      },

      deleteLayout: function(layoutId) {
        this.layouts[layoutId].element.remove();
        delete this.layouts[layoutId];
        eventEmitter.trigger("layoutDeleted", [this]);
      },

      commitLayouts: function() {
        for (var key in this.layouts) {
          this.layouts[key].commit();
        }
      },

      getCommittedLayouts: function() {
        var committedLayouts = {};
        for (var key in this.layouts) {
          if (this.layouts[key].committed) {
            committedLayouts[key] = this.layouts[key];
          }
        }
        return committedLayouts;
      },

      getBlock: function(layoutId, columnId, blockId) { return this.layouts[layoutId].columns[columnId].blocks[blockId]; },

      getCommittedBlocks: function() {
        var committedBlocks = [];
        for(var key in this.layouts) {
          committedBlocks = $.merge(this.layouts[key].getCommittedBlocks(), committedBlocks);
        }
        return committedBlocks;
      },

      getInsertedBlocks: function() {
        var insertedBlocks = [];
        for(var key in this.layouts) {
          insertedBlocks = $.merge(this.layouts[key].getInsertedBlocks(), insertedBlocks);
        }
        return insertedBlocks;
      },

      setBlock: function(layoutId, columnId, blockId, block) { this.layouts[layoutId].columns[columnId].blocks[blockId] = block; },

      insertBlock: function(layoutId, columnId, content, type) {
        var layout = this.layouts[layoutId];
        var block = layout.insertBlock(columnId, content, type);
        return block;
      },

      deleteBlock: function(layoutId, columnId, blockId) { this.layouts[layoutId].deleteBlock(columnId, blockId); },

      moveLayout: function(oldLayout, newLayoutId) {
        var self = this;
        $.each(this.layouts[newLayoutId].columns, function(colIdx, column) {
          column.element.data("layoutId", newLayoutId);
          column.element.data("container", self.element.data("container"));
          $.each(column.blocks, function(bloIdx, block) {
            block.element.data("layoutId", newLayoutId);
            block.element.data("container", self.element.data("container"));
          });
        });
        eventEmitter.trigger("layoutMoved", [newLayoutId]);
      },

      commitBlocks: function(layoutId, columnId) { this.layouts[layoutId].commitBlocks(columnId); },

      hasLayouts: function() { return Object.keys(this.layouts).length > 0; },

      moveBlock: function(oldLayoutId, oldColumnId, oldBlockId, newLayoutId, newColumnId) {
        var block = this.layouts[oldLayoutId].columns[oldColumnId].blocks[oldBlockId];

        var nextBlockId = idHelper.generateFromHash(this.layouts[newLayoutId].columns[newColumnId].blocks);
        $.extend(block.element.data(), { layoutId: newLayoutId, columnId: newColumnId, blockId: nextBlockId });
        delete this.layouts[oldLayoutId].columns[oldColumnId].blocks[oldBlockId];
        this.layouts[newLayoutId].columns[newColumnId].blocks[nextBlockId] = block;
        eventEmitter.trigger("blockMoved", [nextBlockId]);
      },

      deserialize: function() {
        var self = this;
        $(".sl-layout", this.element).each(function(idx, e) {
          e = $(e);
          var layout = self.insertLayout({ source: e });
          layout.commit();
          layout.deserialize();
        });
      },

      toJSON: function() { return { layouts: this.layouts, container: this.element.attr("id") }; }
    };

  }

  return Layoutmanager;

});

define('app/simplelayout/Toolbar',[], function() {

  "use strict";

  function Toolbar(_actions, orientation, type) {

    if (!(this instanceof Toolbar)) {
      throw new TypeError("Toolbar constructor cannot be called as a function.");
    }

    var defaultActions = {};

    var actions = $.extend(defaultActions, _actions || {});

    var normalizedActions = [];

    $.each(actions, function(key, value) {
      normalizedActions.push(value);
    });

    var template = $.templates(
      /*eslint no-multi-str: 0 */
      "<ul class='sl-toolbar{{if type}}-{{:type}}{{/if}}{{if orientation}} {{:orientation}}{{/if}}'> \
        {{for actions}} \
          <li> \
            <a {{props}} {{>key}}='{{>prop}}' {{/props}}></a> \
          </li> \
          <li class='delimiter'></li> \
        {{/for}} \
      </ul>");

    var element = $(template.render({
      actions: normalizedActions,
      orientation: orientation,
      type: type
    }));

    return {

      element: element

    };

  }
  return Toolbar;

});

define('app/toolbox/Toolbox',[], function() {

  "use strict";

  function Toolbox(_options) {

    if (!(this instanceof Toolbox)) {
      throw new TypeError("Toolbox constructor cannot be called as a function.");
    }

    if (!_options || !_options.layouts || _options.layouts.length === 0) {
      throw new Error("No layouts defined.");
    }

    var options = $.extend({
      components: {}
    }, _options || {});

    var normalizeCompare = function(a, b) {
      return a.localeCompare(b, "de", {caseFirst: "lower"});
    };

    var template = $.templates(
      /*eslint no-multi-str: 0 */
      "<div id='sl-toolbox' class='sl-toolbox'> \
          <div class='components'> \
            <div class='addables'> \
              <a class='sl-toolbox-header'>Komponenten</a> \
                <div class='sl-toolbox-components'> \
                  {{for components}} \
                    <a class='sl-toolbox-component' title='{{:description}}' data-type='{{:contentType}}' data-form_url='{{:formUrl}}'> \
                      <i class='icon-{{:contentType}}'></i>{{:title}} \
                    </a> \
                  {{/for}} \
                </div> \
              <a class='sl-toolbox-header'>Layout</a> \
                {{props layouts}} \
                  <a class='sl-toolbox-layout' data-columns='{{>prop}}'> \
                    <i class='icon-layout'></i>{{>prop}} - Spalten Layout \
                  </a> \
                 {{/props}} \
            </div> \
            <a class='sl-toolbox-header sl-toolbox-handle'>Toolbox</a> \
          </div> \
        </div>");

    var blocks = [];
    var layoutActions = [];
    if (!$.isEmptyObject(options.components)) {
      blocks = $.map(options.components.addableBlocks, function(component) { return component; }).sort(function(a, b) {
        return normalizeCompare(a.title, b.title);
      });
      if(options.components.layoutActions) {
        layoutActions = $.map(options.components.layoutActions.actions, function(action) { return action; }).sort(function(a, b) {
          return normalizeCompare(a.title, b.title);
        });
      }
    }

    options.layoutActions = layoutActions;

    var data = {
      "components": blocks,
      "layouts": options.layouts
    };

    var element = $(template.render(data));

    $(".sl-toolbox-handle", element).on("click", function() { $(".addables").toggleClass("close"); });

    return {

      options: options,

      element: element,

      disableComponents: function() { $(".sl-toolbox-components", this.element).addClass("disabled"); },

      enableComponents: function() { $(".sl-toolbox-components", this.element).removeClass("disabled"); },

      attachTo: function(target) {
        target.append(element);
      }

    };

  }
  return Toolbox;

});

define('app/simplelayout/Simplelayout',["app/simplelayout/Layoutmanager", "app/simplelayout/Toolbar", "app/toolbox/Toolbox", "app/simplelayout/EventEmitter", "app/simplelayout/idHelper"], function(Layoutmanager, Toolbar, Toolbox, eventEmitter, idHelper) {

  "use strict";

  function Simplelayout(_options) {

    if (!(this instanceof Simplelayout)) {
      throw new TypeError("Simplelayout constructor cannot be called as a function.");
    }

    var options = $.extend({
      toolbox: new Toolbox({layouts: [1, 2, 4]})
    }, _options || {});

    var managers = {};

    var id = 0;

    var moveLayout = function(layout, newManagerId) {
      var layoutData = layout.element.data();
      var manager = managers[layoutData.container];
      var nextLayoutId = idHelper.generateFromHash(managers[newManagerId].layouts);
      $.extend(layout.element.data(), { layoutId: nextLayoutId, container: newManagerId });
      delete manager.layouts[layoutData.layoutId];
      managers[newManagerId].layouts[nextLayoutId] = layout;
      managers[newManagerId].moveLayout(layout, nextLayoutId);
      eventEmitter.trigger("layoutMoved", [layout]);
    };

    var moveBlock = function(block, newManagerId, newLayoutId, newColumnId) {
      var blockData = block.element.data();
      var newData = { container: newManagerId, layoutId: newLayoutId, columnId: newColumnId };
      var newManager = managers[newManagerId];
      delete managers[blockData.container].layouts[blockData.layoutId].columns[blockData.columnId].blocks[blockData.blockId];
      var nextBlockId = idHelper.generateFromHash(managers[newManagerId].layouts[newLayoutId].columns[newColumnId].blocks);
      newData.blockId = nextBlockId;
      $.extend(block.element.data(), newData);
      newManager.setBlock(newLayoutId, newColumnId, nextBlockId, block);
      eventEmitter.trigger("blockMoved", [block]);
    };

    var getCommittedBlocks = function() {
      var committedBlocks = [];
      for(var key in managers) {
        committedBlocks = $.merge(managers[key].getCommittedBlocks(), committedBlocks);
      }
      return committedBlocks;
    };

    var getInsertedBlocks = function() {
      var insertedBlocks = [];
      for(var key in managers) {
        insertedBlocks = $.merge(managers[key].getInsertedBlocks(), insertedBlocks);
      }
      return insertedBlocks;
    };

    var disableFrames = function() {
      $.each(getCommittedBlocks(), function(idx, block) {
        block.disableFrame();
      });
    };

    var enableFrames = function() {
      $.each(getCommittedBlocks(), function(idx, block) {
        block.enableFrame();
      });
    };

    var TOOLBOX_COMPONENT_DRAGGABLE_SETTINGS = {
      helper: "clone",
      cursor: "pointer",
      start: function() {
        enableFrames();
        if($(this).hasClass("sl-toolbox-component")) {
          $(document.documentElement).addClass("sl-block-dragging");
        } else {
          $(document.documentElement).addClass("sl-layout-dragging");
        }
      },
      stop: function() {
        disableFrames();
        $(document.documentElement).removeClass("sl-block-dragging sl-layout-dragging");
      }
    };

    var sortableHelper = function(){ return $('<div class="draggableHelper"><div>'); };

    var animatedrop = function(ui){
      ui.item.addClass("animated");
      setTimeout(function(){
        ui.item.removeClass("animated");
      }, 1);
    };

    var canMove = true;
    var originalLayout;

    var LAYOUT_SORTABLE = {
      connectWith: ".sl-simplelayout",
      items: ".sl-layout",
      handle: ".sl-toolbar-layout .move",
      placeholder: "layout-placeholder",
      axis: "y",
      tolerance: "intersects",
      forcePlaceholderSize: true,
      helper: sortableHelper,
      receive: function(event, ui) {
        var manager = managers[$(this).data("container")];
        if(originalLayout) {
          moveLayout(originalLayout, $(this).data("container"));
          originalLayout = null;
        } else {
          var item = $(this).find(".ui-draggable");
          var layout = manager.insertLayout({ columns: ui.item.data("columns") });
          layout.element.insertAfter(item);
          item.remove();
        }
        canMove = false;
      },
      remove: function(event, ui) {
        originalLayout = managers[$(this).data("container")].layouts[ui.item.data("layoutId")];
      },
      start: function() {
        $(document.documentElement).addClass("sl-layout-dragging");
        enableFrames();
        canMove = true;
      },
      stop: function(event, ui) {
        $(document.documentElement).removeClass("sl-layout-dragging");
        disableFrames();
        animatedrop(ui);
        if(canMove) {
          var itemData = ui.item.data();
          var manager = managers[itemData.container];
          var layout = manager.layouts[itemData.layoutId];
          manager.moveLayout(layout, itemData.layoutId);
        }
      }
    };

    var originalBlock;

    var BLOCK_SORTABLE = {
      connectWith: ".sl-column",
      placeholder: "block-placeholder",
      forcePlaceholderSize: true,
      handle: ".sl-toolbar-block .move",
      helper: sortableHelper,
      tolerance: "pointer",
      receive: function(event, ui) {
        var manager = managers[$(this).data("container")];
        var data = $(this).data();
        if(originalBlock) {
          moveBlock(originalBlock, data.container, data.layoutId, data.columnId);
          originalBlock = null;
        }
        else if(typeof ui.item.data("layoutId") === "undefined") {
          var item = $(this).find(".ui-draggable");
          var type = ui.item.data("type");
          var block = manager.insertBlock(data.layoutId, data.columnId, null, type);
          block.element.insertAfter(item);
          item.remove();
        }
        canMove = false;
      },
      remove: function(event, ui) {
        var itemData = ui.item.data();
        originalBlock = managers[itemData.container].getBlock(itemData.layoutId, itemData.columnId, itemData.blockId);
      },
      start: function() {
        $(document.documentElement).addClass("sl-block-dragging");
        canMove = true;
        enableFrames();
      },
      stop: function(event, ui) {
        $(document.documentElement).removeClass("sl-block-dragging");
        disableFrames();
        animatedrop(ui);
        if(canMove) {
          var itemData = ui.item.data();
          var data = $(this).data();
          managers[itemData.container].moveBlock(itemData.layoutId, itemData.columnId, itemData.blockId, data.layoutId, data.columnId);
        }
      }
    };

    var on = function(eventType, callback) { eventEmitter.on(eventType, callback); };

    var bindToolboxEvents = function() {
      options.toolbox.element.find(".sl-toolbox-component, .sl-toolbox-layout").draggable(TOOLBOX_COMPONENT_DRAGGABLE_SETTINGS);
      options.toolbox.element.find(".sl-toolbox-layout").draggable("option", "connectToSortable", ".sl-simplelayout");
      options.toolbox.element.find(".sl-toolbox-component").draggable("option", "connectToSortable", ".sl-column");
    };

    var bindLayoutEvents = function() {
      $(".sl-simplelayout").sortable(LAYOUT_SORTABLE);
      $(".sl-column").sortable(BLOCK_SORTABLE);
      on("layoutCommitted", function(layout) {
        $(".sl-column", layout.element).sortable(BLOCK_SORTABLE);
      });
    };

    bindLayoutEvents();
    bindToolboxEvents();

    on("layoutInserted", function(layout) {
      var layoutToolbar = new Toolbar(options.toolbox.options.layoutActions, "vertical", "layout");
      layout.attachToolbar(layoutToolbar);
    });

    on("blockInserted", function(block) {
      var blockToolbar = new Toolbar(options.toolbox.options.components.addableBlocks[block.type].actions, "horizontal", "block");
      block.attachToolbar(blockToolbar);
    });

    return {

      options: options,

      moveLayout: moveLayout,

      moveBlock: moveBlock,

      getManagers: function() { return managers; },

      serialize: function() { return JSON.stringify(managers); },

      deserialize: function(target) {
        managers = {};
        id = 0;
        var self = this;
        $(".sl-simplelayout", target).each(function(idx, e) {
          var manager = self.insertManager({ source: e });
          manager.deserialize();
        });
      },

      insertManager: function(managerOptions) {
        var manager = new Layoutmanager(managerOptions);
        manager.element.data("container", id);
        managers[id] = manager;
        id++;
        return manager;
      },

      getCommittedBlocks: getCommittedBlocks,

      getInsertedBlocks: getInsertedBlocks,

      attachTo: function(target) {
        $.each(managers, function(idx, manager) {
          manager.attachTo(target);
        });
      },

      on: on

    };

  }

  return Simplelayout;

});

/*! JsRender v1.0.0-beta: http://www.jsviews.com/#jsrender
informal pre V1.0 commit counter: 64pre*/
!function(e){if("function"==typeof define&&define.amd)define('jsrender',e);else if("object"==typeof exports){var t=module.exports=e(!0,require("fs"));t.renderFile=t.__express=function(e,n,r){var i=t.templates("@"+e).render(n);return r&&r(null,i),i}}else e(!1)}(function(e,t){"use strict";function n(e,t){return function(){var n,r=this,i=r.base;return r.base=e,n=t.apply(r,arguments),r.base=i,n}}function r(e,t){return jt(t)&&(t=n(e?e._d?e:n(s,e):s,t),t._d=1),t}function i(e,t){for(var n in t.props)ct.test(n)&&(e[n]=r(e[n],t.props[n]))}function a(e){return e}function s(){return""}function o(e){try{throw"dbg breakpoint"}catch(t){}return this.base?this.baseApply(arguments):e}function l(e){Nt._dbgMode=e!==!1}function p(e){this.name=(G.link?"JsViews":"JsRender")+" Error",this.message=e||this.name}function d(e,t){var n;for(n in t)e[n]=t[n];return e}function u(e,t,n){return(0!==this||e)&&(W=e?e.charAt(0):W,X=e?e.charAt(1):X,Y=t?t.charAt(0):Y,et=t?t.charAt(1):et,tt=n||tt,e="\\"+W+"(\\"+tt+")?\\"+X,t="\\"+Y+"\\"+et,q="(?:(?:(\\w+(?=[\\/\\s\\"+Y+"]))|(?:(\\w+)?(:)|(>)|!--((?:[^-]|-(?!-))*)--|(\\*)))\\s*((?:[^\\"+Y+"]|\\"+Y+"(?!\\"+et+"))*?)",$t.rTag=q+")",q=new RegExp(e+q+"(\\/)?|(?:\\/(\\w+)))"+t,"g"),H=new RegExp("<.*>|([^\\\\]|^)[{}]|"+e+".*"+t)),[W,X,Y,et,tt]}function c(e,t){t||(t=e,e=void 0);var n,r,i,a,s=this,o=!t||"root"===t;if(e){if(a=s.type===t?s:void 0,!a)if(n=s.views,s._.useKey){for(r in n)if(a=n[r].get(e,t))break}else for(r=0,i=n.length;!a&&i>r;r++)a=n[r].get(e,t)}else if(o)for(;s.parent.parent;)a=s=s.parent;else for(;s&&!a;)a=s.type===t?s:void 0,s=s.parent;return a}function f(){var e=this.get("item");return e?e.index:void 0}function g(){return this.index}function v(e){var t,n=this,r=n.linkCtx,i=(n.ctx||{})[e];return void 0===i&&r&&r.ctx&&(i=r.ctx[e]),void 0===i&&(i=Mt[e]),i&&jt(i)&&!i._wrp&&(t=function(){return i.apply(this&&this!==z?this:n,arguments)},t._wrp=!0,d(t,i)),t||i}function m(e,t,n,r){var a,s,o="number"==typeof n&&t.tmpl.bnds[n-1],l=t.linkCtx;return void 0!==r?n=r={props:{},args:[r]}:o&&(n=o(t.data,t,kt)),s=n.args[0],(e||o)&&(a=l&&l.tag,a||(a=d(new $t._tg,{_:{inline:!l,bnd:o,unlinked:!0},tagName:":",cvt:e,flow:!0,tagCtx:n}),l&&(l.tag=a,a.linkCtx=l),n.ctx=J(n.ctx,(l?l.view:t).ctx)),a._er=r&&s,i(a,n),n.view=t,a.ctx=n.ctx||{},n.ctx=void 0,t._.tag=a,s=a.cvtArgs(a.convert||"true"!==e&&e)[0],s=o&&t._.onRender?t._.onRender(s,t,o):s,t._.tag=void 0),void 0!=s?s:""}function h(e){var t=this,n=t.tagCtx,r=n.view,i=n.args;return e=t.convert||e,e=e&&(""+e===e?r.getRsc("converters",e)||V("Unknown converter: '"+e+"'"):e),i=i.length||n.index?e?i.slice():i:[r.data],e&&(e.depends&&(t.depends=$t.getDeps(t.depends,t,e.depends,e)),i[0]=e.apply(t,i)),i}function w(e,t){for(var n,r,i=this;void 0===n&&i;)r=i.tmpl&&i.tmpl[e],n=r&&r[t],i=i.parent;return n||kt[e][t]}function x(e,t,n,r,a,s){t=t||D;var o,l,p,d,u,c,f,g,v,m,h,w,x,b,_,y,k,C,j="",A=t.linkCtx||0,T=t.ctx,M=n||t.tmpl,$="number"==typeof r&&t.tmpl.bnds[r-1];for("tag"===e._is?(o=e,e=o.tagName,r=o.tagCtxs,p=o.template):(l=t.getRsc("tags",e)||V("Unknown tag: {{"+e+"}} "),p=l.template),void 0!==s?(j+=s,r=s=[{props:{},args:[]}]):$&&(r=$(t.data,t,kt)),g=r.length,f=0;g>f;f++)m=r[f],(!A||!A.tag||f&&!A.tag._.inline||o._er)&&((w=m.tmpl)&&(w=m.content=M.tmpls[w-1]),m.index=f,m.tmpl=p||w,m.render=R,m.view=t,m.ctx=J(m.ctx,T)),(n=m.props.tmpl)&&(n=""+n===n?t.getRsc("templates",n)||Tt(n):n,m.tmpl=n),o||(o=new l._ctr,x=!!o.init,o.parent=c=T&&T.tag,o.tagCtxs=r,A&&(o._.inline=!1,A.tag=o,o.linkCtx=A),(o._.bnd=$||A.fn)?o._.arrVws={}:o.dataBoundOnly&&V("{^{"+e+"}} tag must be data-bound")),m.tag=o,o.dataMap&&o.tagCtxs&&(m.map=o.tagCtxs[f].map),o.flow||(h=m.ctx=m.ctx||{},d=o.parents=h.parentTags=T&&J(h.parentTags,T.parentTags)||{},c&&(d[c.tagName]=c),d[o.tagName]=h.tag=o);if(($||A)&&(t._.tag=o),!(o._er=s)){for(i(o,r[0]),o.rendering={},f=0;g>f;f++)m=o.tagCtx=o.tagCtxs[f],k=m.props,y=o.cvtArgs(),(b=k.dataMap||o.dataMap)&&(y.length||k.dataMap)&&(_=m.map,(!_||_.src!==y[0]||a)&&(_&&_.src&&_.unmap(),_=m.map=b.map(y[0],k)),y=[_.tgt]),o.ctx=m.ctx,f||(x&&(C=o.template,o.init(m,A,o.ctx),x=void 0,o.template!==C&&(o._.tmpl=o.template)),A&&(A.attr=o.attr=A.attr||o.attr),u=o.attr,o._.noVws=u&&u!==ht),v=void 0,o.render&&(v=o.render.apply(o,y)),y.length||(y=[t]),void 0===v&&(v=m.render(y.length?y[0]:t,!0)||(a?void 0:"")),j=j?j+(v||""):v;o.rendering=void 0}return o.tagCtx=o.tagCtxs[0],o.ctx=o.tagCtx.ctx,o._.noVws&&o._.inline&&(j="text"===u?Rt.html(j):""),$&&t._.onRender?t._.onRender(j,t,$):j}function b(e,t,n,r,i,a,s,o){var l,p,d,u,c=this,g="array"===t;c.content=s,c.views=g?[]:{},c.parent=n,c.type=t||"top",c.data=r,c.tmpl=i,u=c._={key:0,useKey:g?0:1,id:""+vt++,onRender:o,bnds:{}},c.linked=!!o,n?(l=n.views,p=n._,p.useKey?(l[u.key="_"+p.useKey++]=c,c.index=bt,c.getIndex=f,d=p.tag,u.bnd=g&&(!d||!!d._.bnd&&d)):l.length===(u.key=c.index=a)?l.push(c):l.splice(a,0,c),c.ctx=e||n.ctx):c.ctx=e}function _(e){var t,n,r,i,a,s,o;for(t in yt)if(a=yt[t],(s=a.compile)&&(n=e[t+"s"]))for(r in n)i=n[r]=s(r,n[r],e,0),i._is=t,i&&(o=$t.onStore[t])&&o(r,i,s)}function y(e,t,n){function i(){var t=this;t._={inline:!0,unlinked:!0},t.tagName=e}var a,s,o,l=new $t._tg;if(jt(t)?t={depends:t.depends,render:t}:""+t===t&&(t={template:t}),s=t.baseTag){t.flow=!!t.flow,t.baseTag=s=""+s===s?n&&n.tags[s]||Vt[s]:s,l=d(l,s);for(o in t)l[o]=r(s[o],t[o])}else l=d(l,t);return void 0!==(a=l.template)&&(l.template=""+a===a?Tt[a]||Tt(a):a),l.init!==!1&&((i.prototype=l).constructor=l._ctr=i),n&&(l._parentTmpl=n),l}function k(e){return this.base.apply(this,e)}function C(e,n,r,i){function a(n){var a;if(""+n===n||n.nodeType>0&&(s=n)){if(!s)if("@"===n.charAt(0))t?n=Tt[e=e||(n=t.realpathSync(n.slice(1)))]=Tt[e]||C(e,t.readFileSync(n,"utf8"),r,i):s=P.getElementById(n);else if(G.fn&&!H.test(n))try{s=G(P).find(n)[0]}catch(o){}s&&(i?n=s.innerHTML:((a=s.getAttribute(xt))&&(n=Tt[a])&&e!==a&&delete Tt[a],e=e||a||"_"+gt++,a||(n=C(e,s.innerHTML,r,i)),s.setAttribute(xt,e),Tt[n.tmplName=e]=n),s=void 0)}else n.fn||(n=void 0);return n}var s,o,l=n=n||"";return 0===i&&(i=void 0,l=a(l)),i=i||(n.markup?n:{}),i.tmplName=e,r&&(i._parentTmpl=r),!l&&n.markup&&(l=a(n.markup))&&l.fn&&(l=l.markup),void 0!==l?(l.fn||n.fn?l.fn&&(o=l):(n=A(l,i),N(l.replace(st,"\\$&"),n)),o||(_(i),o=d(function(){return n.render.apply(n,arguments)},n)),e&&!r&&(_t[e]=o),o):void 0}function j(e){function t(t,n){this.tgt=e.getTgt(t,n)}return jt(e)&&(e={getTgt:e}),e.baseMap&&(e=d(d({},e.baseMap),e)),e.map=function(e,n){return new t(e,n)},e}function A(e,t){var n,r=Nt.wrapMap||{},i=d({tmpls:[],links:{},bnds:[],_is:"template",render:R},t);return i.markup=e,t.htmlTag||(n=pt.exec(e),i.htmlTag=n?n[1].toLowerCase():""),n=r[i.htmlTag],n&&n!==r.div&&(i.markup=G.trim(i.markup)),i}function T(e,t){function n(i,a,s){var o,l,p,d;if(i&&typeof i===wt&&!i.nodeType&&!i.markup&&!i.getTgt){for(p in i)n(p,i[p],a);return kt}return void 0===a&&(a=i,i=void 0),i&&""+i!==i&&(s=a,a=i,i=void 0),d=s?s[r]=s[r]||{}:n,l=t.compile,null===a?i&&delete d[i]:(a=l?l(i,a,s,0):a,i&&(d[i]=a)),l&&a&&(a._is=e),a&&(o=$t.onStore[e])&&o(i,a,l),a}var r=e+"s";kt[r]=n}function R(e,t,n,r,i,a){var s,o,l,p,d,u,c,f,g=r,v="";if(t===!0?(n=t,t=void 0):typeof t!==wt&&(t=void 0),(l=this.tag)?(d=this,p=l._.tmpl||d.tmpl,g=g||d.view,arguments.length||(e=g)):p=this,p){if(!g&&e&&"view"===e._is&&(g=e),g&&e===g&&(e=g.data),p.fn||(p=l._.tmpl=Tt[p]||Tt(p)),Q=Q||(u=!g),g||((t=t||{}).root=e),!Q||p.useViews)v=M(p,e,t,n,g,i,a,l);else{if(g?(c=g.data,f=g.index,g.index=bt):(g=D,g.data=e,g.ctx=t),At(e)&&!n)for(s=0,o=e.length;o>s;s++)g.index=s,g.data=e[s],v+=p.fn(e[s],g,kt);else v+=p.fn(e,g,kt);g.data=c,g.index=f}u&&(Q=void 0)}return v}function M(e,t,n,r,i,a,s,o){function l(e){_=d({},n),_[x]=e}var p,u,c,f,g,v,m,h,w,x,_,y,k="";if(o&&(w=o.tagName,y=o.tagCtx,n=n?J(n,o.ctx):o.ctx,m=y.content,y.props.link===!1&&(n=n||{},n.link=!1),(x=y.props.itemVar)&&("~"!==x.charAt(0)&&$("Use itemVar='~myItem'"),x=x.slice(1))),i&&(m=m||i.content,s=s||i._.onRender,n=n||i.ctx),a===!0&&(v=!0,a=0),s&&(n&&n.link===!1||o&&o._.noVws)&&(s=void 0),h=s,s===!0&&(h=void 0,s=i._.onRender),n=e.helpers?J(e.helpers,n):n,_=n,At(t)&&!r)for(c=v?i:void 0!==a&&i||new b(n,"array",i,t,e,a,m,s),x&&(c.it=x),x=c.it,p=0,u=t.length;u>p;p++)x&&l(t[p]),f=new b(_,"item",c,t[p],e,(a||0)+p,m,s),g=e.fn(t[p],f,kt),k+=c._.onRender?c._.onRender(g,f):g;else x&&l(t),c=v?i:new b(_,w||"data",i,t,e,a,m,s),o&&!o.flow&&(c.tag=o),k+=e.fn(t,c,kt);return h?h(k,c):k}function V(e,t,n){var r=Nt.onError(e,t,n);if(""+e===e)throw new $t.Err(r);return!t.linkCtx&&t.linked?Rt.html(r):r}function $(e){V("Syntax error\n"+e)}function N(e,t,n,r,i){function a(t){t-=f,t&&v.push(e.substr(f,t).replace(it,"\\n"))}function s(t,n){t&&(t+="}}",$((n?"{{"+n+"}} block has {{/"+t+" without {{"+t:"Unmatched or missing {{/"+t)+", in template:\n"+e))}function o(o,l,c,h,w,x,b,_,y,k,C,j){x&&(w=":",h=ht),k=k||n&&!i;var A=(l||n)&&[[]],T="",R="",M="",V="",N="",E="",S="",U="",J=!k&&!w&&!b;c=c||(y=y||"#data",w),a(j),f=j+o.length,_?u&&v.push(["*","\n"+y.replace(/^:/,"ret+= ").replace(at,"$1")+";\n"]):c?("else"===c&&(lt.test(y)&&$('for "{{else if expr}}" use "{{else expr}}"'),A=m[7]&&[[]],m[8]=e.substring(m[8],j),m=g.pop(),v=m[2],J=!0),y&&I(y.replace(it," "),A,t).replace(ot,function(e,t,n,r,i,a,s,o){return r="'"+i+"':",s?(R+=a+",",V+="'"+o+"',"):n?(M+=r+a+",",E+=r+"'"+o+"',"):t?S+=a:("trigger"===i&&(U+=a),T+=r+a+",",N+=r+"'"+o+"',",d=d||ct.test(i)),""}).slice(0,-1),A&&A[0]&&A.pop(),p=[c,h||!!r||d||"",J&&[],F(V,N,E),F(R,T,M),S,U,A||0],v.push(p),J&&(g.push(m),m=p,m[8]=f)):C&&(s(C!==m[0]&&"else"!==m[0]&&C,m[0]),m[8]=e.substring(m[8],j),m=g.pop()),s(!m&&C),v=m[2]}var l,p,d,u=Nt.allowCode||t&&t.allowCode,c=[],f=0,g=[],v=c,m=[,,c];return u&&(t.allowCode=u),n&&(e=W+e+et),s(g[0]&&g[0][2].pop()[0]),e.replace(q,o),a(e.length),(f=c[c.length-1])&&s(""+f!==f&&+f[8]===f[8]&&f[0]),n?(l=U(c,e,n),E(l,[c[0][7]])):l=U(c,t),l}function E(e,t){var n,r,i=0,a=t.length;for(e.deps=[];a>i;i++){r=t[i];for(n in r)"_jsvto"!==n&&r[n].length&&(e.deps=e.deps.concat(r[n]))}e.paths=r}function F(e,t,n){return[e.slice(0,-1),t.slice(0,-1),n.slice(0,-1)]}function S(e,t){return"\n	"+(t?t+":{":"")+"args:["+e[0]+"]"+(e[1]||!t?",\n	props:{"+e[1]+"}":"")+(e[2]?",\n	ctx:{"+e[2]+"}":"")}function I(e,t,n){function r(r,h,w,x,b,_,y,k,C,j,A,T,R,M,V,E,F,S,I,U){function J(e,n,r,s,o,l,u,c){var f="."===r;if(r&&(b=b.slice(n.length),f||(e=(s?'view.hlp("'+s+'")':o?"view":"data")+(c?(l?"."+l:s?"":o?"":"."+r)+(u||""):(c=s?"":o?l||"":r,"")),e+=c?"."+c:"",e=n+("view.data"===e.slice(0,9)?e.slice(5):e)),p)){if(B="linkTo"===i?a=t._jsvto=t._jsvto||[]:d.bd,L=f&&B[B.length-1]){if(L._jsv){for(;L.sb;)L=L.sb;L.bnd&&(b="^"+b.slice(1)),L.sb=b,L.bnd=L.bnd||"^"===b.charAt(0)}}else B.push(b);m[g]=I+(f?1:0)}return e}x=p&&x,x&&!k&&(b=x+b),_=_||"",w=w||h||T,b=b||C,j=j||F||"";var K,O,B,L,q;if(!y||l||o){if(p&&E&&!l&&!o&&(!i||s||a)&&(K=m[g-1],U.length-1>I-(K||0))){if(K=U.slice(K,I+r.length),O!==!0)if(B=a||u[g-1].bd,L=B[B.length-1],L&&L.prm){for(;L.sb&&L.sb.prm;)L=L.sb;q=L.sb={path:L.sb,bnd:L.bnd}}else B.push(q={path:B.pop()});E=X+":"+K+" onerror=''"+Y,O=f[E],O||(f[E]=!0,f[E]=O=N(E,n,!0)),O!==!0&&q&&(q._jsv=O,q.prm=d.bd,q.bnd=q.bnd||q.path&&q.path.indexOf("^")>=0)}return l?(l=!R,l?r:T+'"'):o?(o=!M,o?r:T+'"'):(w?(m[g]=I++,d=u[++g]={bd:[]},w):"")+(S?g?"":(c=U.slice(c,I),(i?(i=s=a=!1,"\b"):"\b,")+c+(c=I+r.length,p&&t.push(d.bd=[]),"\b")):k?(g&&$(e),p&&t.pop(),i=b,s=x,c=I+r.length,x&&(p=d.bd=t[i]=[]),b+":"):b?b.split("^").join(".").replace(nt,J)+(j?(d=u[++g]={bd:[]},v[g]=!0,j):_):_?_:V?(v[g]=!1,d=u[--g],V+(j?(d=u[++g],v[g]=!0,j):"")):A?(v[g]||$(e),","):h?"":(l=R,o=M,'"'))}$(e)}var i,a,s,o,l,p=t&&t[0],d={bd:p},u={0:d},c=0,f=n?n.links:p&&(p.links=p.links||{}),g=0,v={},m={};return(e+(n?" ":"")).replace(rt,r)}function U(e,t,n){var r,i,a,s,o,l,p,d,u,c,f,g,v,m,h,w,x,b,_,y,k,C,j,T,R,M,V,N,F,I,J=0,K=t.useViews||t.tags||t.templates||t.helpers||t.converters,O="",B={},L=e.length;for(""+t===t?(b=n?'data-link="'+t.replace(it," ").slice(1,-1)+'"':t,t=0):(b=t.tmplName||"unnamed",t.allowCode&&(B.allowCode=!0),t.debug&&(B.debug=!0),f=t.bnds,x=t.tmpls),r=0;L>r;r++)if(i=e[r],""+i===i)O+='\n+"'+i+'"';else if(a=i[0],"*"===a)O+=";\n"+i[1]+"\nret=ret";else{if(s=i[1],k=!n&&i[2],o=S(i[3],"params")+"},"+S(v=i[4]),N=i[5],I=i[6],C=i[8]&&i[8].replace(at,"$1"),(R="else"===a)?g&&g.push(i[7]):(J=0,f&&(g=i[7])&&(g=[g],J=f.push(1))),K=K||v[1]||v[2]||g||/view.(?!index)/.test(v[0]),(M=":"===a)?s&&(a=s===ht?">":s+a):(k&&(_=A(C,B),_.tmplName=b+"/"+a,_.useViews=_.useViews||K,U(k,_),K=_.useViews,x.push(_)),R||(y=a,K=K||a&&(!Vt[a]||!Vt[a].flow),T=O,O=""),j=e[r+1],j=j&&"else"===j[0]),F=N?";\ntry{\nret+=":"\n+",m="",h="",M&&(g||I||s&&s!==ht)){if(V="return {"+o+"};",w='c("'+s+'",view,',V=new Function("data,view,j,u"," // "+b+" "+J+" "+a+"\n"+V),V._er=N,m=w+J+",",h=")",V._tag=a,n)return V;E(V,g),c=!0}if(O+=M?(n?(N?"\ntry{\n":"")+"return ":F)+(c?(c=void 0,K=u=!0,w+(g?(f[J-1]=V,J):"{"+o+"}")+")"):">"===a?(p=!0,"h("+v[0]+")"):(d=!0,"((v="+(v[0]||"data")+')!=null?v:"")')):(l=!0,"\n{view:view,tmpl:"+(k?x.length:"0")+","+o+"},"),y&&!j){if(O="["+O.slice(0,-1)+"]",w='t("'+y+'",view,this,',n||g){if(O=new Function("data,view,j,u"," // "+b+" "+J+" "+y+"\nreturn "+O+";"),O._er=N,O._tag=y,g&&E(f[J-1]=O,g),n)return O;m=w+J+",undefined,",h=")"}O=T+F+w+(J||O)+")",g=0,y=0}N&&(K=!0,O+=";\n}catch(e){ret"+(n?"urn ":"+=")+m+"j._err(e,view,"+N+")"+h+";}\n"+(n?"":"ret=ret"))}O="// "+b+"\nvar v"+(l?",t=j._tag":"")+(u?",c=j._cnvt":"")+(p?",h=j.converters.html":"")+(n?";\n":',ret=""\n')+(B.debug?"debugger;":"")+O+(n?"\n":";\nreturn ret;"),Nt._dbgMode&&(O="try {\n"+O+"\n}catch(e){\nreturn j._err(e, view);\n}");try{O=new Function("data,view,j,u",O)}catch(q){$("Compiled template code:\n\n"+O+'\n: "'+q.message+'"')}return t&&(t.fn=O,t.useViews=!!K),O}function J(e,t){return e&&e!==t?t?d(d({},t),e):e:t&&d({},t)}function K(e){return mt[e]||(mt[e]="&#"+e.charCodeAt(0)+";")}function O(e){var t,n,r=[];if(typeof e===wt)for(t in e)n=e[t],n&&n.toJSON&&!n.toJSON()||jt(n)||r.push({key:t,prop:n});return r}function B(e){return void 0!=e?ut.test(e)&&(""+e).replace(ft,K)||e:""}e=e===!0;var L,q,H,D,Q,Z="v1.0.0-beta",z=(0,eval)("this"),G=z.jQuery,P=z.document,W="{",X="{",Y="}",et="}",tt="^",nt=/^(!*?)(?:null|true|false|\d[\d.]*|([\w$]+|\.|~([\w$]+)|#(view|([\w$]+))?)([\w$.^]*?)(?:[.[^]([\w$]+)\]?)?)$/g,rt=/(\()(?=\s*\()|(?:([([])\s*)?(?:(\^?)(!*?[#~]?[\w$.^]+)?\s*((\+\+|--)|\+|-|&&|\|\||===|!==|==|!=|<=|>=|[<>%*:?\/]|(=))\s*|(!*?[#~]?[\w$.^]+)([([])?)|(,\s*)|(\(?)\\?(?:(')|("))|(?:\s*(([)\]])(?=\s*[.^]|\s*$|[^\(\[])|[)\]])([([]?))|(\s+)/g,it=/[ \t]*(\r\n|\n|\r)/g,at=/\\(['"])/g,st=/['"\\]/g,ot=/(?:\x08|^)(onerror:)?(?:(~?)(([\w$_\.]+):)?([^\x08]+))\x08(,)?([^\x08]+)/gi,lt=/^if\s/,pt=/<(\w+)[>\s]/,dt=/[\x00`><"'&]/g,ut=/[\x00`><\"'&]/,ct=/^on[A-Z]|^convert(Back)?$/,ft=dt,gt=0,vt=0,mt={"&":"&amp;","<":"&lt;",">":"&gt;","\x00":"&#0;","'":"&#39;",'"':"&#34;","`":"&#96;"},ht="html",wt="object",xt="data-jsv-tmpl",bt="For #index in nested block use #getIndex().",_t={},yt={template:{compile:C},tag:{compile:y},helper:{},converter:{}},kt={jsviews:Z,settings:function(e){d(Nt,e),l(Nt._dbgMode),Nt.jsv&&Nt.jsv()},sub:{View:b,Err:p,tmplFn:N,parse:I,extend:d,syntaxErr:$,onStore:{},_ths:i,_tg:function(){}},map:j,_cnvt:m,_tag:x,_err:V},Ct=z.jsviews;(p.prototype=new Error).constructor=p,f.depends=function(){return[this.get("item"),"index"]},g.depends="index",b.prototype={get:c,getIndex:g,getRsc:w,hlp:v,_is:"view"};for(L in yt)T(L,yt[L]);var jt,At,Tt=kt.templates,Rt=kt.converters,Mt=kt.helpers,Vt=kt.tags,$t=kt.sub,Nt=kt.settings;return $t._tg.prototype={baseApply:k,cvtArgs:h},D=$t.topView=new b,G?(G.fn.render=function(e,t,n){var r=this.jquery&&(this[0]||V('Unknown template: "'+this.selector+'"')),i=r.getAttribute(xt);return R.call(i?Tt[i]:Tt(r),e,t,n)},G.observable&&(d($t,G.views.sub),kt.map=G.views.map)):(G={},e||(z.jsviews=G),G.isFunction=function(e){return"function"==typeof e},G.isArray=Array.isArray||function(e){return"[object Array]"===G.toString.call(e)},G.noConflict=function(){return z.jsviews===G&&(z.jsviews=Ct),G}),jt=G.isFunction,At=G.isArray,G.render=_t,G.views=kt,G.templates=Tt=kt.templates,kt.compile=function(e,t){return t=t||{},t.markup=e,Tt(t)},Nt({debugMode:l,delimiters:u,onError:function(e,t,n){return t&&(e=void 0===n?"{Error: "+(e.message||e)+"}":jt(n)?n(e,t):n),void 0==e?"":e},_dbgMode:!1}),Vt({"if":{render:function(e){var t=this,n=t.tagCtx,r=t.rendering.done||!e&&(arguments.length||!n.index)?"":(t.rendering.done=!0,t.selected=n.index,n.render(n.view,!0));return r},flow:!0},"for":{render:function(e){var t,n=!arguments.length,r=this,i=r.tagCtx,a="",s=0;return r.rendering.done||(t=n?i.view.data:e,void 0!==t&&(a+=i.render(t,n),s+=At(t)?t.length:1),(r.rendering.done=s)&&(r.selected=i.index)),a},flow:!0},props:{baseTag:"for",dataMap:j(O),flow:!0},include:{flow:!0},"*":{render:a,flow:!0},":*":{render:a,flow:!0},dbg:Mt.dbg=Rt.dbg=o}),Rt({html:B,attr:B,url:function(e){return void 0!=e?encodeURI(""+e):null===e?e:""}}),u(),kt});
//# sourceMappingURL=jsrender.min.js.map;
require.config({
  "baseUrl": "js/lib/",
  "paths": {
    "app": "../app",
    "EventEmitter": "eventEmitter/EventEmitter.min",
    "jquery": "jquery/dist/jquery",
    "jqueryui": "jquery-ui/ui/minified/jquery-ui.custom.min",
    "jsrender": "jsrender/jsrender.min"
  },
  "shim": {
    "jsrender": {
      "deps": ["jquery"],
      "exports": "jQuery.fn.template"
    },
    "jqueryui": {
      "deps": ["jquery"]
    }
  }
});

define('app',["app/simplelayout/Simplelayout", "app/toolbox/Toolbox", "app/simplelayout/EventEmitter", "jsrender"], function(Simplelayout, Toolbox) {

  "use strict";

  return {
    simplelayout: Simplelayout,
    toolbox: Toolbox
  };
});

  // Ask almond to synchronously require the
  // module value for 'app' here and return it as the
  // value to use for the public API for the built file.
  return require("app");
}));

