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

define('app/simplelayout/transactional',["app/simplelayout/EventEmitter"], function(EventEmitter) {

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

define('app/simplelayout/idHelper',[], function() {

  "use strict";

  return {
    createGUID: function() {
      return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function(c) {
          var r = Math.random() * 16 | 0;
          var v = c === "x" ? r : (r & 0x3 | 0x8);
          return v.toString(16);
      });
    }
  };

});

/*! JsRender v0.9.80 (Beta): http://jsviews.com/#jsrender */
/*! **VERSION FOR WEB** (For NODE.JS see http://jsviews.com/download/jsrender-node.js) */
!function(e,t){var n=t.jQuery;"object"==typeof exports?module.exports=n?e(t,n):function(n){if(n&&!n.fn)throw"Provide jQuery or null";return e(t,n)}:"function"==typeof define&&define.amd?define('jsrender',[],function(){return e(t)}):e(t,!1)}(function(e,t){"use strict";function n(e,t){return function(){var n,r=this,i=r.base;return r.base=e,n=t.apply(r,arguments),r.base=i,n}}function r(e,t){return ee(t)&&(t=n(e?e._d?e:n(s,e):s,t),t._d=1),t}function i(e,t){for(var n in t.props)Ve.test(n)&&(e[n]=r(e[n],t.props[n]))}function o(e){return e}function s(){return""}function a(e){try{throw console.log("JsRender dbg breakpoint: "+e),"dbg breakpoint"}catch(t){}return this.base?this.baseApply(arguments):e}function d(e){this.name=(t.link?"JsViews":"JsRender")+" Error",this.message=e||this.name}function u(e,t){for(var n in t)e[n]=t[n];return e}function l(e,t,n){return e?te(e)?l.apply(X,e):(ae.delimiters=[e,t,ge=n?n.charAt(0):ge],le=e.charAt(0),pe=e.charAt(1),ce=t.charAt(0),fe=t.charAt(1),e="\\"+le+"(\\"+ge+")?\\"+pe,t="\\"+ce+"\\"+fe,G="(?:(\\w+(?=[\\/\\s\\"+ce+"]))|(\\w+)?(:)|(>)|(\\*))\\s*((?:[^\\"+ce+"]|\\"+ce+"(?!\\"+fe+"))*?)",se.rTag="(?:"+G+")",G=new RegExp("(?:"+e+G+"(\\/)?|\\"+le+"(\\"+ge+")?\\"+pe+"(?:(?:\\/(\\w+))\\s*|!--[\\s\\S]*?--))"+t,"g"),se.rTmpl=new RegExp("<.*>|([^\\\\]|^)[{}]|"+e+".*"+t),ue):ae.delimiters}function p(e,t){t||e===!0||(t=e,e=void 0);var n,r,i,o,s=this,a=!t||"root"===t;if(e){if(o=t&&s.type===t&&s,!o)if(n=s.views,s._.useKey){for(r in n)if(o=t?n[r].get(e,t):n[r])break}else for(r=0,i=n.length;!o&&i>r;r++)o=t?n[r].get(e,t):n[r]}else if(a)for(;s.parent;)o=s,s=s.parent;else for(;s&&!o;)o=s.type===t?s:void 0,s=s.parent;return o}function c(){var e=this.get("item");return e?e.index:void 0}function f(){return this.index}function g(t,n){var r,i,o=this,s=o.ctx;if(s&&(s=s[t]),void 0===s&&(s=ie[t]),s&&s._cp){if(n)return i=se._ceo(s[1].deps),i.unshift(s[0].data),i._cp=!0,i;s=X.getCtx(s)}return s&&ee(s)&&!s._wrp&&(r=function(){return s.apply(this&&this!==e?this:o,arguments)},r._wrp=o,u(r,s)),r||s}function v(e){return e&&(e.fn?e:this.getRsc("templates",e)||ne(e))}function h(e,t,n,r){var o,s,a="number"==typeof n&&t.tmpl.bnds[n-1],d=t.linkCtx;return void 0!==r?n=r={props:{},args:[r]}:a&&(n=a(t.data,t,se)),s=n.args[0],(e||a)&&(o=d&&d.tag,o||(o=u(new se._tg,{_:{inline:!d,bnd:a,unlinked:!0},tagName:":",cvt:e,flow:!0,tagCtx:n}),d&&(d.tag=o,o.linkCtx=d),n.ctx=L(n.ctx,(d?d.view:t).ctx)),o._er=r&&s,i(o,n),n.view=t,o.ctx=n.ctx||o.ctx||{},n.ctx=void 0,s=o.cvtArgs("true"!==e&&e)[0],s=a&&t._.onRender?t._.onRender(s,t,o):s),void 0!=s?s:""}function m(e){var t=this,n=t.tagCtx,r=n.view,i=n.args;return e=e||t.convert,e=e&&(""+e===e?r.getRsc("converters",e)||S("Unknown converter: '"+e+"'"):e),i=i.length||n.index?e?i.slice():i:[r.data],e&&(e.depends&&(t.depends=se.getDeps(t.depends,t,e.depends,e)),i[0]=e.apply(t,i)),i}function w(e,t){for(var n,r,i=this;void 0===n&&i;)r=i.tmpl&&i.tmpl[e],n=r&&r[t],i=i.parent;return n||X[e][t]}function x(e,t,n,r,o,s){t=t||W;var a,d,u,l,p,c,f,g,v,h,m,w,x,_,b,y,k,j,C,T="",A=t.linkCtx||0,V=t.ctx,R=n||t.tmpl,M="number"==typeof r&&t.tmpl.bnds[r-1];for("tag"===e._is?(a=e,e=a.tagName,r=a.tagCtxs,u=a.template):(d=t.getRsc("tags",e)||S("Unknown tag: {{"+e+"}} "),u=d.template),void 0!==s?(T+=s,r=s=[{props:{},args:[]}]):M&&(r=M(t.data,t,se)),g=r.length,f=0;g>f;f++)h=r[f],(!A||!A.tag||f&&!A.tag._.inline||a._er)&&((w=R.tmpls&&h.tmpl)&&(w=h.content=R.tmpls[w-1]),h.index=f,h.tmpl=w,h.render=N,h.view=t,h.ctx=L(h.ctx,V)),(n=h.props.tmpl)&&(h.tmpl=t.getTmpl(n)),a||(a=new d._ctr,x=!!a.init,a.parent=c=V&&V.tag,a.tagCtxs=r,C=a.dataMap,A&&(a._.inline=!1,A.tag=a,a.linkCtx=A),(a._.bnd=M||A.fn)?a._.arrVws={}:a.dataBoundOnly&&S("{^{"+e+"}} tag must be data-bound")),r=a.tagCtxs,C=a.dataMap,h.tag=a,C&&r&&(h.map=r[f].map),a.flow||(m=h.ctx=h.ctx||{},l=a.parents=m.parentTags=V&&L(m.parentTags,V.parentTags)||{},c&&(l[c.tagName]=c),l[a.tagName]=m.tag=a);if(!(a._er=s)){for(i(a,r[0]),a.rendering={},f=0;g>f;f++)h=a.tagCtx=r[f],k=h.props,y=a.cvtArgs(),(_=k.dataMap||C)&&(y.length||k.dataMap)&&(b=h.map,b&&b.src===y[0]&&!o||(b&&b.src&&b.unmap(),b=h.map=_.map(y[0],k,void 0,!a._.bnd)),y=[b.tgt]),a.ctx=h.ctx,f||(x&&(j=a.template,a.init(h,A,a.ctx),x=void 0),A&&(A.attr=a.attr=A.attr||a.attr),p=a.attr,a._.noVws=p&&p!==Ne),v=void 0,a.render&&(v=a.render.apply(a,y)),y.length||(y=[t]),void 0===v&&(v=h.render(y[0],!0)||(o?void 0:"")),T=T?T+(v||""):v;a.rendering=void 0}return a.tagCtx=r[0],a.ctx=a.tagCtx.ctx,a._.noVws&&a._.inline&&(T="text"===p?re.html(T):""),M&&t._.onRender?t._.onRender(T,t,a):T}function _(e,t,n,r,i,o,s,a){var d,u,l,p=this,f="array"===t;p.content=a,p.views=f?[]:{},p.parent=n,p.type=t||"top",p.data=r,p.tmpl=i,l=p._={key:0,useKey:f?0:1,id:""+Me++,onRender:s,bnds:{}},p.linked=!!s,n?(d=n.views,u=n._,u.useKey?(d[l.key="_"+u.useKey++]=p,p.index=Ie,p.getIndex=c):d.length===(l.key=p.index=o)?d.push(p):d.splice(o,0,p),p.ctx=e||n.ctx):p.ctx=e}function b(e){var t,n,r;for(t in Ke)n=t+"s",e[n]&&(r=e[n],e[n]={},X[n](r,e))}function y(e,t,n){function i(){var t=this;t._={inline:!0,unlinked:!0},t.tagName=e}var o,s,a,d=new se._tg;if(ee(t)?t={depends:t.depends,render:t}:""+t===t&&(t={template:t}),s=t.baseTag){t.flow=!!t.flow,t.baseTag=s=""+s===s?n&&n.tags[s]||oe[s]:s,d=u(d,s);for(a in t)d[a]=r(s[a],t[a])}else d=u(d,t);return void 0!==(o=d.template)&&(d.template=""+o===o?ne[o]||ne(o):o),d.init!==!1&&((i.prototype=d).constructor=d._ctr=i),n&&(d._parentTmpl=n),d}function k(e){return this.base.apply(this,e)}function j(e,n,r,i){function o(n){var o,a;if(""+n===n||n.nodeType>0&&(s=n)){if(!s)if(/^\.\/[^\\:*?"<>]*$/.test(n))(a=ne[e=e||n])?n=a:s=document.getElementById(n);else if(t.fn&&!se.rTmpl.test(n))try{s=t(document).find(n)[0]}catch(d){}s&&(i?n=s.innerHTML:(o=s.getAttribute(Fe),o?o!==Se?(n=ne[o],delete ne[o]):t.fn&&(n=t.data(s)[Se]):(e=e||(t.fn?Se:n),n=j(e,s.innerHTML,r,i)),n.tmplName=e=e||o,e!==Se&&(ne[e]=n),s.setAttribute(Fe,e),t.fn&&t.data(s,Se,n))),s=void 0}else n.fn||(n=void 0);return n}var s,a,d=n=n||"";return 0===i&&(i=void 0,d=o(d)),i=i||(n.markup?n:{}),i.tmplName=e,r&&(i._parentTmpl=r),!d&&n.markup&&(d=o(n.markup))&&d.fn&&(d=d.markup),void 0!==d?(d.fn||n.fn?d.fn&&(a=d):(n=V(d,i),U(d.replace(ye,"\\$&"),n)),a||(a=u(function(){return a.render.apply(a,arguments)},n),b(a)),e&&!r&&e!==Se&&(Ue[e]=a),a):void 0}function C(e,n){return t.isFunction(e)?e.call(n):e}function T(e){var t,n=[],r=e.length;for(t=0;r>t;t++)n.push(e[t].unmap());return n}function A(e,n){function r(e){l.apply(this,e)}function i(){return new r(arguments)}function o(e,t){var n,r,i,o,s,a=c.length;for(n=0;a>n;n++)o=c[n],r=void 0,o+""!==o&&(r=o,o=r.getter),void 0===(s=e[o])&&r&&void 0!==(i=r.defaultVal)&&(s=C(i,e)),t(s,r&&p[r.type],o)}function s(t){t=t+""===t?JSON.parse(t):t;var n,r,i,s=t,u=[];if(te(t)){for(t=t||[],r=t.length,n=0;r>n;n++)u.push(this.map(t[n]));return u._is=e,u.unmap=d,u.merge=a,u}if(t){o(t,function(e,t){t&&(e=t.map(e)),u.push(e)}),s=this.apply(this,u);for(i in t)i===Y||_[i]||(s[i]=t[i])}return s}function a(e){e=e+""===e?JSON.parse(e):e;var t,n,r,s,a,d,u,l,p,c,f=this;if(te(f)){for(l={},c=[],r=e.length,s=f.length,t=0;r>t;t++){for(p=e[t],u=!1,n=0;s>n&&!u;n++)l[n]||(d=f[n],g&&(l[n]=u=g+""===g?p[g]&&(_[g]?d[g]():d[g])===p[g]:g(d,p)));u?(d.merge(p),c.push(d)):c.push(i.map(p))}return void(x?x(f).refresh(c,!0):f.splice.apply(f,[0,f.length].concat(c)))}o(e,function(e,t,n){t?f[n]().merge(e):f[n](e)});for(a in e)a===Y||_[a]||(f[a]=e[a])}function d(){var e,n,r,i,o,s,a=this;if(te(a))return T(a);for(e={},i=c.length,r=0;i>r;r++)n=c[r],o=void 0,n+""!==n&&(o=n,n=o.getter),s=a[n](),e[n]=o&&s&&p[o.type]?te(s)?T(s):s.unmap():s;for(n in a)"_is"===n||_[n]||n===Y||"_"===n.charAt(0)&&_[n.slice(1)]||t.isFunction(a[n])||(e[n]=a[n]);return e}var u,l,p=this,c=n.getters,f=n.extend,g=n.id,v=t.extend({_is:e||"unnamed",unmap:d,merge:a},f),h="",m="",w=c?c.length:0,x=t.observable,_={};for(r.prototype=v,u=0;w>u;u++)!function(e){e=e.getter||e,_[e]=u+1;var t="_"+e;h+=(h?",":"")+e,m+="this."+t+" = "+e+";\n",v[e]=v[e]||function(n){return arguments.length?void(x?x(this).setProperty(e,n):this[t]=n):this[t]},x&&(v[e].set=v[e].set||function(e){this[t]=e})}(c[u]);return l=new Function(h,m.slice(0,-1)),l.prototype=v,v.constructor=l,i.map=s,i.getters=c,i.extend=f,i.id=g,i}function V(e,n){var r,i=de._wm||{},o=u({tmpls:[],links:{},bnds:[],_is:"template",render:N},n);return o.markup=e,n.htmlTag||(r=Ce.exec(e),o.htmlTag=r?r[1].toLowerCase():""),r=i[o.htmlTag],r&&r!==i.div&&(o.markup=t.trim(o.markup)),o}function R(e,t){function n(i,o,s){var a,d,u,l;if(i&&typeof i===Ee&&!i.nodeType&&!i.markup&&!i.getTgt&&!("viewModel"===e&&i.getters||i.extend)){for(u in i)n(u,i[u],o);return o||X}return void 0===o&&(o=i,i=void 0),i&&""+i!==i&&(s=o,o=i,i=void 0),l=s?"viewModel"===e?s:s[r]=s[r]||{}:n,d=t.compile,null===o?i&&delete l[i]:(o=d?d.call(l,i,o,s,0):o,i&&(l[i]=o)),d&&o&&(o._is=e),o&&(a=se.onStore[e])&&a(i,o,d),o}var r=e+"s";X[r]=n}function M(e){ue[e]=function(t){return arguments.length?(ae[e]=t,ue):ae[e]}}function $(e){function t(t,n){this.tgt=e.getTgt(t,n)}return ee(e)&&(e={getTgt:e}),e.baseMap&&(e=u(u({},e.baseMap),e)),e.map=function(e,n){return new t(e,n)},e}function N(e,t,n,r,i,o){var s,a,d,u,l,p,c,f,g=r,v="";if(t===!0?(n=t,t=void 0):typeof t!==Ee&&(t=void 0),(d=this.tag)?(l=this,g=g||l.view,u=g.getTmpl(d.template||l.tmpl),arguments.length||(e=g)):u=this,u){if(!g&&e&&"view"===e._is&&(g=e),g&&e===g&&(e=g.data),p=!g,he=he||p,g||((t=t||{}).root=e),!he||de.useViews||u.useViews||g&&g!==W)v=E(u,e,t,n,g,i,o,d);else{if(g?(c=g.data,f=g.index,g.index=Ie):(g=W,g.data=e,g.ctx=t),te(e)&&!n)for(s=0,a=e.length;a>s;s++)g.index=s,g.data=e[s],v+=u.fn(e[s],g,se);else g.data=e,v+=u.fn(e,g,se);g.data=c,g.index=f}p&&(he=void 0)}return v}function E(e,t,n,r,i,o,s,a){function d(e){b=u({},n),b[x]=e}var l,p,c,f,g,v,h,m,w,x,b,y,k="";if(a&&(w=a.tagName,y=a.tagCtx,n=n?L(n,a.ctx):a.ctx,e===i.content?h=e!==i.ctx._wrp?i.ctx._wrp:void 0:e!==y.content?e===a.template?(h=y.tmpl,n._wrp=y.content):h=y.content||i.content:h=i.content,y.props.link===!1&&(n=n||{},n.link=!1),(x=y.props.itemVar)&&("~"!==x.charAt(0)&&I("Use itemVar='~myItem'"),x=x.slice(1))),i&&(s=s||i._.onRender,n=L(n,i.ctx)),o===!0&&(v=!0,o=0),s&&(n&&n.link===!1||a&&a._.noVws)&&(s=void 0),m=s,s===!0&&(m=void 0,s=i._.onRender),n=e.helpers?L(e.helpers,n):n,b=n,te(t)&&!r)for(c=v?i:void 0!==o&&i||new _(n,"array",i,t,e,o,s),i&&i._.useKey&&(c._.bnd=!a||a._.bnd&&a),x&&(c.it=x),x=c.it,l=0,p=t.length;p>l;l++)x&&d(t[l]),f=new _(b,"item",c,t[l],e,(o||0)+l,s,h),g=e.fn(t[l],f,se),k+=c._.onRender?c._.onRender(g,f):g;else x&&d(t),c=v?i:new _(b,w||"data",i,t,e,o,s,h),a&&!a.flow&&(c.tag=a),k+=e.fn(t,c,se);return m?m(k,c):k}function F(e,t,n){var r=void 0!==n?ee(n)?n.call(t.data,e,t):n||"":"{Error: "+e.message+"}";return ae.onError&&void 0!==(n=ae.onError.call(t.data,e,n&&r,t))&&(r=n),t&&!t.linkCtx?re.html(r):r}function S(e){throw new se.Err(e)}function I(e){S("Syntax error\n"+e)}function U(e,t,n,r,i){function o(t){t-=v,t&&m.push(e.substr(v,t).replace(_e,"\\n"))}function s(t,n){t&&(t+="}}",I((n?"{{"+n+"}} block has {{/"+t+" without {{"+t:"Unmatched or missing {{/"+t)+", in template:\n"+e))}function a(a,d,u,c,g,x,_,b,y,k,j,C){(_&&d||y&&!u||b&&":"===b.slice(-1)||k)&&I(a),x&&(g=":",c=Ne),y=y||n&&!i;var T=(d||n)&&[[]],A="",V="",R="",M="",$="",N="",E="",F="",S=!y&&!g;u=u||(b=b||"#data",g),o(C),v=C+a.length,_?f&&m.push(["*","\n"+b.replace(/^:/,"ret+= ").replace(be,"$1")+";\n"]):u?("else"===u&&(je.test(b)&&I('for "{{else if expr}}" use "{{else expr}}"'),T=w[7]&&[[]],w[8]=e.substring(w[8],C),w=h.pop(),m=w[2],S=!0),b&&O(b.replace(_e," "),T,t).replace(ke,function(e,t,n,r,i,o,s,a){return r="'"+i+"':",s?(V+=o+",",M+="'"+a+"',"):n?(R+=r+"j._cp("+o+',"'+a+'",view),',N+=r+"'"+a+"',"):t?E+=o:("trigger"===i&&(F+=o),A+=r+o+",",$+=r+"'"+a+"',",p=p||Ve.test(i)),""}).slice(0,-1),T&&T[0]&&T.pop(),l=[u,c||!!r||p||"",S&&[],J(M||(":"===u?"'#data',":""),$,N),J(V||(":"===u?"data,":""),A,R),E,F,T||0],m.push(l),S&&(h.push(w),w=l,w[8]=v)):j&&(s(j!==w[0]&&"else"!==w[0]&&j,w[0]),w[8]=e.substring(w[8],C),w=h.pop()),s(!w&&j),m=w[2]}var d,u,l,p,c,f=ae.allowCode||t&&t.allowCode||ue.allowCode===!0,g=[],v=0,h=[],m=g,w=[,,g];if(f&&t._is&&(t.allowCode=f),n&&(void 0!==r&&(e=e.slice(0,-r.length-2)+fe),e=le+e+fe),s(h[0]&&h[0][2].pop()[0]),e.replace(G,a),o(e.length),(v=g[g.length-1])&&s(""+v!==v&&+v[8]===v[8]&&v[0]),n){for(u=B(g,e,n),c=[],d=g.length;d--;)c.unshift(g[d][7]);q(u,c)}else u=B(g,t);return u}function q(e,t){var n,r,i=0,o=t.length;for(e.deps=[];o>i;i++){r=t[i];for(n in r)"_jsvto"!==n&&r[n].length&&(e.deps=e.deps.concat(r[n]))}e.paths=r}function J(e,t,n){return[e.slice(0,-1),t.slice(0,-1),n.slice(0,-1)]}function K(e,t){return"\n	"+(t?t+":{":"")+"args:["+e[0]+"]"+(e[1]||!t?",\n	props:{"+e[1]+"}":"")+(e[2]?",\n	ctx:{"+e[2]+"}":"")}function O(e,t,n){function r(r,m,w,x,_,b,y,k,j,C,T,A,V,R,M,$,N,E,F,S){function q(e,n,r,s,a,d,p,c){var f="."===r;if(r&&(_=_.slice(n.length),/^\.?constructor$/.test(c||_)&&I(e),f||(e=(s?'view.hlp("'+s+'")':a?"view":"data")+(c?(d?"."+d:s?"":a?"":"."+r)+(p||""):(c=s?"":a?d||"":r,"")),e+=c?"."+c:"",e=n+("view.data"===e.slice(0,9)?e.slice(5):e)),u)){if(O="linkTo"===i?o=t._jsvto=t._jsvto||[]:l.bd,B=f&&O[O.length-1]){if(B._jsv){for(;B.sb;)B=B.sb;B.bnd&&(_="^"+_.slice(1)),B.sb=_,B.bnd=B.bnd||"^"===_.charAt(0)}}else O.push(_);h[g]=F+(f?1:0)}return e}x&&!k&&(_=x+_),b=b||"",w=w||m||A,_=_||j,C=C||N||"";var J,K,O,B,L,Q=")";if("["===C&&(C="[j._sq(",Q=")]"),!y||d||a){if(u&&$&&!d&&!a&&(!i||s||o)&&(J=h[g-1],S.length-1>F-(J||0))){if(J=S.slice(J,F+r.length),K!==!0)if(O=o||p[g-1].bd,B=O[O.length-1],B&&B.prm){for(;B.sb&&B.sb.prm;)B=B.sb;L=B.sb={path:B.sb,bnd:B.bnd}}else O.push(L={path:O.pop()});$=pe+":"+J+" onerror=''"+ce,K=f[$],K||(f[$]=!0,f[$]=K=U($,n,!0)),K!==!0&&L&&(L._jsv=K,L.prm=l.bd,L.bnd=L.bnd||L.path&&L.path.indexOf("^")>=0)}return d?(d=!V,d?r:A+'"'):a?(a=!R,a?r:A+'"'):(w?(h[g]=F++,l=p[++g]={bd:[]},w):"")+(E?g?"":(c=S.slice(c,F),(i?(i=s=o=!1,"\b"):"\b,")+c+(c=F+r.length,u&&t.push(l.bd=[]),"\b")):k?(g&&I(e),u&&t.pop(),i=_,s=x,c=F+r.length,x&&(u=l.bd=t[i]=[]),_+":"):_?_.split("^").join(".").replace(we,q)+(C?(l=p[++g]={bd:[]},v[g]=Q,C):b):b?b:M?(M=v[g]||M,v[g]=!1,l=p[--g],M+(C?(l=p[++g],v[g]=Q,C):"")):T?(v[g]||I(e),","):m?"":(d=V,a=R,'"'))}I(e)}var i,o,s,a,d,u=t&&t[0],l={bd:u},p={0:l},c=0,f=(n?n.links:u&&(u.links=u.links||{}))||W.tmpl.links,g=0,v={},h={},m=(e+(n?" ":"")).replace(xe,r);return!g&&m||I(e)}function B(e,t,n){var r,i,o,s,a,d,u,l,p,c,f,g,v,h,m,w,x,_,b,y,k,j,C,T,A,R,M,$,N,E,F=0,S=de.useViews||t.useViews||t.tags||t.templates||t.helpers||t.converters,U="",J={},O=e.length;for(""+t===t?(_=n?'data-link="'+t.replace(_e," ").slice(1,-1)+'"':t,t=0):(_=t.tmplName||"unnamed",t.allowCode&&(J.allowCode=!0),t.debug&&(J.debug=!0),f=t.bnds,x=t.tmpls),r=0;O>r;r++)if(i=e[r],""+i===i)U+='\n+"'+i+'"';else if(o=i[0],"*"===o)U+=";\n"+i[1]+"\nret=ret";else{if(s=i[1],k=!n&&i[2],a=K(i[3],"params")+"},"+K(v=i[4]),$=i[5],E=i[6],j=i[8]&&i[8].replace(be,"$1"),(A="else"===o)?g&&g.push(i[7]):(F=0,f&&(g=i[7])&&(g=[g],F=f.push(1))),S=S||v[1]||v[2]||g||/view.(?!index)/.test(v[0]),(R=":"===o)?s&&(o=s===Ne?">":s+o):(k&&(b=V(j,J),b.tmplName=_+"/"+o,b.useViews=b.useViews||S,B(k,b),S=b.useViews,x.push(b)),A||(y=o,S=S||o&&(!oe[o]||!oe[o].flow),T=U,U=""),C=e[r+1],C=C&&"else"===C[0]),N=$?";\ntry{\nret+=":"\n+",h="",m="",R&&(g||E||s&&s!==Ne)){if(M=new Function("data,view,j,u"," // "+_+" "+F+" "+o+"\nreturn {"+a+"};"),M._er=$,M._tag=o,n)return M;q(M,g),w='c("'+s+'",view,',c=!0,h=w+F+",",m=")"}if(U+=R?(n?($?"try{\n":"")+"return ":N)+(c?(c=void 0,S=p=!0,w+(g?(f[F-1]=M,F):"{"+a+"}")+")"):">"===o?(u=!0,"h("+v[0]+")"):(l=!0,"((v="+v[0]+")!=null?v:"+(n?"null)":'"")'))):(d=!0,"\n{view:view,tmpl:"+(k?x.length:"0")+","+a+"},"),y&&!C){if(U="["+U.slice(0,-1)+"]",w='t("'+y+'",view,this,',n||g){if(U=new Function("data,view,j,u"," // "+_+" "+F+" "+y+"\nreturn "+U+";"),U._er=$,U._tag=y,g&&q(f[F-1]=U,g),n)return U;h=w+F+",undefined,",m=")"}U=T+N+w+(F||U)+")",g=0,y=0}$&&(S=!0,U+=";\n}catch(e){ret"+(n?"urn ":"+=")+h+"j._err(e,view,"+$+")"+m+";}"+(n?"":"ret=ret"))}U="// "+_+"\nvar v"+(d?",t=j._tag":"")+(p?",c=j._cnvt":"")+(u?",h=j._html":"")+(n?";\n":',ret=""\n')+(J.debug?"debugger;":"")+U+(n?"\n":";\nreturn ret;"),ae.debugMode!==!1&&(U="try {\n"+U+"\n}catch(e){\nreturn j._err(e, view);\n}");try{U=new Function("data,view,j,u",U)}catch(L){I("Compiled template code:\n\n"+U+'\n: "'+L.message+'"')}return t&&(t.fn=U,t.useViews=!!S),U}function L(e,t){return e&&e!==t?t?u(u({},t),e):e:t&&u({},t)}function Q(e){return $e[e]||($e[e]="&#"+e.charCodeAt(0)+";")}function H(e){var t,n,r=[];if(typeof e===Ee)for(t in e)n=e[t],t===Y||ee(n)||r.push({key:t,prop:n});return r}function P(e,n,r){var i=this.jquery&&(this[0]||S('Unknown template: "'+this.selector+'"')),o=i.getAttribute(Fe);return N.call(o?t.data(i)[Se]:ne(i),e,n,r)}function D(e){return void 0!=e?Ae.test(e)&&(""+e).replace(Re,Q)||e:""}var Z=t===!1;t=t&&t.fn?t:e.jQuery;var z,G,W,X,Y,ee,te,ne,re,ie,oe,se,ae,de,ue,le,pe,ce,fe,ge,ve,he,me="v0.9.80",we=/^(!*?)(?:null|true|false|\d[\d.]*|([\w$]+|\.|~([\w$]+)|#(view|([\w$]+))?)([\w$.^]*?)(?:[.[^]([\w$]+)\]?)?)$/g,xe=/(\()(?=\s*\()|(?:([([])\s*)?(?:(\^?)(!*?[#~]?[\w$.^]+)?\s*((\+\+|--)|\+|-|&&|\|\||===|!==|==|!=|<=|>=|[<>%*:?\/]|(=))\s*|(!*?[#~]?[\w$.^]+)([([])?)|(,\s*)|(\(?)\\?(?:(')|("))|(?:\s*(([)\]])(?=\s*[.^]|\s*$|[^([])|[)\]])([([]?))|(\s+)/g,_e=/[ \t]*(\r\n|\n|\r)/g,be=/\\(['"])/g,ye=/['"\\]/g,ke=/(?:\x08|^)(onerror:)?(?:(~?)(([\w$_\.]+):)?([^\x08]+))\x08(,)?([^\x08]+)/gi,je=/^if\s/,Ce=/<(\w+)[>\s]/,Te=/[\x00`><"'&=]/g,Ae=/[\x00`><\"'&=]/,Ve=/^on[A-Z]|^convert(Back)?$/,Re=Te,Me=0,$e={"&":"&amp;","<":"&lt;",">":"&gt;","\x00":"&#0;","'":"&#39;",'"':"&#34;","`":"&#96;","=":"&#61;"},Ne="html",Ee="object",Fe="data-jsv-tmpl",Se="jsvTmpl",Ie="For #index in nested block use #getIndex().",Ue={},qe=e.jsrender,Je=qe&&t&&!t.render,Ke={template:{compile:j},tag:{compile:y},viewModel:{compile:A},helper:{},converter:{}};if(X={jsviews:me,sub:{View:_,Err:d,tmplFn:U,parse:O,extend:u,extendCtx:L,syntaxErr:I,onStore:{},addSetting:M,settings:{allowCode:!1},advSet:s,_ths:i,_tg:function(){},_cnvt:h,_tag:x,_er:S,_err:F,_html:D,_cp:o,_sq:function(e){return"constructor"===e&&I(""),e}},settings:{delimiters:l,advanced:function(e){return e?(u(de,e),se.advSet(),ue):de}},getCtx:o,map:$},(d.prototype=new Error).constructor=d,c.depends=function(){return[this.get("item"),"index"]},f.depends="index",_.prototype={get:p,getIndex:f,getRsc:w,getTmpl:v,hlp:g,_is:"view"},se=X.sub,ue=X.settings,!(qe||t&&t.render)){for(z in Ke)R(z,Ke[z]);re=X.converters,ie=X.helpers,oe=X.tags,se._tg.prototype={baseApply:k,cvtArgs:m},W=se.topView=new _,t?(t.fn.render=P,Y=t.expando,t.observable&&(u(se,t.views.sub),X.map=t.views.map)):(t={},Z&&(e.jsrender=t),t.renderFile=t.__express=t.compile=function(){throw"Node.js: use npm jsrender, or jsrender-node.js"},t.isFunction=function(e){return"function"==typeof e},t.isArray=Array.isArray||function(e){return"[object Array]"==={}.toString.call(e)},se._jq=function(e){e!==t&&(u(e,t),t=e,t.fn.render=P,delete t.jsrender,Y=t.expando)},t.jsrender=me),ae=se.settings,ae.allowCode=!1,ee=t.isFunction,t.render=Ue,t.views=X,t.templates=ne=X.templates;for(ve in ae)M(ve);(ue.debugMode=function(e){return void 0===e?ae.debugMode:(ae.debugMode=e,ae.onError=e+""===e?new Function("","return '"+e+"';"):ee(e)?e:void 0,ue)})(!1),de=ae.advanced={useViews:!1,_jsv:!1},oe({"if":{render:function(e){var t=this,n=t.tagCtx,r=t.rendering.done||!e&&(arguments.length||!n.index)?"":(t.rendering.done=!0,t.selected=n.index,n.render(n.view,!0));return r},flow:!0},"for":{render:function(e){var t,n=!arguments.length,r=this,i=r.tagCtx,o="",s=0;return r.rendering.done||(t=n?i.view.data:e,void 0!==t&&(o+=i.render(t,n),s+=te(t)?t.length:1),(r.rendering.done=s)&&(r.selected=i.index)),o},flow:!0},props:{baseTag:"for",dataMap:$(H),flow:!0},include:{flow:!0},"*":{render:o,flow:!0},":*":{render:o,flow:!0},dbg:ie.dbg=re.dbg=a}),re({html:D,attr:D,url:function(e){return void 0!=e?encodeURI(""+e):null===e?e:""}})}return ae=se.settings,te=t.isArray,ue.delimiters("{{","}}","^"),Je&&qe.views.sub._jq(t),t||qe},window);
//# sourceMappingURL=jsrender.min.js.map
;
define('app/simplelayout/Element',["app/simplelayout/idHelper", "jsrender"], function(idHelper) {

  "use strict";

  function Element(template, represents) {

    this.template = $.templates(template);
    this.represents = represents;
    this.enabled = true;

    this.create = function(data) {
      this.element = $(this.template.render(data));
      this.id = idHelper.createGUID();
      this.element.data({ id: this.id, object: this });
      return this.element;
    };

    this.data = function(data) {
      if(data) {
        return this.element.data(data);
      }
      return this.element.data();
    };

    this.remove = function() {
      this.element.remove();
      return this;
    };

    this.detach = function() {
      this.element.detach();
      return this;
    };

    this.attachToolbar = function(toolbar) {
      this.toolbar = toolbar;
      this.element.append(toolbar.element);
      return this;
    };

    this.isEnabled = function(state) {
      this.element.toggleClass("disabled", !state);
      this.enabled = state;
      return this;
    };

    this.restore = function(restoreElement, restoreParent, restoreRepresents) {
      this.element = $(restoreElement);
      this.parent = restoreParent;
      this.data({ id: this.id, object: this, parent: restoreParent, represents: restoreRepresents });
      this.represents = restoreRepresents;
    };

    return this;
  }

  return Element;

});

define('app/simplelayout/Block',[
      "app/simplelayout/EventEmitter",
      "app/simplelayout/transactional",
      "app/simplelayout/Element"
    ], function(EventEmitter, transactional, Element) {

  "use strict";

  var Block = function(content, type) {

    if (!(this instanceof Block)) {
      throw new TypeError("Block constructor cannot be called as a function.");
    }

    this.name = "block";

    this.type = type;

    var frame = $($.templates('<div class="iFrameFix"></div>').render());

    var template = '<div data-type="{{:type}}" class="sl-block {{:type}}"><div class="sl-block-content">{{:content}}</div></div>';

    Element.call(this, template);

    this.create({ type: type, content: content });

    this.content = function(toReplace) {
      $(".sl-block-content", this.element).html(toReplace);
      EventEmitter.trigger("blockReplaced", [this]);
      return this;
    };

    this.delete = function() { return this.parent.deleteBlock(this.id); };

    this.fixFrame = function() {
      this.element.prepend(frame);
      return this;
    };

    this.fixFrame();

    this.enableFrame = function() {
      frame.css("display", "block");
      return this;
    };

    this.disableFrame = function() {
      frame.css("display", "none");
      return this;
    };

    this.restore = function(restoreElement, restoreParent, restoreType, represents) {
      this.type = restoreType;
      Block.prototype.restore.call(this, restoreElement, restoreParent, represents);
      this.fixFrame();
      this.commit();
    };

    this.toJSON = function() { return { represents: this.represents, type: this.type }; };

  };

  transactional.call(Block.prototype);
  Element.call(Block.prototype);

  return Block;

});

define('app/simplelayout/Toolbar',["app/simplelayout/Element"], function(Element) {

  "use strict";

  var Toolbar = function(actions, orientation, type) {

    if (!(this instanceof Toolbar)) {
      throw new TypeError("Toolbar constructor cannot be called as a function.");
    }

    actions = actions || [];

    var template = $.templates("<ul class='sl-toolbar{{if type}}-{{:type}}{{/if}}{{if orientation}} {{:orientation}}{{/if}}'>{{for actions}}<li><a {{props}} {{>key}}='{{>prop}}' {{/props}}></a></li><li class='delimiter'></li>{{/for}}</ul>");

    Element.call(this, template);

    var normalizedActions = [];

    $.each(actions, function(key, value) {
      normalizedActions.push(value);
    });

    this.create({ actions: normalizedActions, orientation: orientation, type: type });

    this.disable = function(action) { $("." + action, this.element).css("display", "none"); };

    this.enable = function(action) { $("." + action, this.element).css("display", "inline"); };

  };

  Element.call(Toolbar.prototype);

  return Toolbar;

});

define('app/helpers/template_range',["jsrender"], function() {

  "use strict";

  $.views.tags({
    range: {
      // Inherit from {{for}} tag
      baseTag: "for",

      // Override the render method of {{for}}
      render: function(val) {
        var array = val,
          start = this.tagCtx.props.start || 0,
          end = this.tagCtx.props.end;

        if (start || end) {
          if (!this.tagCtx.args.length) {
            // No array argument passed from tag, so create a computed array of integers from start to end
            array = [];
            end = end || 0;
            for (var i = start; i <= end; i++) {
              array.push(i);
            }
          } else if ($.isArray(array)) {
            // There is an array argument and start and end properties, so render using the array truncated to the chosen range
            array = array.slice(start, end);
          }
        }

        // Call the {{for}} baseTag render method
        return this.base(array);
      },

      // override onArrayChange of the {{for}} tag implementation
      onArrayChange: function() {
        this.refresh();
      }
    }
  });

});

define('app/simplelayout/Layout',[
      "app/simplelayout/Block",
      "app/simplelayout/EventEmitter",
      "app/simplelayout/transactional",
      "app/simplelayout/Element",
      "app/simplelayout/Toolbar",
      "app/helpers/template_range"
    ],
    function(
      Block,
      EventEmitter,
      transactional,
      Element,
      Toolbar) {

  "use strict";

  var Layout = function(columns) {
    if (!(this instanceof Layout)) {
      throw new TypeError("Layout constructor cannot be called as a function.");
    }

    columns = columns || 4;

    var template = "<div class='sl-layout'>{{range start=1 end=columns ~columns=columns}}<div class='sl-column sl-col-{{:~columns}}'></div>{{/range}}</div>";

    Element.call(this, template);

    this.name = "layout";

    this.create({ columns: columns });

    this.columns = columns;

    this.blocks = {};

    this.toolbar = new Toolbar();

    this.hasBlocks = function() { return Object.keys(this.blocks).length > 0; };

    this.delete = function() { return this.parent.deleteLayout(this.id); };

    this.insertBlock = function(content, type) {
      var block = new Block(content, type);
      block.parent = this;
      block.data({ parent: this });
      this.blocks[block.id] = block;
      EventEmitter.trigger("blockInserted", [block]);
      return block;
    };

    this.deleteBlock = function(id) {
      var block = this.blocks[id];
      delete this.blocks[id];
      EventEmitter.trigger("blockDeleted", [block]);
      return block;
    };

    this.getCommittedBlocks = function() {
      return $.grep($.map(this.blocks, function(block) { return block; }), function(block) {
        return block.committed;
      });
    };

    this.getInsertedBlocks = function() {
      return $.grep($.map(this.blocks, function(block) { return block; }), function(block) {
        return !block.committed;
      });
    };

    this.moveBlock = function(block, target) {
      EventEmitter.trigger("beforeBlockMoved", [block]);
      this.deleteBlock(block.id);
      block.parent = target;
      block.data({ parent: target });
      target.blocks[block.id] = block;
      EventEmitter.trigger("blockMoved", [block]);
      return this;
    };

    this.restore = function(restoreElement, restoreParent, restoreColumn, represents) {
      var self = this;
      this.columns = restoreColumn;
      Layout.prototype.restore.call(this, restoreElement, restoreParent, represents);
      this.commit();
      $(".sl-block", restoreElement).each(function() {
        self.insertBlock().restore(this, self, $(this).data().type, $(this).data().uid);
      });
    };

    this.toJSON = function() { return { columns: this.columns, blocks: this.blocks }; };

  };

  transactional.call(Layout.prototype);
  Element.call(Layout.prototype);

  return Layout;

});

define('app/simplelayout/Layoutmanager',[
      "app/simplelayout/Layout",
      "app/simplelayout/Block",
      "app/simplelayout/EventEmitter",
      "app/simplelayout/Element",
      "app/simplelayout/transactional",
      "app/helpers/template_range"
    ],
    function(
      Layout,
      Block,
      EventEmitter,
      Element,
      transactional) {

  "use strict";

  var Layoutmanager = function() {

    if (!(this instanceof Layoutmanager)) {
      throw new TypeError("Layoutmanager constructor cannot be called as a function.");
    }

    var template = "<div class='sl-simplelayout'></div>";

    Element.call(this, template);

    this.name = "layoutmanager";

    this.create();

    this.layouts = {};

    this.attachTo = function(target) {
      $(target).append(this.element);
      return this;
    };

    this.insertLayout = function(columns) {
      var layout = new Layout(columns);
      layout.parent = this;
      layout.data({ parent: this });
      this.layouts[layout.id] = layout;
      EventEmitter.trigger("layoutInserted", [layout]);
      return layout;
    };

    this.deleteLayout = function(id) {
      var layout = this.layouts[id];
      delete this.layouts[id];
      EventEmitter.trigger("layoutDeleted", [layout]);
      return layout;
    };

    this.hasLayouts = function() { return Object.keys(this.layouts).length > 0; };

    this.getInsertedBlocks = function() {
      return $.map(this.layouts, function(layout) {
        return layout.getInsertedBlocks();
      });
    };

    this.getCommittedBlocks = function() {
      return $.map(this.layouts, function(layout) {
        return layout.getCommittedBlocks();
      });
    };

    this.moveBlock = function(block, target) {
      block.parent.moveBlock(block, target);
      return this;
    };

    this.restore = function(restoreElement, represents) {
      var self = this;
      Layoutmanager.prototype.restore.call(this, restoreElement, null, represents);
      this.commit();
      $(".sl-layout", restoreElement).each(function() {
        self.insertLayout().restore(this, self, $(".sl-column", this).length);
      });
    };

    this.toJSON = function() { return { layouts: this.layouts, represents: this.represents }; };

  };

  Element.call(Layoutmanager.prototype);
  transactional.call(Layoutmanager.prototype);

  return Layoutmanager;

});

/*
 * jQuery css bezier animation support -- Jonah Fox
 * version 0.0.1
 * Released under the MIT license.
 */
/*
  var path = $.path.bezier({
    start: {x:10, y:10, angle: 20, length: 0.3},
    end:   {x:20, y:30, angle: -20, length: 0.2}
  })
  $("myobj").animate({path: path}, duration)

*/

;(function($){

  $.path = {};

  var V = {
    rotate: function(p, degrees) {
      var radians = degrees * Math.PI / 180,
        c = Math.cos(radians),
        s = Math.sin(radians);
      return [c*p[0] - s*p[1], s*p[0] + c*p[1]];
    },
    scale: function(p, n) {
      return [n*p[0], n*p[1]];
    },
    add: function(a, b) {
      return [a[0]+b[0], a[1]+b[1]];
    },
    minus: function(a, b) {
      return [a[0]-b[0], a[1]-b[1]];
    }
  };

  $.path.bezier = function( params, rotate ) {
    params.start = $.extend( {angle: 0, length: 0.3333}, params.start );
    params.end = $.extend( {angle: 0, length: 0.3333}, params.end );

    this.p1 = [params.start.x, params.start.y];
    this.p4 = [params.end.x, params.end.y];

    var v14 = V.minus( this.p4, this.p1 ),
      v12 = V.scale( v14, params.start.length ),
      v41 = V.scale( v14, -1 ),
      v43 = V.scale( v41, params.end.length );

    v12 = V.rotate( v12, params.start.angle );
    this.p2 = V.add( this.p1, v12 );

    v43 = V.rotate(v43, params.end.angle );
    this.p3 = V.add( this.p4, v43 );

    this.f1 = function(t) { return (t*t*t); };
    this.f2 = function(t) { return (3*t*t*(1-t)); };
    this.f3 = function(t) { return (3*t*(1-t)*(1-t)); };
    this.f4 = function(t) { return ((1-t)*(1-t)*(1-t)); };

    /* p from 0 to 1 */
    this.css = function(p) {
      var f1 = this.f1(p), f2 = this.f2(p), f3 = this.f3(p), f4=this.f4(p), css = {};
      if (rotate) {
        css.prevX = this.x;
        css.prevY = this.y;
      }
      css.x = this.x = ( this.p1[0]*f1 + this.p2[0]*f2 +this.p3[0]*f3 + this.p4[0]*f4 +.5 )|0;
      css.y = this.y = ( this.p1[1]*f1 + this.p2[1]*f2 +this.p3[1]*f3 + this.p4[1]*f4 +.5 )|0;
      css.left = css.x + "px";
      css.top = css.y + "px";
      return css;
    };
  };

  $.path.arc = function(params, rotate) {
    for ( var i in params ) {
      this[i] = params[i];
    }

    this.dir = this.dir || 1;

    while ( this.start > this.end && this.dir > 0 ) {
      this.start -= 360;
    }

    while ( this.start < this.end && this.dir < 0 ) {
      this.start += 360;
    }

    this.css = function(p) {
      var a = ( this.start * (p ) + this.end * (1-(p )) ) * Math.PI / 180,
        css = {};

      if (rotate) {
        css.prevX = this.x;
        css.prevY = this.y;
      }
      css.x = this.x = ( Math.sin(a) * this.radius + this.center[0] +.5 )|0;
      css.y = this.y = ( Math.cos(a) * this.radius + this.center[1] +.5 )|0;
      css.left = css.x + "px";
      css.top = css.y + "px";
      return css;
    };
  };

  $.fx.step.path = function(fx) {
    var css = fx.end.css( 1 - fx.pos );
    if ( css.prevX != null ) {
      $.cssHooks.transform.set( fx.elem, "rotate(" + Math.atan2(css.prevY - css.y, css.prevX - css.x) + ")" );
    }
    fx.elem.style.top = css.top;
    fx.elem.style.left = css.left;
  };

})(jQuery);
define("jquery-path", (function (global) {
    return function () {
        var ret, fn;
        return ret || global.jQuery.path;
    };
}(this)));

define('app/toolbox/Toolbox',["app/simplelayout/Element", "jsrender", "jquery-path"], function(Element) {

  "use strict";

  var Toolbox = function(options) {

    if (!(this instanceof Toolbox)) {
      throw new TypeError("Toolbox constructor cannot be called as a function.");
    }

    var template = $.templates(
    /*eslint no-multi-str: 0 */
    "<div id='sl-toolbox' class='sl-toolbox'> \
      <div> \
        <a class='sl-toolbox-header blocks'> \
          <span></span> \
        </a> \
          <div class='sl-toolbox-blocks'> \
            {{for blocks}} \
              <a class='sl-toolbox-block {{:contentType}}' data-type='{{:contentType}}' data-form-url='{{:formUrl}}'> \
                <span class='icon-{{:contentType}}'></span> \
                <span class='description'>{{:title}}</span> \
              </a> \
            {{/for}} \
          </div> \
          {{if canChangeLayout}} \
            <a class='sl-toolbox-header layouts'> \
              <span></span> \
            </a> \
            <div class='sl-toolbox-layouts'> \
              {{props layouts}} \
                <a class='sl-toolbox-layout' data-columns='{{>prop}}'> \
                  <span>{{>prop}}</span> \
                  <span class='description'>{{>prop}}{{>#parent.parent.data.labels.labelColumnPostfix}}</span> \
                </a> \
              {{/props}} \
            </div> \
          {{/if}} \
        </div> \
      </div>");

    Element.call(this, template);

    this.options = $.extend({
      layouts: [1, 2, 4],
      blocks: [],
      labels: {},
      layoutActions: {}
    }, options || {});

    this.create({
      blocks: this.options.blocks,
      layouts: this.options.layouts,
      labels: this.options.labels,
      canChangeLayout: this.options.canChangeLayout
    });

    var blockObjects = {};
    $.each(this.options.blocks, function(idx, block) {
      blockObjects[block.contentType] = block;
    });

    this.options.blocks = blockObjects;

    this.attachTo = function(target) { target.append(this.element); };

    this.blocksEnabled = function(state) { $(".sl-toolbox-blocks", this.element).toggleClass("disabled", !state); };

    /* Patch for registring beforeStart event */
    var oldMouseStart = $.ui.draggable.prototype._mouseStart;
    $.ui.draggable.prototype._mouseStart = function (event, overrideHandle, noActivation) {
        this._trigger("beforeStart", event, this._uiHash());
        oldMouseStart.apply(this, [event, overrideHandle, noActivation]);
    };

    this.triggerHint = function(addable, target, animationOptions) {

      animationOptions = $.extend({
        time: 500,
        easing: "easeInOutQuad"
      }, animationOptions);
      var path = {
        start: {
          x: 0,
          y: addable.position().top,
          angle: 70
        },
        end: {
          x: -$(window).width() / 2 + addable.width(),
          y: $(window).height() / 2 - addable.height(),
          angle: 290
        }
      };
      /*eslint new-cap: 0 */
      var bezier = new $.path.bezier(path);
      var clone = addable.clone().insertAfter(addable);
      clone.css("position", "absolute").css("z-index", "1");
      clone.animate({ path: bezier }, animationOptions.time, animationOptions.easing, function() { clone.css("z-index", "auto").addClass("hintDropped"); });
      setTimeout(function() { clone.remove(); }, animationOptions.time + 300);
    };

  };

  Element.call(Toolbox.prototype);

  return Toolbox;

});

define('app/simplelayout/Simplelayout',[
  "app/simplelayout/Layoutmanager",
  "app/simplelayout/Toolbar",
  "app/toolbox/Toolbox",
  "app/simplelayout/EventEmitter"
  ],
  function(
    Layoutmanager,
    Toolbar,
    Toolbox,
    EventEmitter) {

  "use strict";

  var Simplelayout = function(options) {

    if (!(this instanceof Simplelayout)) {
      throw new TypeError("Simplelayout constructor cannot be called as a function.");
    }

    var root = $(":root");

    var self = this;

    var sortableHelper = function() { return $('<div class="draggableHelper"><div>'); };

    var LAYOUT_SORTABLE = {
      connectWith: ".sl-simplelayout",
      items: ".sl-layout",
      handle: ".sl-toolbar-layout .move",
      placeholder: "layout-placeholder",
      cursorAt: { left: 50, top: 50 },
      // axis: "y",
      forcePlaceholderSize: true,
      helper: sortableHelper,
      receive: function(event, ui) {
        var layout;
        if(ui.item.hasClass("sl-toolbox-layout")) {
          var item = $(this).find(".ui-draggable");
          layout = $(this).data().object.insertLayout(ui.item.data().columns);
          layout.element.insertAfter(item);
          item.remove();
        } else {
          self.moveLayout($(ui.item).data().object, $(this).data().object);
          self.disableFrames();
        }
      },
      beforeStart: function(event, ui) {
        if(ui.item.hasClass("sl-layout")) {
          self.restrictLayout(ui.item.data().object.columns);
        }
      },
      start: function() {
        self.enableFrames();
        root.addClass("sl-layout-dragging");
        $(".sl-simplelayout").sortable("refreshPositions");
      },
      update: function(event, ui) {
        if(ui.item.parent()[0] === this && !ui.sender) {
          EventEmitter.trigger("layoutMoved", [ui.item.data().object]);
        }
      },
      stop: function(event, ui) {
        if(ui.item.hasClass("sl-layout")) {
          self.allowLayout(ui.item.data().object.columns);
        }
        root.removeClass("sl-layout-dragging");
        self.disableFrames();
      }
    };

    var BLOCK_SORTABLE = {
      connectWith: ".sl-column",
      placeholder: "block-placeholder",
      forcePlaceholderSize: true,
      handle: ".sl-toolbar-block .move",
      helper: sortableHelper,
      cursorAt: { left: 50, top: 50 },
      receive: function(event, ui) {
        var block;
        if($(ui.item).hasClass("sl-toolbox-block")) {
          var item = $(this).find(".ui-draggable");
          var layout = $(this).parents(".sl-layout").data().object;
          block = layout.insertBlock("", $(ui.item).data().type);
          block.element.insertAfter(item);
          item.remove();
        } else {
          var sourceLayout = ui.sender.parents(".sl-layout").data().object;
          sourceLayout.moveBlock(ui.item.data().object, $(this).parents(".sl-layout").data().object);
        }
      },
      start: function() {
        self.enableFrames();
        root.addClass("sl-block-dragging");
        $(".sl-column").sortable("refreshPositions");
      },
      stop: function() {
        self.disableFrames();
        root.removeClass("sl-block-dragging");
      },
      update: function(event, ui) {
        if(ui.item.parent()[0] === this && !ui.sender) {
          EventEmitter.trigger("blockMoved", [ui.item.data().object]);
        }
      }
    };

    this.options = $.extend({
      toolbox: new Toolbox(),
      editLayouts: true,
      layoutRestrictions: {}
    }, options || {});

    this.managers = {};

    this.insertManager = function() {
      var manager = new Layoutmanager();
      this.managers[manager.id] = manager;
      return manager;
    };

    this.moveLayout = function(layout, target) {
      var source = layout.parent;

      layout.data({ parent: target });
      layout.parent = target;
      target.layouts[layout.id] = layout;

      source.deleteLayout(layout.id);
      EventEmitter.trigger("layoutMoved", [layout]);
      return this;
    };

    this.getCommittedBlocks = function() {
      return $.map(this.managers, function(manager) {
        return manager.getCommittedBlocks();
      });
    };

    this.getInsertedBlocks = function() {
      return $.map(this.managers, function(manager) {
        return manager.getInsertedBlocks();
      });
    };

    this.disableFrames = function() {
      $.each(this.getCommittedBlocks(), function(idx, block) {
        block.disableFrame();
      });
      return this;
    };

    this.enableFrames = function() {
      $.each(this.getCommittedBlocks(), function(idx, block) {
        block.enableFrame();
      });
      return this;
    };

    this.restrictLayout = function(layout) {
      if(this.options.layoutRestrictions[layout]) {
        $.each(this.options.layoutRestrictions[layout], function(idx, managerId) {
          self.managers[managerId].isEnabled(false).element.sortable("disable");
        });
      }
    };

    this.allowLayout = function(layout) {
      if(this.options.layoutRestrictions[layout]) {
        $.each(this.options.layoutRestrictions[layout], function(idx, managerId) {
          self.managers[managerId].isEnabled(true).element.sortable("enable");
        });
      }
    };

    this.on = function(eventType, callback) {
      EventEmitter.on(eventType, callback);
      return this;
    };

    this.serialize = function() { return JSON.stringify(this.managers); };

    this.restore = function(source) {
      this.source = source;
      $(".sl-simplelayout", source).each(function() {
        self.insertManager().restore(this, $(this).attr("id"));
      });
      $(".sl-simplelayout", this.source).sortable(LAYOUT_SORTABLE);
      $(".sl-column", this.source).sortable(BLOCK_SORTABLE);
      return this;
    };

    var TOOLBOX_COMPONENT_DRAGGABLE_SETTINGS = {
      helper: "clone",
      cursor: "pointer",
      beforeStart: function() {
        if($(this).hasClass("sl-toolbox-layout")) {
          self.restrictLayout($(this).data().columns);
        }
      },
      start: function() {
        self.enableFrames();
        if($(this).hasClass("sl-toolbox-block")) {
          root.addClass("sl-block-dragging");
        } else {
          root.addClass("sl-layout-dragging");
        }
      },
      stop: function() {
        self.allowLayout($(this).data().columns);
        self.disableFrames();
        root.removeClass("sl-block-dragging sl-layout-dragging");
      }
    };

    this.on("layout-committed", function(layout) {
      if(self.options.editLayouts) {
        var layoutToolbar = new Toolbar(self.options.toolbox.options.layoutActions, "vertical", "layout");
        layout.attachToolbar(layoutToolbar);
        $(".sl-column", layout.element).sortable(BLOCK_SORTABLE);
      }
    });

    this.on("block-committed", function(block) {
      if(self.options.toolbox.options.blocks[block.type]) {
        var blockToolbar = new Toolbar(self.options.toolbox.options.blocks[block.type].actions, "horizontal", "block");
        block.attachToolbar(blockToolbar);
      }
    });

    this.options.toolbox.element.find(".sl-toolbox-block, .sl-toolbox-layout").draggable(TOOLBOX_COMPONENT_DRAGGABLE_SETTINGS);
    this.options.toolbox.element.find(".sl-toolbox-layout").draggable("option", "connectToSortable", ".sl-simplelayout");
    this.options.toolbox.element.find(".sl-toolbox-block").draggable("option", "connectToSortable", ".sl-column");

    $(".sl-simplelayout").sortable(LAYOUT_SORTABLE);
    $(".sl-column").sortable(BLOCK_SORTABLE);

    root.addClass("simplelayout-initialized");

    /* Patch for registring beforeStart event */
    var oldMouseStart = $.ui.sortable.prototype._mouseStart;
    $.ui.sortable.prototype._mouseStart = function (event, overrideHandle, noActivation) {
        this._trigger("beforeStart", event, this._uiHash());
        oldMouseStart.apply(this, [event, overrideHandle, noActivation]);
    };

  };

  return Simplelayout;

});

require.config({
  "baseUrl": "js/lib/",
  "paths": {
    "app": "../app",
    "EventEmitter": "eventEmitter/EventEmitter.min",
    "jquery": "jquery/dist/jquery",
    "jqueryui": "jquery-ui/ui/minified/jquery-ui.custom.min",
    "jsrender": "jsrender/jsrender.min",
    "jquery-path": "jquery-path/jquery.path"
  },
  "shim": {
    "jsrender": {
      "deps": ["jquery"],
      "exports": "jQuery.fn.template"
    },
    "jqueryui": {
      "deps": ["jquery"]
    },
    "jquery-path": {
      "exports": "jQuery.path"
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

