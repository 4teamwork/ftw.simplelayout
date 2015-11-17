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

<<<<<<< HEAD
/*! JsRender v1.0.0-beta: http://www.jsviews.com/#jsrender
informal pre V1.0 commit counter: 64pre*/
!function(e){if("function"==typeof define&&define.amd)define('jsrender',e);else if("object"==typeof exports){var t=module.exports=e(!0,require("fs"));t.renderFile=t.__express=function(e,n,r){var i=t.templates("@"+e).render(n);return r&&r(null,i),i}}else e(!1)}(function(e,t){"use strict";function n(e,t){return function(){var n,r=this,i=r.base;return r.base=e,n=t.apply(r,arguments),r.base=i,n}}function r(e,t){return jt(t)&&(t=n(e?e._d?e:n(s,e):s,t),t._d=1),t}function i(e,t){for(var n in t.props)ct.test(n)&&(e[n]=r(e[n],t.props[n]))}function a(e){return e}function s(){return""}function o(e){try{throw"dbg breakpoint"}catch(t){}return this.base?this.baseApply(arguments):e}function l(e){Nt._dbgMode=e!==!1}function p(e){this.name=(G.link?"JsViews":"JsRender")+" Error",this.message=e||this.name}function d(e,t){var n;for(n in t)e[n]=t[n];return e}function u(e,t,n){return(0!==this||e)&&(W=e?e.charAt(0):W,X=e?e.charAt(1):X,Y=t?t.charAt(0):Y,et=t?t.charAt(1):et,tt=n||tt,e="\\"+W+"(\\"+tt+")?\\"+X,t="\\"+Y+"\\"+et,q="(?:(?:(\\w+(?=[\\/\\s\\"+Y+"]))|(?:(\\w+)?(:)|(>)|!--((?:[^-]|-(?!-))*)--|(\\*)))\\s*((?:[^\\"+Y+"]|\\"+Y+"(?!\\"+et+"))*?)",$t.rTag=q+")",q=new RegExp(e+q+"(\\/)?|(?:\\/(\\w+)))"+t,"g"),H=new RegExp("<.*>|([^\\\\]|^)[{}]|"+e+".*"+t)),[W,X,Y,et,tt]}function c(e,t){t||(t=e,e=void 0);var n,r,i,a,s=this,o=!t||"root"===t;if(e){if(a=s.type===t?s:void 0,!a)if(n=s.views,s._.useKey){for(r in n)if(a=n[r].get(e,t))break}else for(r=0,i=n.length;!a&&i>r;r++)a=n[r].get(e,t)}else if(o)for(;s.parent.parent;)a=s=s.parent;else for(;s&&!a;)a=s.type===t?s:void 0,s=s.parent;return a}function f(){var e=this.get("item");return e?e.index:void 0}function g(){return this.index}function v(e){var t,n=this,r=n.linkCtx,i=(n.ctx||{})[e];return void 0===i&&r&&r.ctx&&(i=r.ctx[e]),void 0===i&&(i=Mt[e]),i&&jt(i)&&!i._wrp&&(t=function(){return i.apply(this&&this!==z?this:n,arguments)},t._wrp=!0,d(t,i)),t||i}function m(e,t,n,r){var a,s,o="number"==typeof n&&t.tmpl.bnds[n-1],l=t.linkCtx;return void 0!==r?n=r={props:{},args:[r]}:o&&(n=o(t.data,t,kt)),s=n.args[0],(e||o)&&(a=l&&l.tag,a||(a=d(new $t._tg,{_:{inline:!l,bnd:o,unlinked:!0},tagName:":",cvt:e,flow:!0,tagCtx:n}),l&&(l.tag=a,a.linkCtx=l),n.ctx=J(n.ctx,(l?l.view:t).ctx)),a._er=r&&s,i(a,n),n.view=t,a.ctx=n.ctx||{},n.ctx=void 0,t._.tag=a,s=a.cvtArgs(a.convert||"true"!==e&&e)[0],s=o&&t._.onRender?t._.onRender(s,t,o):s,t._.tag=void 0),void 0!=s?s:""}function h(e){var t=this,n=t.tagCtx,r=n.view,i=n.args;return e=t.convert||e,e=e&&(""+e===e?r.getRsc("converters",e)||V("Unknown converter: '"+e+"'"):e),i=i.length||n.index?e?i.slice():i:[r.data],e&&(e.depends&&(t.depends=$t.getDeps(t.depends,t,e.depends,e)),i[0]=e.apply(t,i)),i}function w(e,t){for(var n,r,i=this;void 0===n&&i;)r=i.tmpl&&i.tmpl[e],n=r&&r[t],i=i.parent;return n||kt[e][t]}function x(e,t,n,r,a,s){t=t||D;var o,l,p,d,u,c,f,g,v,m,h,w,x,b,_,y,k,C,j="",A=t.linkCtx||0,T=t.ctx,M=n||t.tmpl,$="number"==typeof r&&t.tmpl.bnds[r-1];for("tag"===e._is?(o=e,e=o.tagName,r=o.tagCtxs,p=o.template):(l=t.getRsc("tags",e)||V("Unknown tag: {{"+e+"}} "),p=l.template),void 0!==s?(j+=s,r=s=[{props:{},args:[]}]):$&&(r=$(t.data,t,kt)),g=r.length,f=0;g>f;f++)m=r[f],(!A||!A.tag||f&&!A.tag._.inline||o._er)&&((w=m.tmpl)&&(w=m.content=M.tmpls[w-1]),m.index=f,m.tmpl=p||w,m.render=R,m.view=t,m.ctx=J(m.ctx,T)),(n=m.props.tmpl)&&(n=""+n===n?t.getRsc("templates",n)||Tt(n):n,m.tmpl=n),o||(o=new l._ctr,x=!!o.init,o.parent=c=T&&T.tag,o.tagCtxs=r,A&&(o._.inline=!1,A.tag=o,o.linkCtx=A),(o._.bnd=$||A.fn)?o._.arrVws={}:o.dataBoundOnly&&V("{^{"+e+"}} tag must be data-bound")),m.tag=o,o.dataMap&&o.tagCtxs&&(m.map=o.tagCtxs[f].map),o.flow||(h=m.ctx=m.ctx||{},d=o.parents=h.parentTags=T&&J(h.parentTags,T.parentTags)||{},c&&(d[c.tagName]=c),d[o.tagName]=h.tag=o);if(($||A)&&(t._.tag=o),!(o._er=s)){for(i(o,r[0]),o.rendering={},f=0;g>f;f++)m=o.tagCtx=o.tagCtxs[f],k=m.props,y=o.cvtArgs(),(b=k.dataMap||o.dataMap)&&(y.length||k.dataMap)&&(_=m.map,(!_||_.src!==y[0]||a)&&(_&&_.src&&_.unmap(),_=m.map=b.map(y[0],k)),y=[_.tgt]),o.ctx=m.ctx,f||(x&&(C=o.template,o.init(m,A,o.ctx),x=void 0,o.template!==C&&(o._.tmpl=o.template)),A&&(A.attr=o.attr=A.attr||o.attr),u=o.attr,o._.noVws=u&&u!==ht),v=void 0,o.render&&(v=o.render.apply(o,y)),y.length||(y=[t]),void 0===v&&(v=m.render(y.length?y[0]:t,!0)||(a?void 0:"")),j=j?j+(v||""):v;o.rendering=void 0}return o.tagCtx=o.tagCtxs[0],o.ctx=o.tagCtx.ctx,o._.noVws&&o._.inline&&(j="text"===u?Rt.html(j):""),$&&t._.onRender?t._.onRender(j,t,$):j}function b(e,t,n,r,i,a,s,o){var l,p,d,u,c=this,g="array"===t;c.content=s,c.views=g?[]:{},c.parent=n,c.type=t||"top",c.data=r,c.tmpl=i,u=c._={key:0,useKey:g?0:1,id:""+vt++,onRender:o,bnds:{}},c.linked=!!o,n?(l=n.views,p=n._,p.useKey?(l[u.key="_"+p.useKey++]=c,c.index=bt,c.getIndex=f,d=p.tag,u.bnd=g&&(!d||!!d._.bnd&&d)):l.length===(u.key=c.index=a)?l.push(c):l.splice(a,0,c),c.ctx=e||n.ctx):c.ctx=e}function _(e){var t,n,r,i,a,s,o;for(t in yt)if(a=yt[t],(s=a.compile)&&(n=e[t+"s"]))for(r in n)i=n[r]=s(r,n[r],e,0),i._is=t,i&&(o=$t.onStore[t])&&o(r,i,s)}function y(e,t,n){function i(){var t=this;t._={inline:!0,unlinked:!0},t.tagName=e}var a,s,o,l=new $t._tg;if(jt(t)?t={depends:t.depends,render:t}:""+t===t&&(t={template:t}),s=t.baseTag){t.flow=!!t.flow,t.baseTag=s=""+s===s?n&&n.tags[s]||Vt[s]:s,l=d(l,s);for(o in t)l[o]=r(s[o],t[o])}else l=d(l,t);return void 0!==(a=l.template)&&(l.template=""+a===a?Tt[a]||Tt(a):a),l.init!==!1&&((i.prototype=l).constructor=l._ctr=i),n&&(l._parentTmpl=n),l}function k(e){return this.base.apply(this,e)}function C(e,n,r,i){function a(n){var a;if(""+n===n||n.nodeType>0&&(s=n)){if(!s)if("@"===n.charAt(0))t?n=Tt[e=e||(n=t.realpathSync(n.slice(1)))]=Tt[e]||C(e,t.readFileSync(n,"utf8"),r,i):s=P.getElementById(n);else if(G.fn&&!H.test(n))try{s=G(P).find(n)[0]}catch(o){}s&&(i?n=s.innerHTML:((a=s.getAttribute(xt))&&(n=Tt[a])&&e!==a&&delete Tt[a],e=e||a||"_"+gt++,a||(n=C(e,s.innerHTML,r,i)),s.setAttribute(xt,e),Tt[n.tmplName=e]=n),s=void 0)}else n.fn||(n=void 0);return n}var s,o,l=n=n||"";return 0===i&&(i=void 0,l=a(l)),i=i||(n.markup?n:{}),i.tmplName=e,r&&(i._parentTmpl=r),!l&&n.markup&&(l=a(n.markup))&&l.fn&&(l=l.markup),void 0!==l?(l.fn||n.fn?l.fn&&(o=l):(n=A(l,i),N(l.replace(st,"\\$&"),n)),o||(_(i),o=d(function(){return n.render.apply(n,arguments)},n)),e&&!r&&(_t[e]=o),o):void 0}function j(e){function t(t,n){this.tgt=e.getTgt(t,n)}return jt(e)&&(e={getTgt:e}),e.baseMap&&(e=d(d({},e.baseMap),e)),e.map=function(e,n){return new t(e,n)},e}function A(e,t){var n,r=Nt.wrapMap||{},i=d({tmpls:[],links:{},bnds:[],_is:"template",render:R},t);return i.markup=e,t.htmlTag||(n=pt.exec(e),i.htmlTag=n?n[1].toLowerCase():""),n=r[i.htmlTag],n&&n!==r.div&&(i.markup=G.trim(i.markup)),i}function T(e,t){function n(i,a,s){var o,l,p,d;if(i&&typeof i===wt&&!i.nodeType&&!i.markup&&!i.getTgt){for(p in i)n(p,i[p],a);return kt}return void 0===a&&(a=i,i=void 0),i&&""+i!==i&&(s=a,a=i,i=void 0),d=s?s[r]=s[r]||{}:n,l=t.compile,null===a?i&&delete d[i]:(a=l?l(i,a,s,0):a,i&&(d[i]=a)),l&&a&&(a._is=e),a&&(o=$t.onStore[e])&&o(i,a,l),a}var r=e+"s";kt[r]=n}function R(e,t,n,r,i,a){var s,o,l,p,d,u,c,f,g=r,v="";if(t===!0?(n=t,t=void 0):typeof t!==wt&&(t=void 0),(l=this.tag)?(d=this,p=l._.tmpl||d.tmpl,g=g||d.view,arguments.length||(e=g)):p=this,p){if(!g&&e&&"view"===e._is&&(g=e),g&&e===g&&(e=g.data),p.fn||(p=l._.tmpl=Tt[p]||Tt(p)),Q=Q||(u=!g),g||((t=t||{}).root=e),!Q||p.useViews)v=M(p,e,t,n,g,i,a,l);else{if(g?(c=g.data,f=g.index,g.index=bt):(g=D,g.data=e,g.ctx=t),At(e)&&!n)for(s=0,o=e.length;o>s;s++)g.index=s,g.data=e[s],v+=p.fn(e[s],g,kt);else v+=p.fn(e,g,kt);g.data=c,g.index=f}u&&(Q=void 0)}return v}function M(e,t,n,r,i,a,s,o){function l(e){_=d({},n),_[x]=e}var p,u,c,f,g,v,m,h,w,x,_,y,k="";if(o&&(w=o.tagName,y=o.tagCtx,n=n?J(n,o.ctx):o.ctx,m=y.content,y.props.link===!1&&(n=n||{},n.link=!1),(x=y.props.itemVar)&&("~"!==x.charAt(0)&&$("Use itemVar='~myItem'"),x=x.slice(1))),i&&(m=m||i.content,s=s||i._.onRender,n=n||i.ctx),a===!0&&(v=!0,a=0),s&&(n&&n.link===!1||o&&o._.noVws)&&(s=void 0),h=s,s===!0&&(h=void 0,s=i._.onRender),n=e.helpers?J(e.helpers,n):n,_=n,At(t)&&!r)for(c=v?i:void 0!==a&&i||new b(n,"array",i,t,e,a,m,s),x&&(c.it=x),x=c.it,p=0,u=t.length;u>p;p++)x&&l(t[p]),f=new b(_,"item",c,t[p],e,(a||0)+p,m,s),g=e.fn(t[p],f,kt),k+=c._.onRender?c._.onRender(g,f):g;else x&&l(t),c=v?i:new b(_,w||"data",i,t,e,a,m,s),o&&!o.flow&&(c.tag=o),k+=e.fn(t,c,kt);return h?h(k,c):k}function V(e,t,n){var r=Nt.onError(e,t,n);if(""+e===e)throw new $t.Err(r);return!t.linkCtx&&t.linked?Rt.html(r):r}function $(e){V("Syntax error\n"+e)}function N(e,t,n,r,i){function a(t){t-=f,t&&v.push(e.substr(f,t).replace(it,"\\n"))}function s(t,n){t&&(t+="}}",$((n?"{{"+n+"}} block has {{/"+t+" without {{"+t:"Unmatched or missing {{/"+t)+", in template:\n"+e))}function o(o,l,c,h,w,x,b,_,y,k,C,j){x&&(w=":",h=ht),k=k||n&&!i;var A=(l||n)&&[[]],T="",R="",M="",V="",N="",E="",S="",U="",J=!k&&!w&&!b;c=c||(y=y||"#data",w),a(j),f=j+o.length,_?u&&v.push(["*","\n"+y.replace(/^:/,"ret+= ").replace(at,"$1")+";\n"]):c?("else"===c&&(lt.test(y)&&$('for "{{else if expr}}" use "{{else expr}}"'),A=m[7]&&[[]],m[8]=e.substring(m[8],j),m=g.pop(),v=m[2],J=!0),y&&I(y.replace(it," "),A,t).replace(ot,function(e,t,n,r,i,a,s,o){return r="'"+i+"':",s?(R+=a+",",V+="'"+o+"',"):n?(M+=r+a+",",E+=r+"'"+o+"',"):t?S+=a:("trigger"===i&&(U+=a),T+=r+a+",",N+=r+"'"+o+"',",d=d||ct.test(i)),""}).slice(0,-1),A&&A[0]&&A.pop(),p=[c,h||!!r||d||"",J&&[],F(V,N,E),F(R,T,M),S,U,A||0],v.push(p),J&&(g.push(m),m=p,m[8]=f)):C&&(s(C!==m[0]&&"else"!==m[0]&&C,m[0]),m[8]=e.substring(m[8],j),m=g.pop()),s(!m&&C),v=m[2]}var l,p,d,u=Nt.allowCode||t&&t.allowCode,c=[],f=0,g=[],v=c,m=[,,c];return u&&(t.allowCode=u),n&&(e=W+e+et),s(g[0]&&g[0][2].pop()[0]),e.replace(q,o),a(e.length),(f=c[c.length-1])&&s(""+f!==f&&+f[8]===f[8]&&f[0]),n?(l=U(c,e,n),E(l,[c[0][7]])):l=U(c,t),l}function E(e,t){var n,r,i=0,a=t.length;for(e.deps=[];a>i;i++){r=t[i];for(n in r)"_jsvto"!==n&&r[n].length&&(e.deps=e.deps.concat(r[n]))}e.paths=r}function F(e,t,n){return[e.slice(0,-1),t.slice(0,-1),n.slice(0,-1)]}function S(e,t){return"\n	"+(t?t+":{":"")+"args:["+e[0]+"]"+(e[1]||!t?",\n	props:{"+e[1]+"}":"")+(e[2]?",\n	ctx:{"+e[2]+"}":"")}function I(e,t,n){function r(r,h,w,x,b,_,y,k,C,j,A,T,R,M,V,E,F,S,I,U){function J(e,n,r,s,o,l,u,c){var f="."===r;if(r&&(b=b.slice(n.length),f||(e=(s?'view.hlp("'+s+'")':o?"view":"data")+(c?(l?"."+l:s?"":o?"":"."+r)+(u||""):(c=s?"":o?l||"":r,"")),e+=c?"."+c:"",e=n+("view.data"===e.slice(0,9)?e.slice(5):e)),p)){if(B="linkTo"===i?a=t._jsvto=t._jsvto||[]:d.bd,L=f&&B[B.length-1]){if(L._jsv){for(;L.sb;)L=L.sb;L.bnd&&(b="^"+b.slice(1)),L.sb=b,L.bnd=L.bnd||"^"===b.charAt(0)}}else B.push(b);m[g]=I+(f?1:0)}return e}x=p&&x,x&&!k&&(b=x+b),_=_||"",w=w||h||T,b=b||C,j=j||F||"";var K,O,B,L,q;if(!y||l||o){if(p&&E&&!l&&!o&&(!i||s||a)&&(K=m[g-1],U.length-1>I-(K||0))){if(K=U.slice(K,I+r.length),O!==!0)if(B=a||u[g-1].bd,L=B[B.length-1],L&&L.prm){for(;L.sb&&L.sb.prm;)L=L.sb;q=L.sb={path:L.sb,bnd:L.bnd}}else B.push(q={path:B.pop()});E=X+":"+K+" onerror=''"+Y,O=f[E],O||(f[E]=!0,f[E]=O=N(E,n,!0)),O!==!0&&q&&(q._jsv=O,q.prm=d.bd,q.bnd=q.bnd||q.path&&q.path.indexOf("^")>=0)}return l?(l=!R,l?r:T+'"'):o?(o=!M,o?r:T+'"'):(w?(m[g]=I++,d=u[++g]={bd:[]},w):"")+(S?g?"":(c=U.slice(c,I),(i?(i=s=a=!1,"\b"):"\b,")+c+(c=I+r.length,p&&t.push(d.bd=[]),"\b")):k?(g&&$(e),p&&t.pop(),i=b,s=x,c=I+r.length,x&&(p=d.bd=t[i]=[]),b+":"):b?b.split("^").join(".").replace(nt,J)+(j?(d=u[++g]={bd:[]},v[g]=!0,j):_):_?_:V?(v[g]=!1,d=u[--g],V+(j?(d=u[++g],v[g]=!0,j):"")):A?(v[g]||$(e),","):h?"":(l=R,o=M,'"'))}$(e)}var i,a,s,o,l,p=t&&t[0],d={bd:p},u={0:d},c=0,f=n?n.links:p&&(p.links=p.links||{}),g=0,v={},m={};return(e+(n?" ":"")).replace(rt,r)}function U(e,t,n){var r,i,a,s,o,l,p,d,u,c,f,g,v,m,h,w,x,b,_,y,k,C,j,T,R,M,V,N,F,I,J=0,K=t.useViews||t.tags||t.templates||t.helpers||t.converters,O="",B={},L=e.length;for(""+t===t?(b=n?'data-link="'+t.replace(it," ").slice(1,-1)+'"':t,t=0):(b=t.tmplName||"unnamed",t.allowCode&&(B.allowCode=!0),t.debug&&(B.debug=!0),f=t.bnds,x=t.tmpls),r=0;L>r;r++)if(i=e[r],""+i===i)O+='\n+"'+i+'"';else if(a=i[0],"*"===a)O+=";\n"+i[1]+"\nret=ret";else{if(s=i[1],k=!n&&i[2],o=S(i[3],"params")+"},"+S(v=i[4]),N=i[5],I=i[6],C=i[8]&&i[8].replace(at,"$1"),(R="else"===a)?g&&g.push(i[7]):(J=0,f&&(g=i[7])&&(g=[g],J=f.push(1))),K=K||v[1]||v[2]||g||/view.(?!index)/.test(v[0]),(M=":"===a)?s&&(a=s===ht?">":s+a):(k&&(_=A(C,B),_.tmplName=b+"/"+a,_.useViews=_.useViews||K,U(k,_),K=_.useViews,x.push(_)),R||(y=a,K=K||a&&(!Vt[a]||!Vt[a].flow),T=O,O=""),j=e[r+1],j=j&&"else"===j[0]),F=N?";\ntry{\nret+=":"\n+",m="",h="",M&&(g||I||s&&s!==ht)){if(V="return {"+o+"};",w='c("'+s+'",view,',V=new Function("data,view,j,u"," // "+b+" "+J+" "+a+"\n"+V),V._er=N,m=w+J+",",h=")",V._tag=a,n)return V;E(V,g),c=!0}if(O+=M?(n?(N?"\ntry{\n":"")+"return ":F)+(c?(c=void 0,K=u=!0,w+(g?(f[J-1]=V,J):"{"+o+"}")+")"):">"===a?(p=!0,"h("+v[0]+")"):(d=!0,"((v="+(v[0]||"data")+')!=null?v:"")')):(l=!0,"\n{view:view,tmpl:"+(k?x.length:"0")+","+o+"},"),y&&!j){if(O="["+O.slice(0,-1)+"]",w='t("'+y+'",view,this,',n||g){if(O=new Function("data,view,j,u"," // "+b+" "+J+" "+y+"\nreturn "+O+";"),O._er=N,O._tag=y,g&&E(f[J-1]=O,g),n)return O;m=w+J+",undefined,",h=")"}O=T+F+w+(J||O)+")",g=0,y=0}N&&(K=!0,O+=";\n}catch(e){ret"+(n?"urn ":"+=")+m+"j._err(e,view,"+N+")"+h+";}\n"+(n?"":"ret=ret"))}O="// "+b+"\nvar v"+(l?",t=j._tag":"")+(u?",c=j._cnvt":"")+(p?",h=j.converters.html":"")+(n?";\n":',ret=""\n')+(B.debug?"debugger;":"")+O+(n?"\n":";\nreturn ret;"),Nt._dbgMode&&(O="try {\n"+O+"\n}catch(e){\nreturn j._err(e, view);\n}");try{O=new Function("data,view,j,u",O)}catch(q){$("Compiled template code:\n\n"+O+'\n: "'+q.message+'"')}return t&&(t.fn=O,t.useViews=!!K),O}function J(e,t){return e&&e!==t?t?d(d({},t),e):e:t&&d({},t)}function K(e){return mt[e]||(mt[e]="&#"+e.charCodeAt(0)+";")}function O(e){var t,n,r=[];if(typeof e===wt)for(t in e)n=e[t],n&&n.toJSON&&!n.toJSON()||jt(n)||r.push({key:t,prop:n});return r}function B(e){return void 0!=e?ut.test(e)&&(""+e).replace(ft,K)||e:""}e=e===!0;var L,q,H,D,Q,Z="v1.0.0-beta",z=(0,eval)("this"),G=z.jQuery,P=z.document,W="{",X="{",Y="}",et="}",tt="^",nt=/^(!*?)(?:null|true|false|\d[\d.]*|([\w$]+|\.|~([\w$]+)|#(view|([\w$]+))?)([\w$.^]*?)(?:[.[^]([\w$]+)\]?)?)$/g,rt=/(\()(?=\s*\()|(?:([([])\s*)?(?:(\^?)(!*?[#~]?[\w$.^]+)?\s*((\+\+|--)|\+|-|&&|\|\||===|!==|==|!=|<=|>=|[<>%*:?\/]|(=))\s*|(!*?[#~]?[\w$.^]+)([([])?)|(,\s*)|(\(?)\\?(?:(')|("))|(?:\s*(([)\]])(?=\s*[.^]|\s*$|[^\(\[])|[)\]])([([]?))|(\s+)/g,it=/[ \t]*(\r\n|\n|\r)/g,at=/\\(['"])/g,st=/['"\\]/g,ot=/(?:\x08|^)(onerror:)?(?:(~?)(([\w$_\.]+):)?([^\x08]+))\x08(,)?([^\x08]+)/gi,lt=/^if\s/,pt=/<(\w+)[>\s]/,dt=/[\x00`><"'&]/g,ut=/[\x00`><\"'&]/,ct=/^on[A-Z]|^convert(Back)?$/,ft=dt,gt=0,vt=0,mt={"&":"&amp;","<":"&lt;",">":"&gt;","\x00":"&#0;","'":"&#39;",'"':"&#34;","`":"&#96;"},ht="html",wt="object",xt="data-jsv-tmpl",bt="For #index in nested block use #getIndex().",_t={},yt={template:{compile:C},tag:{compile:y},helper:{},converter:{}},kt={jsviews:Z,settings:function(e){d(Nt,e),l(Nt._dbgMode),Nt.jsv&&Nt.jsv()},sub:{View:b,Err:p,tmplFn:N,parse:I,extend:d,syntaxErr:$,onStore:{},_ths:i,_tg:function(){}},map:j,_cnvt:m,_tag:x,_err:V},Ct=z.jsviews;(p.prototype=new Error).constructor=p,f.depends=function(){return[this.get("item"),"index"]},g.depends="index",b.prototype={get:c,getIndex:g,getRsc:w,hlp:v,_is:"view"};for(L in yt)T(L,yt[L]);var jt,At,Tt=kt.templates,Rt=kt.converters,Mt=kt.helpers,Vt=kt.tags,$t=kt.sub,Nt=kt.settings;return $t._tg.prototype={baseApply:k,cvtArgs:h},D=$t.topView=new b,G?(G.fn.render=function(e,t,n){var r=this.jquery&&(this[0]||V('Unknown template: "'+this.selector+'"')),i=r.getAttribute(xt);return R.call(i?Tt[i]:Tt(r),e,t,n)},G.observable&&(d($t,G.views.sub),kt.map=G.views.map)):(G={},e||(z.jsviews=G),G.isFunction=function(e){return"function"==typeof e},G.isArray=Array.isArray||function(e){return"[object Array]"===G.toString.call(e)},G.noConflict=function(){return z.jsviews===G&&(z.jsviews=Ct),G}),jt=G.isFunction,At=G.isArray,G.render=_t,G.views=kt,G.templates=Tt=kt.templates,kt.compile=function(e,t){return t=t||{},t.markup=e,Tt(t)},Nt({debugMode:l,delimiters:u,onError:function(e,t,n){return t&&(e=void 0===n?"{Error: "+(e.message||e)+"}":jt(n)?n(e,t):n),void 0==e?"":e},_dbgMode:!1}),Vt({"if":{render:function(e){var t=this,n=t.tagCtx,r=t.rendering.done||!e&&(arguments.length||!n.index)?"":(t.rendering.done=!0,t.selected=n.index,n.render(n.view,!0));return r},flow:!0},"for":{render:function(e){var t,n=!arguments.length,r=this,i=r.tagCtx,a="",s=0;return r.rendering.done||(t=n?i.view.data:e,void 0!==t&&(a+=i.render(t,n),s+=At(t)?t.length:1),(r.rendering.done=s)&&(r.selected=i.index)),a},flow:!0},props:{baseTag:"for",dataMap:j(O),flow:!0},include:{flow:!0},"*":{render:a,flow:!0},":*":{render:a,flow:!0},dbg:Mt.dbg=Rt.dbg=o}),Rt({html:B,attr:B,url:function(e){return void 0!=e?encodeURI(""+e):null===e?e:""}}),u(),kt});
=======
/*! JsRender v1.0.0-rc.70 (Beta - Release Candidate): http://jsviews.com/#jsrender */
/*! **VERSION FOR WEB** (For NODE.JS see http://jsviews.com/download/jsrender-node.js) */
!function(e){var t=(0,eval)("this"),n=t.jQuery;"function"==typeof define&&define.amd?define('jsrender',e):"object"==typeof exports?module.exports=n?e(n):function(t){if(t&&!t.fn)throw"Provide jQuery or null";return e(t)}:e(!1)}(function(e){"use strict";function t(e,t){return function(){var n,r=this,i=r.base;return r.base=e,n=t.apply(r,arguments),r.base=i,n}}function n(e,n){return z(n)&&(n=t(e?e._d?e:t(a,e):a,n),n._d=1),n}function r(e,t){for(var r in t.props)xe.test(r)&&(e[r]=n(e[r],t.props[r]))}function i(e){return e}function a(){return""}function s(e){try{throw"dbg breakpoint"}catch(t){}return this.base?this.baseApply(arguments):e}function o(e){ne._dbgMode=e!==!1}function d(t){this.name=(e.link?"JsViews":"JsRender")+" Error",this.message=t||this.name}function p(e,t){var n;for(n in t)e[n]=t[n];return e}function l(e,t,n){return(0!==this||e)&&(ae=e?e.charAt(0):ae,se=e?e.charAt(1):se,oe=t?t.charAt(0):oe,de=t?t.charAt(1):de,pe=n||pe,e="\\"+ae+"(\\"+pe+")?\\"+se,t="\\"+oe+"\\"+de,H="(?:(?:(\\w+(?=[\\/\\s\\"+oe+"]))|(?:(\\w+)?(:)|(>)|!--((?:[^-]|-(?!-))*)--|(\\*)))\\s*((?:[^\\"+oe+"]|\\"+oe+"(?!\\"+de+"))*?)",te.rTag=H+")",H=new RegExp(e+H+"(\\/)?|(?:\\/(\\w+)))"+t,"g"),D=new RegExp("<.*>|([^\\\\]|^)[{}]|"+e+".*"+t)),[ae,se,oe,de,pe]}function u(e,t){t||(t=e,e=void 0);var n,r,i,a,s=this,o=!t||"root"===t;if(e){if(a=s.type===t?s:void 0,!a)if(n=s.views,s._.useKey){for(r in n)if(a=n[r].get(e,t))break}else for(r=0,i=n.length;!a&&i>r;r++)a=n[r].get(e,t)}else if(o)for(;s.parent.parent;)a=s=s.parent;else for(;s&&!a;)a=s.type===t?s:void 0,s=s.parent;return a}function c(){var e=this.get("item");return e?e.index:void 0}function f(){return this.index}function g(e){var t,n=this,r=n.linkCtx,i=(n.ctx||{})[e];return void 0===i&&r&&r.ctx&&(i=r.ctx[e]),void 0===i&&(i=Y[e]),i&&z(i)&&!i._wrp&&(t=function(){return i.apply(this&&this!==B?this:n,arguments)},t._wrp=!0,p(t,i)),t||i}function v(e,t,n,i){var a,s,o="number"==typeof n&&t.tmpl.bnds[n-1],d=t.linkCtx;return void 0!==i?n=i={props:{},args:[i]}:o&&(n=o(t.data,t,Z)),s=n.args[0],(e||o)&&(a=d&&d.tag,a||(a=p(new te._tg,{_:{inline:!d,bnd:o,unlinked:!0},tagName:":",cvt:e,flow:!0,tagCtx:n}),d&&(d.tag=a,a.linkCtx=d),n.ctx=U(n.ctx,(d?d.view:t).ctx)),a._er=i&&s,r(a,n),n.view=t,a.ctx=n.ctx||{},n.ctx=void 0,t._.tag=a,s=a.cvtArgs(a.convert||"true"!==e&&e)[0],s=o&&t._.onRender?t._.onRender(s,t,o):s,t._.tag=void 0),void 0!=s?s:""}function m(e){var t=this,n=t.tagCtx,r=n.view,i=n.args;return e=t.convert||e,e=e&&(""+e===e?r.getRsc("converters",e)||V("Unknown converter: '"+e+"'"):e),i=i.length||n.index?e?i.slice():i:[r.data],e&&(e.depends&&(t.depends=te.getDeps(t.depends,t,e.depends,e)),i[0]=e.apply(t,i)),i}function h(e,t){for(var n,r,i=this;void 0===n&&i;)r=i.tmpl&&i.tmpl[e],n=r&&r[t],i=i.parent;return n||Z[e][t]}function w(e,t,n,i,a,s){t=t||P;var o,d,p,l,u,c,f,g,v,m,h,w,b,x,_,y,k,j,C,A="",R=t.linkCtx||0,M=t.ctx,$=n||t.tmpl,N="number"==typeof i&&t.tmpl.bnds[i-1];for("tag"===e._is?(o=e,e=o.tagName,i=o.tagCtxs,p=o.template):(d=t.getRsc("tags",e)||V("Unknown tag: {{"+e+"}} "),p=d.template),void 0!==s?(A+=s,i=s=[{props:{},args:[]}]):N&&(i=N(t.data,t,Z)),g=i.length,f=0;g>f;f++)m=i[f],(!R||!R.tag||f&&!R.tag._.inline||o._er)&&((w=m.tmpl)&&(w=m.content=$.tmpls[w-1]),m.index=f,m.tmpl=p||w,m.render=T,m.view=t,m.ctx=U(m.ctx,M)),(n=m.props.tmpl)&&(n=""+n===n?t.getRsc("templates",n)||W(n):n,m.tmpl=n),o||(o=new d._ctr,b=!!o.init,o.parent=c=M&&M.tag,o.tagCtxs=i,C=o.dataMap,R&&(o._.inline=!1,R.tag=o,o.linkCtx=R),(o._.bnd=N||R.fn)?o._.arrVws={}:o.dataBoundOnly&&V("{^{"+e+"}} tag must be data-bound")),i=o.tagCtxs,C=o.dataMap,m.tag=o,C&&i&&(m.map=i[f].map),o.flow||(h=m.ctx=m.ctx||{},l=o.parents=h.parentTags=M&&U(h.parentTags,M.parentTags)||{},c&&(l[c.tagName]=c),l[o.tagName]=h.tag=o);if((N||R)&&(t._.tag=o),!(o._er=s)){for(r(o,i[0]),o.rendering={},f=0;g>f;f++)m=o.tagCtx=i[f],k=m.props,y=o.cvtArgs(),(x=k.dataMap||C)&&(y.length||k.dataMap)&&(_=m.map,(!_||_.src!==y[0]||a)&&(_&&_.src&&_.unmap(),_=m.map=x.map(y[0],k,void 0,!o._.bnd)),y=[_.tgt]),o.ctx=m.ctx,f||(b&&(j=o.template,o.init(m,R,o.ctx),b=void 0,o.template!==j&&(o._.tmpl=o.template)),R&&(R.attr=o.attr=R.attr||o.attr),u=o.attr,o._.noVws=u&&u!==je),v=void 0,o.render&&(v=o.render.apply(o,y)),y.length||(y=[t]),void 0===v&&(v=m.render(y.length?y[0]:t,!0)||(a?void 0:"")),A=A?A+(v||""):v;o.rendering=void 0}return o.tagCtx=i[0],o.ctx=o.tagCtx.ctx,o._.noVws&&o._.inline&&(A="text"===u?X.html(A):""),N&&t._.onRender?t._.onRender(A,t,N):A}function b(e,t,n,r,i,a,s,o){var d,p,l,u,f=this,g="array"===t;f.content=s,f.views=g?[]:{},f.parent=n,f.type=t||"top",f.data=r,f.tmpl=i,u=f._={key:0,useKey:g?0:1,id:""+ye++,onRender:o,bnds:{}},f.linked=!!o,n?(d=n.views,p=n._,p.useKey?(d[u.key="_"+p.useKey++]=f,f.index=Re,f.getIndex=c,l=p.tag,u.bnd=g&&(!l||!!l._.bnd&&l)):d.length===(u.key=f.index=a)?d.push(f):d.splice(a,0,f),f.ctx=e||n.ctx):f.ctx=e}function x(e){var t,n,r,i,a,s,o;for(t in Ne)if(a=Ne[t],(s=a.compile)&&(n=e[t+"s"]))for(r in n)i=n[r]=s(r,n[r],e,0),i._is=t,i&&(o=te.onStore[t])&&o(r,i,s)}function _(e,t,r){function i(){var t=this;t._={inline:!0,unlinked:!0},t.tagName=e}var a,s,o,d=new te._tg;if(z(t)?t={depends:t.depends,render:t}:""+t===t&&(t={template:t}),s=t.baseTag){t.flow=!!t.flow,t.baseTag=s=""+s===s?r&&r.tags[s]||ee[s]:s,d=p(d,s);for(o in t)d[o]=n(s[o],t[o])}else d=p(d,t);return void 0!==(a=d.template)&&(d.template=""+a===a?W[a]||W(a):a),d.init!==!1&&((i.prototype=d).constructor=d._ctr=i),r&&(d._parentTmpl=r),d}function y(e){return this.base.apply(this,e)}function k(t,n,r,i){function a(n){var a,o;if(""+n===n||n.nodeType>0&&(s=n)){if(!s)if(/^\.\/[^\\:*?"<>]*$/.test(n))(o=W[t=t||n])?n=o:s=document.getElementById(n);else if(e.fn&&!D.test(n))try{s=e(document).find(n)[0]}catch(d){}s&&(i?n=s.innerHTML:(a=s.getAttribute(Ae),a?a!==Te?(n=W[a],delete W[a]):e.fn&&(n=e.data(s)[Te]):(t=t||(e.fn?Te:n),n=k(t,s.innerHTML,r,i)),n.tmplName=t=t||a,t!==Te&&(W[t]=n),s.setAttribute(Ae,t),e.fn&&e.data(s,Te,n))),s=void 0}else n.fn||(n=void 0);return n}var s,o,d=n=n||"";return 0===i&&(i=void 0,d=a(d)),i=i||(n.markup?n:{}),i.tmplName=t,r&&(i._parentTmpl=r),!d&&n.markup&&(d=a(n.markup))&&d.fn&&(d=d.markup),void 0!==d?(d.fn||n.fn?d.fn&&(o=d):(n=C(d,i),$(d.replace(ge,"\\$&"),n)),o||(x(i),o=p(function(){return n.render.apply(n,arguments)},n)),t&&!r&&t!==Te&&(Ve[t]=o),o):void 0}function j(e){function t(t,n){this.tgt=e.getTgt(t,n)}return z(e)&&(e={getTgt:e}),e.baseMap&&(e=p(p({},e.baseMap),e)),e.map=function(e,n){return new t(e,n)},e}function C(t,n){var r,i=ne.wrapMap||{},a=p({tmpls:[],links:{},bnds:[],_is:"template",render:T},n);return a.markup=t,n.htmlTag||(r=he.exec(t),a.htmlTag=r?r[1].toLowerCase():""),r=i[a.htmlTag],r&&r!==i.div&&(a.markup=e.trim(a.markup)),a}function A(e,t){function n(i,a,s){var o,d,p,l;if(i&&typeof i===Ce&&!i.nodeType&&!i.markup&&!i.getTgt){for(p in i)n(p,i[p],a);return Z}return void 0===a&&(a=i,i=void 0),i&&""+i!==i&&(s=a,a=i,i=void 0),l=s?s[r]=s[r]||{}:n,d=t.compile,null===a?i&&delete l[i]:(a=d?d(i,a,s,0):a,i&&(l[i]=a)),d&&a&&(a._is=e),a&&(o=te.onStore[e])&&o(i,a,d),a}var r=e+"s";Z[r]=n}function T(e,t,n,r,i,a){var s,o,d,p,l,u,c,f,g=r,v="";if(t===!0?(n=t,t=void 0):typeof t!==Ce&&(t=void 0),(d=this.tag)?(l=this,p=d._.tmpl||l.tmpl,g=g||l.view,arguments.length||(e=g)):p=this,p){if(!g&&e&&"view"===e._is&&(g=e),g&&e===g&&(e=g.data),p.fn||(p=d._.tmpl=W[p]||W(p)),u=!g,re=re||u,g||((t=t||{}).root=e),!re||ne.useViews||p.useViews||g&&g!==P)v=R(p,e,t,n,g,i,a,d);else{if(g?(c=g.data,f=g.index,g.index=Re):(g=P,g.data=e,g.ctx=t),G(e)&&!n)for(s=0,o=e.length;o>s;s++)g.index=s,g.data=e[s],v+=p.fn(e[s],g,Z);else v+=p.fn(e,g,Z);g.data=c,g.index=f}u&&(re=void 0)}return v}function R(e,t,n,r,i,a,s,o){function d(e){_=p({},n),_[x]=e}var l,u,c,f,g,v,m,h,w,x,_,y,k="";if(o&&(w=o.tagName,y=o.tagCtx,n=n?U(n,o.ctx):o.ctx,m=y.content,y.props.link===!1&&(n=n||{},n.link=!1),(x=y.props.itemVar)&&("~"!==x.charAt(0)&&M("Use itemVar='~myItem'"),x=x.slice(1))),i&&(m=m||i.content,s=s||i._.onRender,n=U(n,i.ctx)),a===!0&&(v=!0,a=0),s&&(n&&n.link===!1||o&&o._.noVws)&&(s=void 0),h=s,s===!0&&(h=void 0,s=i._.onRender),n=e.helpers?U(e.helpers,n):n,_=n,G(t)&&!r)for(c=v?i:void 0!==a&&i||new b(n,"array",i,t,e,a,m,s),x&&(c.it=x),x=c.it,l=0,u=t.length;u>l;l++)x&&d(t[l]),f=new b(_,"item",c,t[l],e,(a||0)+l,m,s),g=e.fn(t[l],f,Z),k+=c._.onRender?c._.onRender(g,f):g;else x&&d(t),c=v?i:new b(_,w||"data",i,t,e,a,m,s),o&&!o.flow&&(c.tag=o),k+=e.fn(t,c,Z);return h?h(k,c):k}function V(e,t,n){var r=ne.onError(e,t,n);if(""+e===e)throw new te.Err(r);return!t.linkCtx&&t.linked?X.html(r):r}function M(e){V("Syntax error\n"+e)}function $(e,t,n,r,i){function a(t){t-=f,t&&v.push(e.substr(f,t).replace(ce,"\\n"))}function s(t,n){t&&(t+="}}",M((n?"{{"+n+"}} block has {{/"+t+" without {{"+t:"Unmatched or missing {{/"+t)+", in template:\n"+e))}function o(o,d,c,h,w,b,x,_,y,k,j,C){b&&(w=":",h=je),k=k||n&&!i;var A=(d||n)&&[[]],T="",R="",V="",$="",N="",F="",I="",U="",J=!k&&!w&&!x;c=c||(y=y||"#data",w),a(C),f=C+o.length,_?u&&v.push(["*","\n"+y.replace(/^:/,"ret+= ").replace(fe,"$1")+";\n"]):c?("else"===c&&(me.test(y)&&M('for "{{else if expr}}" use "{{else expr}}"'),A=m[7]&&[[]],m[8]=e.substring(m[8],C),m=g.pop(),v=m[2],J=!0),y&&S(y.replace(ce," "),A,t).replace(ve,function(e,t,n,r,i,a,s,o){return r="'"+i+"':",s?(R+=a+",",$+="'"+o+"',"):n?(V+=r+a+",",F+=r+"'"+o+"',"):t?I+=a:("trigger"===i&&(U+=a),T+=r+a+",",N+=r+"'"+o+"',",l=l||xe.test(i)),""}).slice(0,-1),A&&A[0]&&A.pop(),p=[c,h||!!r||l||"",J&&[],E($,N,F),E(R,T,V),I,U,A||0],v.push(p),J&&(g.push(m),m=p,m[8]=f)):j&&(s(j!==m[0]&&"else"!==m[0]&&j,m[0]),m[8]=e.substring(m[8],C),m=g.pop()),s(!m&&j),v=m[2]}var d,p,l,u=ne.allowCode||t&&t.allowCode,c=[],f=0,g=[],v=c,m=[,,c];return u&&(t.allowCode=u),n&&(e=ae+e+de),s(g[0]&&g[0][2].pop()[0]),e.replace(H,o),a(e.length),(f=c[c.length-1])&&s(""+f!==f&&+f[8]===f[8]&&f[0]),n?(d=I(c,e,n),N(d,[c[0][7]])):d=I(c,t),d}function N(e,t){var n,r,i=0,a=t.length;for(e.deps=[];a>i;i++){r=t[i];for(n in r)"_jsvto"!==n&&r[n].length&&(e.deps=e.deps.concat(r[n]))}e.paths=r}function E(e,t,n){return[e.slice(0,-1),t.slice(0,-1),n.slice(0,-1)]}function F(e,t){return"\n	"+(t?t+":{":"")+"args:["+e[0]+"]"+(e[1]||!t?",\n	props:{"+e[1]+"}":"")+(e[2]?",\n	ctx:{"+e[2]+"}":"")}function S(e,t,n){function r(r,h,w,b,x,_,y,k,j,C,A,T,R,V,N,E,F,S,I,U){function J(e,n,r,s,o,d,u,c){var f="."===r;if(r&&(x=x.slice(n.length),f||(e=(s?'view.hlp("'+s+'")':o?"view":"data")+(c?(d?"."+d:s?"":o?"":"."+r)+(u||""):(c=s?"":o?d||"":r,"")),e+=c?"."+c:"",e=n+("view.data"===e.slice(0,9)?e.slice(5):e)),p)){if(q="linkTo"===i?a=t._jsvto=t._jsvto||[]:l.bd,B=f&&q[q.length-1]){if(B._jsv){for(;B.sb;)B=B.sb;B.bnd&&(x="^"+x.slice(1)),B.sb=x,B.bnd=B.bnd||"^"===x.charAt(0)}}else q.push(x);m[g]=I+(f?1:0)}return e}b=p&&b,b&&!k&&(x=b+x),_=_||"",w=w||h||T,x=x||j,C=C||F||"";var K,O,q,B,L;if(!y||d||o){if(p&&E&&!d&&!o&&(!i||s||a)&&(K=m[g-1],U.length-1>I-(K||0))){if(K=U.slice(K,I+r.length),O!==!0)if(q=a||u[g-1].bd,B=q[q.length-1],B&&B.prm){for(;B.sb&&B.sb.prm;)B=B.sb;L=B.sb={path:B.sb,bnd:B.bnd}}else q.push(L={path:q.pop()});E=se+":"+K+" onerror=''"+oe,O=f[E],O||(f[E]=!0,f[E]=O=$(E,n,!0)),O!==!0&&L&&(L._jsv=O,L.prm=l.bd,L.bnd=L.bnd||L.path&&L.path.indexOf("^")>=0)}return d?(d=!R,d?r:T+'"'):o?(o=!V,o?r:T+'"'):(w?(m[g]=I++,l=u[++g]={bd:[]},w):"")+(S?g?"":(c=U.slice(c,I),(i?(i=s=a=!1,"\b"):"\b,")+c+(c=I+r.length,p&&t.push(l.bd=[]),"\b")):k?(g&&M(e),p&&t.pop(),i=x,s=b,c=I+r.length,b&&(p=l.bd=t[i]=[]),x+":"):x?x.split("^").join(".").replace(le,J)+(C?(l=u[++g]={bd:[]},v[g]=!0,C):_):_?_:N?(v[g]=!1,l=u[--g],N+(C?(l=u[++g],v[g]=!0,C):"")):A?(v[g]||M(e),","):h?"":(d=R,o=V,'"'))}M(e)}var i,a,s,o,d,p=t&&t[0],l={bd:p},u={0:l},c=0,f=n?n.links:p&&(p.links=p.links||{}),g=0,v={},m={},h=(e+(n?" ":"")).replace(ue,r);return!g&&h||M(e)}function I(e,t,n){var r,i,a,s,o,d,p,l,u,c,f,g,v,m,h,w,b,x,_,y,k,j,A,T,R,V,$,E,S,U,J=0,K=ne.useViews||t.useViews||t.tags||t.templates||t.helpers||t.converters,O="",q={},B=e.length;for(""+t===t?(x=n?'data-link="'+t.replace(ce," ").slice(1,-1)+'"':t,t=0):(x=t.tmplName||"unnamed",t.allowCode&&(q.allowCode=!0),t.debug&&(q.debug=!0),f=t.bnds,b=t.tmpls),r=0;B>r;r++)if(i=e[r],""+i===i)O+='\n+"'+i+'"';else if(a=i[0],"*"===a)O+=";\n"+i[1]+"\nret=ret";else{if(s=i[1],k=!n&&i[2],o=F(i[3],"params")+"},"+F(v=i[4]),E=i[5],U=i[6],j=i[8]&&i[8].replace(fe,"$1"),(R="else"===a)?g&&g.push(i[7]):(J=0,f&&(g=i[7])&&(g=[g],J=f.push(1))),K=K||v[1]||v[2]||g||/view.(?!index)/.test(v[0]),(V=":"===a)?s&&(a=s===je?">":s+a):(k&&(_=C(j,q),_.tmplName=x+"/"+a,_.useViews=_.useViews||K,I(k,_),K=_.useViews,b.push(_)),R||(y=a,K=K||a&&(!ee[a]||!ee[a].flow),T=O,O=""),A=e[r+1],A=A&&"else"===A[0]),S=E?";\ntry{\nret+=":"\n+",m="",h="",V&&(g||U||s&&s!==je)){if($="return {"+o+"};",w='c("'+s+'",view,',$=new Function("data,view,j,u"," // "+x+" "+J+" "+a+"\n"+$),$._er=E,m=w+J+",",h=")",$._tag=a,n)return $;N($,g),c=!0}if(O+=V?(n?(E?"\ntry{\n":"")+"return ":S)+(c?(c=void 0,K=u=!0,w+(g?(f[J-1]=$,J):"{"+o+"}")+")"):">"===a?(p=!0,"h("+v[0]+")"):(l=!0,"((v="+(v[0]||"data")+')!=null?v:"")')):(d=!0,"\n{view:view,tmpl:"+(k?b.length:"0")+","+o+"},"),y&&!A){if(O="["+O.slice(0,-1)+"]",w='t("'+y+'",view,this,',n||g){if(O=new Function("data,view,j,u"," // "+x+" "+J+" "+y+"\nreturn "+O+";"),O._er=E,O._tag=y,g&&N(f[J-1]=O,g),n)return O;m=w+J+",undefined,",h=")"}O=T+S+w+(J||O)+")",g=0,y=0}E&&(K=!0,O+=";\n}catch(e){ret"+(n?"urn ":"+=")+m+"j._err(e,view,"+E+")"+h+";}\n"+(n?"":"ret=ret"))}O="// "+x+"\nvar v"+(d?",t=j._tag":"")+(u?",c=j._cnvt":"")+(p?",h=j.converters.html":"")+(n?";\n":',ret=""\n')+(q.debug?"debugger;":"")+O+(n?"\n":";\nreturn ret;"),ne._dbgMode&&(O="try {\n"+O+"\n}catch(e){\nreturn j._err(e, view);\n}");try{O=new Function("data,view,j,u",O)}catch(L){M("Compiled template code:\n\n"+O+'\n: "'+L.message+'"')}return t&&(t.fn=O,t.useViews=!!K),O}function U(e,t){return e&&e!==t?t?p(p({},t),e):e:t&&p({},t)}function J(e){return ke[e]||(ke[e]="&#"+e.charCodeAt(0)+";")}function K(e){var t,n,r=[];if(typeof e===Ce)for(t in e)n=e[t],n&&n.toJSON&&!n.toJSON()||z(n)||r.push({key:t,prop:n});return r}function O(t,n,r){var i=this.jquery&&(this[0]||V('Unknown template: "'+this.selector+'"')),a=i.getAttribute(Ae);return T.call(a?e.data(i)[Te]:W(i),t,n,r)}function q(e){return void 0!=e?be.test(e)&&(""+e).replace(_e,J)||e:""}var B=(0,eval)("this"),L=e===!1;e=e&&e.fn?e:B.jQuery;var Q,H,D,P,Z,z,G,W,X,Y,ee,te,ne,re,ie="v1.0.0-beta",ae="{",se="{",oe="}",de="}",pe="^",le=/^(!*?)(?:null|true|false|\d[\d.]*|([\w$]+|\.|~([\w$]+)|#(view|([\w$]+))?)([\w$.^]*?)(?:[.[^]([\w$]+)\]?)?)$/g,ue=/(\()(?=\s*\()|(?:([([])\s*)?(?:(\^?)(!*?[#~]?[\w$.^]+)?\s*((\+\+|--)|\+|-|&&|\|\||===|!==|==|!=|<=|>=|[<>%*:?\/]|(=))\s*|(!*?[#~]?[\w$.^]+)([([])?)|(,\s*)|(\(?)\\?(?:(')|("))|(?:\s*(([)\]])(?=\s*[.^]|\s*$|[^\(\[])|[)\]])([([]?))|(\s+)/g,ce=/[ \t]*(\r\n|\n|\r)/g,fe=/\\(['"])/g,ge=/['"\\]/g,ve=/(?:\x08|^)(onerror:)?(?:(~?)(([\w$_\.]+):)?([^\x08]+))\x08(,)?([^\x08]+)/gi,me=/^if\s/,he=/<(\w+)[>\s]/,we=/[\x00`><"'&]/g,be=/[\x00`><\"'&]/,xe=/^on[A-Z]|^convert(Back)?$/,_e=we,ye=0,ke={"&":"&amp;","<":"&lt;",">":"&gt;","\x00":"&#0;","'":"&#39;",'"':"&#34;","`":"&#96;"},je="html",Ce="object",Ae="data-jsv-tmpl",Te="jsvTmpl",Re="For #index in nested block use #getIndex().",Ve={},Me=B.jsrender,$e=Me&&e&&!e.render,Ne={template:{compile:k},tag:{compile:_},helper:{},converter:{}};if(Z={jsviews:ie,settings:function(e){p(ne,e),o(ne._dbgMode),ne.jsv&&ne.jsv()},sub:{View:b,Err:d,tmplFn:$,parse:S,extend:p,extendCtx:U,syntaxErr:M,onStore:{},_ths:r,_tg:function(){}},map:j,_cnvt:v,_tag:w,_err:V},(d.prototype=new Error).constructor=d,c.depends=function(){return[this.get("item"),"index"]},f.depends="index",b.prototype={get:u,getIndex:f,getRsc:h,hlp:g,_is:"view"},!(Me||e&&e.render)){for(Q in Ne)A(Q,Ne[Q]);W=Z.templates,X=Z.converters,Y=Z.helpers,ee=Z.tags,te=Z.sub,ne=Z.settings,te._tg.prototype={baseApply:y,cvtArgs:m},P=te.topView=new b,e?(e.fn.render=O,e.observable&&(p(te,e.views.sub),Z.map=e.views.map)):(e={},L&&(B.jsrender=e),e.renderFile=e.__express=e.compile=function(){throw"Node.js: use npm jsrender, or jsrender-node.js"},e.isFunction=function(e){return"function"==typeof e},e.isArray=Array.isArray||function(e){return"[object Array]"==={}.toString.call(e)},te._jq=function(t){t!==e&&(p(t,e),e=t,e.fn.render=O,delete e.jsrender)},e.jsrender=ie),z=e.isFunction,G=e.isArray,e.render=Ve,e.views=Z,e.templates=W=Z.templates,ne({debugMode:o,delimiters:l,onError:function(e,t,n){return t&&(e=void 0===n?"{Error: "+(e.message||e)+"}":z(n)?n(e,t):n),void 0==e?"":e},_dbgMode:!1}),ee({"if":{render:function(e){var t=this,n=t.tagCtx,r=t.rendering.done||!e&&(arguments.length||!n.index)?"":(t.rendering.done=!0,t.selected=n.index,n.render(n.view,!0));return r},flow:!0},"for":{render:function(e){var t,n=!arguments.length,r=this,i=r.tagCtx,a="",s=0;return r.rendering.done||(t=n?i.view.data:e,void 0!==t&&(a+=i.render(t,n),s+=G(t)?t.length:1),(r.rendering.done=s)&&(r.selected=i.index)),a},flow:!0},props:{baseTag:"for",dataMap:j(K),flow:!0},include:{flow:!0},"*":{render:i,flow:!0},":*":{render:i,flow:!0},dbg:Y.dbg=X.dbg=s}),X({html:q,attr:q,url:function(e){return void 0!=e?encodeURI(""+e):null===e?e:""}}),l()}return $e&&Me.views.sub._jq(e),e||Me});
>>>>>>> Improve dragging behaviour.
//# sourceMappingURL=jsrender.min.js.map;
define('app/simplelayout/Element',["app/simplelayout/idHelper", "jsrender"], function(idHelper) {

  "use strict";

  function Element(template, represents) {

    this.template = $.templates(template);
    this.represents = represents;

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
      frame.show();
      return this;
    };

    this.disableFrame = function() {
      frame.hide();
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
      "app/helpers/template_range"
    ],
    function(
      Block,
      EventEmitter,
      transactional,
      Element) {

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

    this.attachTo = function(target) { $(target).append(this.element); };

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

    this.disable = function(action) { $("." + action, this.element).hide(); };

    this.enable = function(action) { $("." + action, this.element).show(); };

  };

  Element.call(Toolbar.prototype);

  return Toolbar;

});

define('app/toolbox/Toolbox',["app/simplelayout/Element", "jsrender"], function(Element) {

  "use strict";

  var Toolbox = function(options) {

    if (!(this instanceof Toolbox)) {
      throw new TypeError("Toolbox constructor cannot be called as a function.");
    }

    var template = $.templates(
      /*eslint no-multi-str: 0 */
      "<div id='sl-toolbox' class='sl-toolbox'> \
          <div class='components'> \
            <a class='sl-toolbox-header components'> \
              <i></i> \
            </a> \
              <div class='sl-toolbox-components'> \
                {{for components}} \
                  <a class='sl-toolbox-component {{:contentType}}' data-type='{{:contentType}}' data-form_url='{{:formUrl}}'> \
                    <i class='icon-{{:contentType}}'></i> \
                    <span class='description'>{{:title}}</span> \
                  </a> \
                {{/for}} \
              </div> \
              {{if canChangeLayout}} \
                <a class='sl-toolbox-header layouts'> \
                  <i></i> \
                </a> \
                <div class='sl-toolbox-layouts'> \
                  {{props layouts}} \
                    <a class='sl-toolbox-layout' data-columns='{{>prop}}'>{{>prop}} \
                      <span class='description'>{{>prop}} {{>#parent.parent.data.labels.labelColumnPostfix}}</span> \
                    </a> \
                  {{/props}} \
                </div> \
              {{/if}} \
          </div> \
          {{if canChangeLayout}} \
            <a class='sl-toolbox-header layouts'> \
              <i></i> \
            </a> \
            <div class='sl-toolbox-layouts'> \
              {{props layouts}} \
                <a class='sl-toolbox-layout' data-columns='{{>prop}}'>{{>prop}} \
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

    this.options = $.extend({
      toolbox: new Toolbox()
    }, options || {});

    this.managers = {};

    this.insertManager = function() {
      var manager = new Layoutmanager();
      this.managers[manager.id] = manager;
      return manager;
    };

    this.moveLayout = function(layout, target) {
      var source = layout.parent;
      source.deleteLayout(layout.id);
      target.layouts[layout.id] = layout;
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

    this.on = function(eventType, callback) {
      EventEmitter.on(eventType, callback);
      return this;
    };

    this.serialize = function() { return JSON.stringify(this.managers); };

    this.restore = function(source) {
      $(".sl-simplelayout", source).each(function() {
        self.insertManager().restore(this, $(this).attr("id"));
      });
      return this;
    };

    var sortableHelper = function() { return $('<div class="draggableHelper"><div>'); };

    var TOOLBOX_COMPONENT_DRAGGABLE_SETTINGS = {
      helper: "clone",
      cursor: "pointer",
      start: function() {
        self.enableFrames();
        if($(this).hasClass("sl-toolbox-block")) {
          root.addClass("sl-block-dragging");
        } else {
          root.addClass("sl-layout-dragging");
        }
      },
      stop: function() {
        self.disableFrames();
        root.removeClass("sl-block-dragging sl-layout-dragging");
      }
    };

    var LAYOUT_SORTABLE = {
      connectWith: ".sl-simplelayout",
      items: ".sl-layout",
      handle: ".sl-toolbar-layout .move",
      placeholder: "layout-placeholder",
      axis: "y",
      forcePlaceholderSize: true,
      helper: sortableHelper,
      receive: function(event, ui) {
        var layout;
        if($(ui.item).hasClass("sl-toolbox-layout")) {
          var item = $(this).find(".ui-draggable");
          layout = $(this).data().object.insertLayout(ui.item.data().columns);
          layout.element.insertAfter(item);
          item.remove();
        } else {
          self.moveLayout($(this).data().object, $(this).data().parent);
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
        self.disableFrames();
        root.removeClass("sl-layout-dragging");
      },
      stop: function() {
        self.disableFrames();
        root.removeClass("sl-layout-dragging");
      }
    };

    var BLOCK_SORTABLE = {
      connectWith: ".sl-column",
      placeholder: "block-placeholder",
      forcePlaceholderSize: true,
      handle: ".sl-toolbar-block .move",
      helper: sortableHelper,
<<<<<<< HEAD
      cursorAt: { left: 50, top: 50 },
=======
>>>>>>> Improve dragging behaviour.
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
      update: function(event, ui) {
        if(ui.item.parent()[0] === this && !ui.sender) {
          EventEmitter.trigger("blockMoved", [ui.item.data().object]);
        }
        self.disableFrames();
        root.removeClass("sl-block-dragging");
      },
      stop: function() {
        self.disableFrames();
        root.removeClass("sl-block-dragging");
      }
    };

    this.on("layout-committed", function(layout) {
      var layoutToolbar = new Toolbar(self.options.toolbox.options.layoutActions, "vertical", "layout");
      layout.attachToolbar(layoutToolbar);
      $(".sl-column", layout.element).sortable(BLOCK_SORTABLE);
    });

    this.on("block-committed", function(block) {
      if(self.options.toolbox.options.blocks[block.type]) {
        var blockToolbar = new Toolbar(self.options.toolbox.options.blocks[block.type].actions, "horizontal", "block");
        block.attachToolbar(blockToolbar);
      }
    });

    $(".sl-simplelayout").sortable(LAYOUT_SORTABLE);
    $(".sl-column").sortable(BLOCK_SORTABLE);

    this.options.toolbox.element.find(".sl-toolbox-block, .sl-toolbox-layout").draggable(TOOLBOX_COMPONENT_DRAGGABLE_SETTINGS);
    this.options.toolbox.element.find(".sl-toolbox-layout").draggable("option", "connectToSortable", ".sl-simplelayout");
    this.options.toolbox.element.find(".sl-toolbox-block").draggable("option", "connectToSortable", ".sl-column");

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

