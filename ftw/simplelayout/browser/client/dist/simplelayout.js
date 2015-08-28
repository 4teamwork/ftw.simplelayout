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

    var components = {};
    if (!$.isEmptyObject(options.components)) {
      components = $.map(options.components.addable_blocks, function(component) { return component; }).sort(function(a, b) {
        return normalizeCompare(a.title, b.title);
      });
    }
    var data = {
      "components": components,
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

      var layoutToolbar = new Toolbar(options.toolbox.options.components.layout_actions.actions, "vertical", "layout");
      layout.attachToolbar(layoutToolbar);
    });

    on("blockInserted", function(block) {
      var blockToolbar = new Toolbar(options.toolbox.options.components.addable_blocks[block.type].actions, "horizontal", "block");
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

/*! JsRender v1.0.0-rc.65 (Beta - Release Candidate): http://jsviews.com/#jsrender */
/*! **VERSION FOR WEB** (For NODE.JS see http://jsviews.com/download/jsrender-node.js) */
!function(e){var t=(0,eval)("this"),n=t.jQuery;"function"==typeof define&&define.amd?define('jsrender',e):"object"==typeof exports?module.exports=n?e(n):function(t){if(t&&!t.fn)throw"Provide jQuery or null";return e(t)}:e(!1)}(function(e){"use strict";function t(e,t){return function(){var n,r=this,i=r.base;return r.base=e,n=t.apply(r,arguments),r.base=i,n}}function n(e,n){return z(n)&&(n=t(e?e._d?e:t(a,e):a,n),n._d=1),n}function r(e,t){for(var r in t.props)xe.test(r)&&(e[r]=n(e[r],t.props[r]))}function i(e){return e}function a(){return""}function o(e){try{throw"dbg breakpoint"}catch(t){}return this.base?this.baseApply(arguments):e}function s(e){ne._dbgMode=e!==!1}function d(t){this.name=(e.link?"JsViews":"JsRender")+" Error",this.message=t||this.name}function p(e,t){var n;for(n in t)e[n]=t[n];return e}function l(e,t,n){return(0!==this||e)&&(ae=e?e.charAt(0):ae,oe=e?e.charAt(1):oe,se=t?t.charAt(0):se,de=t?t.charAt(1):de,pe=n||pe,e="\\"+ae+"(\\"+pe+")?\\"+oe,t="\\"+se+"\\"+de,H="(?:(?:(\\w+(?=[\\/\\s\\"+se+"]))|(?:(\\w+)?(:)|(>)|!--((?:[^-]|-(?!-))*)--|(\\*)))\\s*((?:[^\\"+se+"]|\\"+se+"(?!\\"+de+"))*?)",te.rTag=H+")",H=new RegExp(e+H+"(\\/)?|(?:\\/(\\w+)))"+t,"g"),D=new RegExp("<.*>|([^\\\\]|^)[{}]|"+e+".*"+t)),[ae,oe,se,de,pe]}function u(e,t){t||(t=e,e=void 0);var n,r,i,a,o=this,s=!t||"root"===t;if(e){if(a=o.type===t?o:void 0,!a)if(n=o.views,o._.useKey){for(r in n)if(a=n[r].get(e,t))break}else for(r=0,i=n.length;!a&&i>r;r++)a=n[r].get(e,t)}else if(s)for(;o.parent.parent;)a=o=o.parent;else for(;o&&!a;)a=o.type===t?o:void 0,o=o.parent;return a}function c(){var e=this.get("item");return e?e.index:void 0}function f(){return this.index}function g(e){var t,n=this,r=n.linkCtx,i=(n.ctx||{})[e];return void 0===i&&r&&r.ctx&&(i=r.ctx[e]),void 0===i&&(i=Y[e]),i&&z(i)&&!i._wrp&&(t=function(){return i.apply(this&&this!==B?this:n,arguments)},t._wrp=!0,p(t,i)),t||i}function v(e,t,n,i){var a,o,s="number"==typeof n&&t.tmpl.bnds[n-1],d=t.linkCtx;return void 0!==i?n=i={props:{},args:[i]}:s&&(n=s(t.data,t,Z)),o=n.args[0],(e||s)&&(a=d&&d.tag,a||(a=p(new te._tg,{_:{inline:!d,bnd:s,unlinked:!0},tagName:":",cvt:e,flow:!0,tagCtx:n}),d&&(d.tag=a,a.linkCtx=d),n.ctx=J(n.ctx,(d?d.view:t).ctx)),a._er=i&&o,r(a,n),n.view=t,a.ctx=n.ctx||{},n.ctx=void 0,t._.tag=a,o=a.cvtArgs(a.convert||"true"!==e&&e)[0],o=s&&t._.onRender?t._.onRender(o,t,s):o,t._.tag=void 0),void 0!=o?o:""}function m(e){var t=this,n=t.tagCtx,r=n.view,i=n.args;return e=t.convert||e,e=e&&(""+e===e?r.getRsc("converters",e)||V("Unknown converter: '"+e+"'"):e),i=i.length||n.index?e?i.slice():i:[r.data],e&&(e.depends&&(t.depends=te.getDeps(t.depends,t,e.depends,e)),i[0]=e.apply(t,i)),i}function h(e,t){for(var n,r,i=this;void 0===n&&i;)r=i.tmpl&&i.tmpl[e],n=r&&r[t],i=i.parent;return n||Z[e][t]}function w(e,t,n,i,a,o){t=t||P;var s,d,p,l,u,c,f,g,v,m,h,w,b,x,_,y,k,j,C,A="",R=t.linkCtx||0,M=t.ctx,$=n||t.tmpl,N="number"==typeof i&&t.tmpl.bnds[i-1];for("tag"===e._is?(s=e,e=s.tagName,i=s.tagCtxs,p=s.template):(d=t.getRsc("tags",e)||V("Unknown tag: {{"+e+"}} "),p=d.template),void 0!==o?(A+=o,i=o=[{props:{},args:[]}]):N&&(i=N(t.data,t,Z)),g=i.length,f=0;g>f;f++)m=i[f],(!R||!R.tag||f&&!R.tag._.inline||s._er)&&((w=m.tmpl)&&(w=m.content=$.tmpls[w-1]),m.index=f,m.tmpl=p||w,m.render=T,m.view=t,m.ctx=J(m.ctx,M)),(n=m.props.tmpl)&&(n=""+n===n?t.getRsc("templates",n)||W(n):n,m.tmpl=n),s||(s=new d._ctr,b=!!s.init,s.parent=c=M&&M.tag,s.tagCtxs=i,C=s.dataMap,R&&(s._.inline=!1,R.tag=s,s.linkCtx=R),(s._.bnd=N||R.fn)?s._.arrVws={}:s.dataBoundOnly&&V("{^{"+e+"}} tag must be data-bound")),i=s.tagCtxs,C=s.dataMap,m.tag=s,C&&i&&(m.map=i[f].map),s.flow||(h=m.ctx=m.ctx||{},l=s.parents=h.parentTags=M&&J(h.parentTags,M.parentTags)||{},c&&(l[c.tagName]=c),l[s.tagName]=h.tag=s);if((N||R)&&(t._.tag=s),!(s._er=o)){for(r(s,i[0]),s.rendering={},f=0;g>f;f++)m=s.tagCtx=i[f],k=m.props,y=s.cvtArgs(),(x=k.dataMap||C)&&(y.length||k.dataMap)&&(_=m.map,(!_||_.src!==y[0]||a)&&(_&&_.src&&_.unmap(),_=m.map=x.map(y[0],k,void 0,!s._.bnd)),y=[_.tgt]),s.ctx=m.ctx,f||(b&&(j=s.template,s.init(m,R,s.ctx),b=void 0,s.template!==j&&(s._.tmpl=s.template)),R&&(R.attr=s.attr=R.attr||s.attr),u=s.attr,s._.noVws=u&&u!==je),v=void 0,s.render&&(v=s.render.apply(s,y)),y.length||(y=[t]),void 0===v&&(v=m.render(y.length?y[0]:t,!0)||(a?void 0:"")),A=A?A+(v||""):v;s.rendering=void 0}return s.tagCtx=i[0],s.ctx=s.tagCtx.ctx,s._.noVws&&s._.inline&&(A="text"===u?X.html(A):""),N&&t._.onRender?t._.onRender(A,t,N):A}function b(e,t,n,r,i,a,o,s){var d,p,l,u,f=this,g="array"===t;f.content=o,f.views=g?[]:{},f.parent=n,f.type=t||"top",f.data=r,f.tmpl=i,u=f._={key:0,useKey:g?0:1,id:""+ye++,onRender:s,bnds:{}},f.linked=!!s,n?(d=n.views,p=n._,p.useKey?(d[u.key="_"+p.useKey++]=f,f.index=Re,f.getIndex=c,l=p.tag,u.bnd=g&&(!l||!!l._.bnd&&l)):d.length===(u.key=f.index=a)?d.push(f):d.splice(a,0,f),f.ctx=e||n.ctx):f.ctx=e}function x(e){var t,n,r,i,a,o,s;for(t in Me)if(a=Me[t],(o=a.compile)&&(n=e[t+"s"]))for(r in n)i=n[r]=o(r,n[r],e,0),i._is=t,i&&(s=te.onStore[t])&&s(r,i,o)}function _(e,t,r){function i(){var t=this;t._={inline:!0,unlinked:!0},t.tagName=e}var a,o,s,d=new te._tg;if(z(t)?t={depends:t.depends,render:t}:""+t===t&&(t={template:t}),o=t.baseTag){t.flow=!!t.flow,t.baseTag=o=""+o===o?r&&r.tags[o]||ee[o]:o,d=p(d,o);for(s in t)d[s]=n(o[s],t[s])}else d=p(d,t);return void 0!==(a=d.template)&&(d.template=""+a===a?W[a]||W(a):a),d.init!==!1&&((i.prototype=d).constructor=d._ctr=i),r&&(d._parentTmpl=r),d}function y(e){return this.base.apply(this,e)}function k(t,n,r,i){function a(n){var a,s;if(""+n===n||n.nodeType>0&&(o=n)){if(!o)if(/^\.\/[^\\:*?"<>]*$/.test(n))(s=W[t=t||n])?n=s:o=document.getElementById(n);else if(e.fn&&!D.test(n))try{o=e(document).find(n)[0]}catch(d){}o&&(i?n=o.innerHTML:(a=o.getAttribute(Ae),a?a!==Te?(n=W[a],delete W[a]):e.fn&&(n=e.data(o)[Te]):(t=t||(e.fn?Te:n),n=k(t,o.innerHTML,r,i)),n.tmplName=t=t||a,t!==Te&&(W[t]=n),o.setAttribute(Ae,t),e.fn&&e.data(o,Te,n))),o=void 0}else n.fn||(n=void 0);return n}var o,s,d=n=n||"";return 0===i&&(i=void 0,d=a(d)),i=i||(n.markup?n:{}),i.tmplName=t,r&&(i._parentTmpl=r),!d&&n.markup&&(d=a(n.markup))&&d.fn&&(d=d.markup),void 0!==d?(d.fn||n.fn?d.fn&&(s=d):(n=C(d,i),$(d.replace(ge,"\\$&"),n)),s||(x(i),s=p(function(){return n.render.apply(n,arguments)},n)),t&&!r&&t!==Te&&(Ve[t]=s),s):void 0}function j(e){function t(t,n){this.tgt=e.getTgt(t,n)}return z(e)&&(e={getTgt:e}),e.baseMap&&(e=p(p({},e.baseMap),e)),e.map=function(e,n){return new t(e,n)},e}function C(t,n){var r,i=ne.wrapMap||{},a=p({tmpls:[],links:{},bnds:[],_is:"template",render:T},n);return a.markup=t,n.htmlTag||(r=he.exec(t),a.htmlTag=r?r[1].toLowerCase():""),r=i[a.htmlTag],r&&r!==i.div&&(a.markup=e.trim(a.markup)),a}function A(e,t){function n(i,a,o){var s,d,p,l;if(i&&typeof i===Ce&&!i.nodeType&&!i.markup&&!i.getTgt){for(p in i)n(p,i[p],a);return Z}return void 0===a&&(a=i,i=void 0),i&&""+i!==i&&(o=a,a=i,i=void 0),l=o?o[r]=o[r]||{}:n,d=t.compile,null===a?i&&delete l[i]:(a=d?d(i,a,o,0):a,i&&(l[i]=a)),d&&a&&(a._is=e),a&&(s=te.onStore[e])&&s(i,a,d),a}var r=e+"s";Z[r]=n}function T(e,t,n,r,i,a){var o,s,d,p,l,u,c,f,g=r,v="";if(t===!0?(n=t,t=void 0):typeof t!==Ce&&(t=void 0),(d=this.tag)?(l=this,p=d._.tmpl||l.tmpl,g=g||l.view,arguments.length||(e=g)):p=this,p){if(!g&&e&&"view"===e._is&&(g=e),g&&e===g&&(e=g.data),p.fn||(p=d._.tmpl=W[p]||W(p)),u=!g,re=re||u,g||((t=t||{}).root=e),!re||ne.useViews||p.useViews||g&&g!==P)v=R(p,e,t,n,g,i,a,d);else{if(g?(c=g.data,f=g.index,g.index=Re):(g=P,g.data=e,g.ctx=t),G(e)&&!n)for(o=0,s=e.length;s>o;o++)g.index=o,g.data=e[o],v+=p.fn(e[o],g,Z);else v+=p.fn(e,g,Z);g.data=c,g.index=f}u&&(re=void 0)}return v}function R(e,t,n,r,i,a,o,s){function d(e){_=p({},n),_[x]=e}var l,u,c,f,g,v,m,h,w,x,_,y,k="";if(s&&(w=s.tagName,y=s.tagCtx,n=n?J(n,s.ctx):s.ctx,m=y.content,y.props.link===!1&&(n=n||{},n.link=!1),(x=y.props.itemVar)&&("~"!==x.charAt(0)&&M("Use itemVar='~myItem'"),x=x.slice(1))),i&&(m=m||i.content,o=o||i._.onRender,n=n||i.ctx),a===!0&&(v=!0,a=0),o&&(n&&n.link===!1||s&&s._.noVws)&&(o=void 0),h=o,o===!0&&(h=void 0,o=i._.onRender),n=e.helpers?J(e.helpers,n):n,_=n,G(t)&&!r)for(c=v?i:void 0!==a&&i||new b(n,"array",i,t,e,a,m,o),x&&(c.it=x),x=c.it,l=0,u=t.length;u>l;l++)x&&d(t[l]),f=new b(_,"item",c,t[l],e,(a||0)+l,m,o),g=e.fn(t[l],f,Z),k+=c._.onRender?c._.onRender(g,f):g;else x&&d(t),c=v?i:new b(_,w||"data",i,t,e,a,m,o),s&&!s.flow&&(c.tag=s),k+=e.fn(t,c,Z);return h?h(k,c):k}function V(e,t,n){var r=ne.onError(e,t,n);if(""+e===e)throw new te.Err(r);return!t.linkCtx&&t.linked?X.html(r):r}function M(e){V("Syntax error\n"+e)}function $(e,t,n,r,i){function a(t){t-=f,t&&v.push(e.substr(f,t).replace(ce,"\\n"))}function o(t,n){t&&(t+="}}",M((n?"{{"+n+"}} block has {{/"+t+" without {{"+t:"Unmatched or missing {{/"+t)+", in template:\n"+e))}function s(s,d,c,h,w,b,x,_,y,k,j,C){b&&(w=":",h=je),k=k||n&&!i;var A=(d||n)&&[[]],T="",R="",V="",$="",N="",F="",I="",J="",U=!k&&!w&&!x;c=c||(y=y||"#data",w),a(C),f=C+s.length,_?u&&v.push(["*","\n"+y.replace(/^:/,"ret+= ").replace(fe,"$1")+";\n"]):c?("else"===c&&(me.test(y)&&M('for "{{else if expr}}" use "{{else expr}}"'),A=m[7]&&[[]],m[8]=e.substring(m[8],C),m=g.pop(),v=m[2],U=!0),y&&S(y.replace(ce," "),A,t).replace(ve,function(e,t,n,r,i,a,o,s){return r="'"+i+"':",o?(R+=a+",",$+="'"+s+"',"):n?(V+=r+a+",",F+=r+"'"+s+"',"):t?I+=a:("trigger"===i&&(J+=a),T+=r+a+",",N+=r+"'"+s+"',",l=l||xe.test(i)),""}).slice(0,-1),A&&A[0]&&A.pop(),p=[c,h||!!r||l||"",U&&[],E($,N,F),E(R,T,V),I,J,A||0],v.push(p),U&&(g.push(m),m=p,m[8]=f)):j&&(o(j!==m[0]&&"else"!==m[0]&&j,m[0]),m[8]=e.substring(m[8],C),m=g.pop()),o(!m&&j),v=m[2]}var d,p,l,u=ne.allowCode||t&&t.allowCode,c=[],f=0,g=[],v=c,m=[,,c];return u&&(t.allowCode=u),n&&(e=ae+e+de),o(g[0]&&g[0][2].pop()[0]),e.replace(H,s),a(e.length),(f=c[c.length-1])&&o(""+f!==f&&+f[8]===f[8]&&f[0]),n?(d=I(c,e,n),N(d,[c[0][7]])):d=I(c,t),d}function N(e,t){var n,r,i=0,a=t.length;for(e.deps=[];a>i;i++){r=t[i];for(n in r)"_jsvto"!==n&&r[n].length&&(e.deps=e.deps.concat(r[n]))}e.paths=r}function E(e,t,n){return[e.slice(0,-1),t.slice(0,-1),n.slice(0,-1)]}function F(e,t){return"\n	"+(t?t+":{":"")+"args:["+e[0]+"]"+(e[1]||!t?",\n	props:{"+e[1]+"}":"")+(e[2]?",\n	ctx:{"+e[2]+"}":"")}function S(e,t,n){function r(r,h,w,b,x,_,y,k,j,C,A,T,R,V,N,E,F,S,I,J){function U(e,n,r,o,s,d,u,c){var f="."===r;if(r&&(x=x.slice(n.length),f||(e=(o?'view.hlp("'+o+'")':s?"view":"data")+(c?(d?"."+d:o?"":s?"":"."+r)+(u||""):(c=o?"":s?d||"":r,"")),e+=c?"."+c:"",e=n+("view.data"===e.slice(0,9)?e.slice(5):e)),p)){if(q="linkTo"===i?a=t._jsvto=t._jsvto||[]:l.bd,B=f&&q[q.length-1]){if(B._jsv){for(;B.sb;)B=B.sb;B.bnd&&(x="^"+x.slice(1)),B.sb=x,B.bnd=B.bnd||"^"===x.charAt(0)}}else q.push(x);m[g]=I+(f?1:0)}return e}b=p&&b,b&&!k&&(x=b+x),_=_||"",w=w||h||T,x=x||j,C=C||F||"";var K,O,q,B,L;if(!y||d||s){if(p&&E&&!d&&!s&&(!i||o||a)&&(K=m[g-1],J.length-1>I-(K||0))){if(K=J.slice(K,I+r.length),O!==!0)if(q=a||u[g-1].bd,B=q[q.length-1],B&&B.prm){for(;B.sb&&B.sb.prm;)B=B.sb;L=B.sb={path:B.sb,bnd:B.bnd}}else q.push(L={path:q.pop()});E=oe+":"+K+" onerror=''"+se,O=f[E],O||(f[E]=!0,f[E]=O=$(E,n,!0)),O!==!0&&L&&(L._jsv=O,L.prm=l.bd,L.bnd=L.bnd||L.path&&L.path.indexOf("^")>=0)}return d?(d=!R,d?r:T+'"'):s?(s=!V,s?r:T+'"'):(w?(m[g]=I++,l=u[++g]={bd:[]},w):"")+(S?g?"":(c=J.slice(c,I),(i?(i=o=a=!1,"\b"):"\b,")+c+(c=I+r.length,p&&t.push(l.bd=[]),"\b")):k?(g&&M(e),p&&t.pop(),i=x,o=b,c=I+r.length,b&&(p=l.bd=t[i]=[]),x+":"):x?x.split("^").join(".").replace(le,U)+(C?(l=u[++g]={bd:[]},v[g]=!0,C):_):_?_:N?(v[g]=!1,l=u[--g],N+(C?(l=u[++g],v[g]=!0,C):"")):A?(v[g]||M(e),","):h?"":(d=R,s=V,'"'))}M(e)}var i,a,o,s,d,p=t&&t[0],l={bd:p},u={0:l},c=0,f=n?n.links:p&&(p.links=p.links||{}),g=0,v={},m={};return(e+(n?" ":"")).replace(ue,r)}function I(e,t,n){var r,i,a,o,s,d,p,l,u,c,f,g,v,m,h,w,b,x,_,y,k,j,A,T,R,V,$,E,S,J,U=0,K=ne.useViews||t.useViews||t.tags||t.templates||t.helpers||t.converters,O="",q={},B=e.length;for(""+t===t?(x=n?'data-link="'+t.replace(ce," ").slice(1,-1)+'"':t,t=0):(x=t.tmplName||"unnamed",t.allowCode&&(q.allowCode=!0),t.debug&&(q.debug=!0),f=t.bnds,b=t.tmpls),r=0;B>r;r++)if(i=e[r],""+i===i)O+='\n+"'+i+'"';else if(a=i[0],"*"===a)O+=";\n"+i[1]+"\nret=ret";else{if(o=i[1],k=!n&&i[2],s=F(i[3],"params")+"},"+F(v=i[4]),E=i[5],J=i[6],j=i[8]&&i[8].replace(fe,"$1"),(R="else"===a)?g&&g.push(i[7]):(U=0,f&&(g=i[7])&&(g=[g],U=f.push(1))),K=K||v[1]||v[2]||g||/view.(?!index)/.test(v[0]),(V=":"===a)?o&&(a=o===je?">":o+a):(k&&(_=C(j,q),_.tmplName=x+"/"+a,_.useViews=_.useViews||K,I(k,_),K=_.useViews,b.push(_)),R||(y=a,K=K||a&&(!ee[a]||!ee[a].flow),T=O,O=""),A=e[r+1],A=A&&"else"===A[0]),S=E?";\ntry{\nret+=":"\n+",m="",h="",V&&(g||J||o&&o!==je)){if($="return {"+s+"};",w='c("'+o+'",view,',$=new Function("data,view,j,u"," // "+x+" "+U+" "+a+"\n"+$),$._er=E,m=w+U+",",h=")",$._tag=a,n)return $;N($,g),c=!0}if(O+=V?(n?(E?"\ntry{\n":"")+"return ":S)+(c?(c=void 0,K=u=!0,w+(g?(f[U-1]=$,U):"{"+s+"}")+")"):">"===a?(p=!0,"h("+v[0]+")"):(l=!0,"((v="+(v[0]||"data")+')!=null?v:"")')):(d=!0,"\n{view:view,tmpl:"+(k?b.length:"0")+","+s+"},"),y&&!A){if(O="["+O.slice(0,-1)+"]",w='t("'+y+'",view,this,',n||g){if(O=new Function("data,view,j,u"," // "+x+" "+U+" "+y+"\nreturn "+O+";"),O._er=E,O._tag=y,g&&N(f[U-1]=O,g),n)return O;m=w+U+",undefined,",h=")"}O=T+S+w+(U||O)+")",g=0,y=0}E&&(K=!0,O+=";\n}catch(e){ret"+(n?"urn ":"+=")+m+"j._err(e,view,"+E+")"+h+";}\n"+(n?"":"ret=ret"))}O="// "+x+"\nvar v"+(d?",t=j._tag":"")+(u?",c=j._cnvt":"")+(p?",h=j.converters.html":"")+(n?";\n":',ret=""\n')+(q.debug?"debugger;":"")+O+(n?"\n":";\nreturn ret;"),ne._dbgMode&&(O="try {\n"+O+"\n}catch(e){\nreturn j._err(e, view);\n}");try{O=new Function("data,view,j,u",O)}catch(L){M("Compiled template code:\n\n"+O+'\n: "'+L.message+'"')}return t&&(t.fn=O,t.useViews=!!K),O}function J(e,t){return e&&e!==t?t?p(p({},t),e):e:t&&p({},t)}function U(e){return ke[e]||(ke[e]="&#"+e.charCodeAt(0)+";")}function K(e){var t,n,r=[];if(typeof e===Ce)for(t in e)n=e[t],n&&n.toJSON&&!n.toJSON()||z(n)||r.push({key:t,prop:n});return r}function O(t,n,r){var i=this.jquery&&(this[0]||V('Unknown template: "'+this.selector+'"')),a=i.getAttribute(Ae);return T.call(a?e.data(i)[Te]:W(i),t,n,r)}function q(e){return void 0!=e?be.test(e)&&(""+e).replace(_e,U)||e:""}var B=(0,eval)("this"),L=e===!1;e=e&&e.fn?e:B.jQuery;var Q,H,D,P,Z,z,G,W,X,Y,ee,te,ne,re,ie="v1.0.0-beta",ae="{",oe="{",se="}",de="}",pe="^",le=/^(!*?)(?:null|true|false|\d[\d.]*|([\w$]+|\.|~([\w$]+)|#(view|([\w$]+))?)([\w$.^]*?)(?:[.[^]([\w$]+)\]?)?)$/g,ue=/(\()(?=\s*\()|(?:([([])\s*)?(?:(\^?)(!*?[#~]?[\w$.^]+)?\s*((\+\+|--)|\+|-|&&|\|\||===|!==|==|!=|<=|>=|[<>%*:?\/]|(=))\s*|(!*?[#~]?[\w$.^]+)([([])?)|(,\s*)|(\(?)\\?(?:(')|("))|(?:\s*(([)\]])(?=\s*[.^]|\s*$|[^\(\[])|[)\]])([([]?))|(\s+)/g,ce=/[ \t]*(\r\n|\n|\r)/g,fe=/\\(['"])/g,ge=/['"\\]/g,ve=/(?:\x08|^)(onerror:)?(?:(~?)(([\w$_\.]+):)?([^\x08]+))\x08(,)?([^\x08]+)/gi,me=/^if\s/,he=/<(\w+)[>\s]/,we=/[\x00`><"'&]/g,be=/[\x00`><\"'&]/,xe=/^on[A-Z]|^convert(Back)?$/,_e=we,ye=0,ke={"&":"&amp;","<":"&lt;",">":"&gt;","\x00":"&#0;","'":"&#39;",'"':"&#34;","`":"&#96;"},je="html",Ce="object",Ae="data-jsv-tmpl",Te="jsvTmpl",Re="For #index in nested block use #getIndex().",Ve={},Me={template:{compile:k},tag:{compile:_},helper:{},converter:{}},$e=B.jsrender,Ne=$e&&e&&!e.render;if(Z={jsviews:ie,settings:function(e){p(ne,e),s(ne._dbgMode),ne.jsv&&ne.jsv()},sub:{View:b,Err:d,tmplFn:$,parse:S,extend:p,syntaxErr:M,onStore:{},_ths:r,_tg:function(){}},map:j,_cnvt:v,_tag:w,_err:V},(d.prototype=new Error).constructor=d,c.depends=function(){return[this.get("item"),"index"]},f.depends="index",b.prototype={get:u,getIndex:f,getRsc:h,hlp:g,_is:"view"},!($e||e&&e.render)){for(Q in Me)A(Q,Me[Q]);W=Z.templates,X=Z.converters,Y=Z.helpers,ee=Z.tags,te=Z.sub,ne=Z.settings,te._tg.prototype={baseApply:y,cvtArgs:m},P=te.topView=new b,e?(e.fn.render=O,e.observable&&(p(te,e.views.sub),Z.map=e.views.map)):(e={},L&&(B.jsrender=e),e.renderFile=e.__express=e.compile=function(){throw"Node.js: use npm jsrender, or jsrender-node.js"},e.isFunction=function(e){return"function"==typeof e},e.isArray=Array.isArray||function(e){return"[object Array]"==={}.toString.call(e)},e.toJq=function(t){e!==t&&(p(t,this),e=t,e.fn.render=O)},e.jsrender=ie),z=e.isFunction,G=e.isArray,e.render=Ve,e.views=Z,e.templates=W=Z.templates,Z.compile=function(e,t){return t=t||{},t.markup=e,W(t)},ne({debugMode:s,delimiters:l,onError:function(e,t,n){return t&&(e=void 0===n?"{Error: "+(e.message||e)+"}":z(n)?n(e,t):n),void 0==e?"":e},_dbgMode:!1}),ee({"if":{render:function(e){var t=this,n=t.tagCtx,r=t.rendering.done||!e&&(arguments.length||!n.index)?"":(t.rendering.done=!0,t.selected=n.index,n.render(n.view,!0));return r},flow:!0},"for":{render:function(e){var t,n=!arguments.length,r=this,i=r.tagCtx,a="",o=0;return r.rendering.done||(t=n?i.view.data:e,void 0!==t&&(a+=i.render(t,n),o+=G(t)?t.length:1),(r.rendering.done=o)&&(r.selected=i.index)),a},flow:!0},props:{baseTag:"for",dataMap:j(K),flow:!0},include:{flow:!0},"*":{render:i,flow:!0},":*":{render:i,flow:!0},dbg:Y.dbg=X.dbg=o}),X({html:q,attr:q,url:function(e){return void 0!=e?encodeURI(""+e):null===e?e:""}}),l()}return Ne&&$e.toJq(e),e||$e});
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

