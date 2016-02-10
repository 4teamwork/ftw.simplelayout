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

/*! JsRender v0.9.72 (Beta): http://jsviews.com/#jsrender */
/*! **VERSION FOR WEB** (For NODE.JS see http://jsviews.com/download/jsrender-node.js) */
!function(e){var t=(0,eval)("this"),n=t.jQuery;"function"==typeof define&&define.amd?define('jsrender',e):"object"==typeof exports?module.exports=n?e(n):function(t){if(t&&!t.fn)throw"Provide jQuery or null";return e(t)}:e(!1)}(function(e){"use strict";function t(e,t){return function(){var n,r=this,i=r.base;return r.base=e,n=t.apply(r,arguments),r.base=i,n}}function n(e,n){return G(n)&&(n=t(e?e._d?e:t(a,e):a,n),n._d=1),n}function r(e,t){for(var r in t.props)_e.test(r)&&(e[r]=n(e[r],t.props[r]))}function i(e){return e}function a(){return""}function s(e){try{throw"dbg breakpoint"}catch(t){}return this.base?this.baseApply(arguments):e}function o(e){re._dbgMode=e!==!1}function d(t){this.name=(e.link?"JsViews":"JsRender")+" Error",this.message=t||this.name}function p(e,t){var n;for(n in t)e[n]=t[n];return e}function l(e,t,n){return(0!==this||e)&&(se=e?e.charAt(0):se,oe=e?e.charAt(1):oe,de=t?t.charAt(0):de,pe=t?t.charAt(1):pe,le=n||le,e="\\"+se+"(\\"+le+")?\\"+oe,t="\\"+de+"\\"+pe,D="(?:(\\w+(?=[\\/\\s\\"+de+"]))|(\\w+)?(:)|(>)|(\\*))\\s*((?:[^\\"+de+"]|\\"+de+"(?!\\"+pe+"))*?)",ne.rTag="(?:"+D+")",D=new RegExp("(?:"+e+D+"(\\/)?|\\"+se+"\\"+oe+"(?:(?:\\/(\\w+))\\s*|!--[\\s\\S]*?--))"+t,"g"),P=new RegExp("<.*>|([^\\\\]|^)[{}]|"+e+".*"+t)),[se,oe,de,pe,le]}function u(e,t){t||e===!0||(t=e,e=void 0);var n,r,i,a,s=this,o=!t||"root"===t;if(e){if(a=t&&s.type===t&&s,!a)if(n=s.views,s._.useKey){for(r in n)if(a=t?n[r].get(e,t):n[r])break}else for(r=0,i=n.length;!a&&i>r;r++)a=t?n[r].get(e,t):n[r]}else if(o)for(;s.parent;)a=s,s=s.parent;else for(;s&&!a;)a=s.type===t?s:void 0,s=s.parent;return a}function c(){var e=this.get("item");return e?e.index:void 0}function f(){return this.index}function g(e){var t,n=this,r=n.linkCtx,i=(n.ctx||{})[e];return void 0===i&&r&&r.ctx&&(i=r.ctx[e]),void 0===i&&(i=ee[e]),i&&G(i)&&!i._wrp&&(t=function(){return i.apply(this&&this!==L?this:n,arguments)},t._wrp=n,p(t,i)),t||i}function v(e){return e&&(e.fn?e:this.getRsc("templates",e)||X(e))}function m(e,t,n,i){var a,s,o="number"==typeof n&&t.tmpl.bnds[n-1],d=t.linkCtx;return void 0!==i?n=i={props:{},args:[i]}:o&&(n=o(t.data,t,z)),s=n.args[0],(e||o)&&(a=d&&d.tag,a||(a=p(new ne._tg,{_:{inline:!d,bnd:o,unlinked:!0},tagName:":",cvt:e,flow:!0,tagCtx:n}),d&&(d.tag=a,a.linkCtx=d),n.ctx=K(n.ctx,(d?d.view:t).ctx)),a._er=i&&s,r(a,n),n.view=t,a.ctx=n.ctx||{},n.ctx=void 0,s=a.cvtArgs(a.convert||"true"!==e&&e)[0],s=o&&t._.onRender?t._.onRender(s,t,a):s),void 0!=s?s:""}function h(e){var t=this,n=t.tagCtx,r=n.view,i=n.args;return e=t.convert||e,e=e&&(""+e===e?r.getRsc("converters",e)||M("Unknown converter: '"+e+"'"):e),i=i.length||n.index?e?i.slice():i:[r.data],e&&(e.depends&&(t.depends=ne.getDeps(t.depends,t,e.depends,e)),i[0]=e.apply(t,i)),i}function w(e,t){for(var n,r,i=this;void 0===n&&i;)r=i.tmpl&&i.tmpl[e],n=r&&r[t],i=i.parent;return n||z[e][t]}function x(e,t,n,i,a,s){t=t||Z;var o,d,p,l,u,c,f,g,v,m,h,w,x,b,_,y,k,j,C,T="",A=t.linkCtx||0,V=t.ctx,$=n||t.tmpl,N="number"==typeof i&&t.tmpl.bnds[i-1];for("tag"===e._is?(o=e,e=o.tagName,i=o.tagCtxs,p=o.template):(d=t.getRsc("tags",e)||M("Unknown tag: {{"+e+"}} "),p=d.template),void 0!==s?(T+=s,i=s=[{props:{},args:[]}]):N&&(i=N(t.data,t,z)),g=i.length,f=0;g>f;f++)m=i[f],(!A||!A.tag||f&&!A.tag._.inline||o._er)&&((w=$.tmpls&&m.tmpl)&&(w=m.content=$.tmpls[w-1]),m.index=f,m.tmpl=w,m.render=R,m.view=t,m.ctx=K(m.ctx,V)),(n=m.props.tmpl)&&(m.tmpl=t.getTmpl(n)),o||(o=new d._ctr,x=!!o.init,o.parent=c=V&&V.tag,o.tagCtxs=i,C=o.dataMap,A&&(o._.inline=!1,A.tag=o,o.linkCtx=A),(o._.bnd=N||A.fn)?o._.arrVws={}:o.dataBoundOnly&&M("{^{"+e+"}} tag must be data-bound")),i=o.tagCtxs,C=o.dataMap,m.tag=o,C&&i&&(m.map=i[f].map),o.flow||(h=m.ctx=m.ctx||{},l=o.parents=h.parentTags=V&&K(h.parentTags,V.parentTags)||{},c&&(l[c.tagName]=c),l[o.tagName]=h.tag=o);if(!(o._er=s)){for(r(o,i[0]),o.rendering={},f=0;g>f;f++)m=o.tagCtx=i[f],k=m.props,y=o.cvtArgs(),(b=k.dataMap||C)&&(y.length||k.dataMap)&&(_=m.map,(!_||_.src!==y[0]||a)&&(_&&_.src&&_.unmap(),_=m.map=b.map(y[0],k,void 0,!o._.bnd)),y=[_.tgt]),o.ctx=m.ctx,f||(x&&(j=o.template,o.init(m,A,o.ctx),x=void 0),A&&(A.attr=o.attr=A.attr||o.attr),u=o.attr,o._.noVws=u&&u!==Ce),v=void 0,o.render&&(v=o.render.apply(o,y)),y.length||(y=[t]),void 0===v&&(v=m.render(y[0],!0)||(a?void 0:"")),T=T?T+(v||""):v;o.rendering=void 0}return o.tagCtx=i[0],o.ctx=o.tagCtx.ctx,o._.noVws&&o._.inline&&(T="text"===u?Y.html(T):""),N&&t._.onRender?t._.onRender(T,t,o):T}function b(e,t,n,r,i,a,s,o){var d,p,l,u=this,f="array"===t;u.content=o,u.views=f?[]:{},u.parent=n,u.type=t||"top",u.data=r,u.tmpl=i,l=u._={key:0,useKey:f?0:1,id:""+ke++,onRender:s,bnds:{}},u.linked=!!s,n?(d=n.views,p=n._,p.useKey?(d[l.key="_"+p.useKey++]=u,u.index=Ve,u.getIndex=c):d.length===(l.key=u.index=a)?d.push(u):d.splice(a,0,u),u.ctx=e||n.ctx):u.ctx=e}function _(e){var t,n,r,i,a,s,o;for(t in Ee)if(a=Ee[t],(s=a.compile)&&(n=e[t+"s"]))for(r in n)i=n[r]=s(r,n[r],e,0),i._is=t,i&&(o=ne.onStore[t])&&o(r,i,s)}function y(e,t,r){function i(){var t=this;t._={inline:!0,unlinked:!0},t.tagName=e}var a,s,o,d=new ne._tg;if(G(t)?t={depends:t.depends,render:t}:""+t===t&&(t={template:t}),s=t.baseTag){t.flow=!!t.flow,t.baseTag=s=""+s===s?r&&r.tags[s]||te[s]:s,d=p(d,s);for(o in t)d[o]=n(s[o],t[o])}else d=p(d,t);return void 0!==(a=d.template)&&(d.template=""+a===a?X[a]||X(a):a),d.init!==!1&&((i.prototype=d).constructor=d._ctr=i),r&&(d._parentTmpl=r),d}function k(e){return this.base.apply(this,e)}function j(t,n,r,i){function a(n){var a,o;if(""+n===n||n.nodeType>0&&(s=n)){if(!s)if(/^\.\/[^\\:*?"<>]*$/.test(n))(o=X[t=t||n])?n=o:s=document.getElementById(n);else if(e.fn&&!P.test(n))try{s=e(document).find(n)[0]}catch(d){}s&&(i?n=s.innerHTML:(a=s.getAttribute(Ae),a?a!==Re?(n=X[a],delete X[a]):e.fn&&(n=e.data(s)[Re]):(t=t||(e.fn?Re:n),n=j(t,s.innerHTML,r,i)),n.tmplName=t=t||a,t!==Re&&(X[t]=n),s.setAttribute(Ae,t),e.fn&&e.data(s,Re,n))),s=void 0}else n.fn||(n=void 0);return n}var s,o,d=n=n||"";return 0===i&&(i=void 0,d=a(d)),i=i||(n.markup?n:{}),i.tmplName=t,r&&(i._parentTmpl=r),!d&&n.markup&&(d=a(n.markup))&&d.fn&&(d=d.markup),void 0!==d?(d.fn||n.fn?d.fn&&(o=d):(n=T(d,i),N(d.replace(ve,"\\$&"),n)),o||(_(i),o=p(function(){return n.render.apply(n,arguments)},n)),t&&!r&&t!==Re&&(Me[t]=o),o):void 0}function C(e){function t(t,n){this.tgt=e.getTgt(t,n)}return G(e)&&(e={getTgt:e}),e.baseMap&&(e=p(p({},e.baseMap),e)),e.map=function(e,n){return new t(e,n)},e}function T(t,n){var r,i=re.wrapMap||{},a=p({tmpls:[],links:{},bnds:[],_is:"template",render:R},n);return a.markup=t,n.htmlTag||(r=we.exec(t),a.htmlTag=r?r[1].toLowerCase():""),r=i[a.htmlTag],r&&r!==i.div&&(a.markup=e.trim(a.markup)),a}function A(e,t){function n(i,a,s){var o,d,p,l;if(i&&typeof i===Te&&!i.nodeType&&!i.markup&&!i.getTgt){for(p in i)n(p,i[p],a);return z}return void 0===a&&(a=i,i=void 0),i&&""+i!==i&&(s=a,a=i,i=void 0),l=s?s[r]=s[r]||{}:n,d=t.compile,null===a?i&&delete l[i]:(a=d?d(i,a,s,0):a,i&&(l[i]=a)),d&&a&&(a._is=e),a&&(o=ne.onStore[e])&&o(i,a,d),a}var r=e+"s";z[r]=n}function R(e,t,n,r,i,a){var s,o,d,p,l,u,c,f,g=r,v="";if(t===!0?(n=t,t=void 0):typeof t!==Te&&(t=void 0),(d=this.tag)?(l=this,g=g||l.view,p=g.getTmpl(d.template||l.tmpl),arguments.length||(e=g)):p=this,p){if(!g&&e&&"view"===e._is&&(g=e),g&&e===g&&(e=g.data),u=!g,ie=ie||u,g||((t=t||{}).root=e),!ie||re.useViews||p.useViews||g&&g!==Z)v=V(p,e,t,n,g,i,a,d);else{if(g?(c=g.data,f=g.index,g.index=Ve):(g=Z,g.data=e,g.ctx=t),W(e)&&!n)for(s=0,o=e.length;o>s;s++)g.index=s,g.data=e[s],v+=p.fn(e[s],g,z);else g.data=e,v+=p.fn(e,g,z);g.data=c,g.index=f}u&&(ie=void 0)}return v}function V(e,t,n,r,i,a,s,o){function d(e){_=p({},n),_[x]=e}var l,u,c,f,g,v,m,h,w,x,_,y,k="";if(o&&(w=o.tagName,y=o.tagCtx,n=n?K(n,o.ctx):o.ctx,e===i.content?m=e!==i.ctx._wrp?i.ctx._wrp:void 0:e!==y.content?e===o.template?(m=y.tmpl,n._wrp=y.content):m=y.content||i.content:m=i.content,y.props.link===!1&&(n=n||{},n.link=!1),(x=y.props.itemVar)&&("~"!==x.charAt(0)&&$("Use itemVar='~myItem'"),x=x.slice(1))),i&&(s=s||i._.onRender,n=K(n,i.ctx)),a===!0&&(v=!0,a=0),s&&(n&&n.link===!1||o&&o._.noVws)&&(s=void 0),h=s,s===!0&&(h=void 0,s=i._.onRender),n=e.helpers?K(e.helpers,n):n,_=n,W(t)&&!r)for(c=v?i:void 0!==a&&i||new b(n,"array",i,t,e,a,s),i&&i._.useKey&&(c._.bnd=!o||o._.bnd&&o),x&&(c.it=x),x=c.it,l=0,u=t.length;u>l;l++)x&&d(t[l]),f=new b(_,"item",c,t[l],e,(a||0)+l,s,m),g=e.fn(t[l],f,z),k+=c._.onRender?c._.onRender(g,f):g;else x&&d(t),c=v?i:new b(_,w||"data",i,t,e,a,s,m),o&&!o.flow&&(c.tag=o),k+=e.fn(t,c,z);return h?h(k,c):k}function M(e,t,n){var r=re.onError(e,t,n);if(""+e===e)throw new ne.Err(r);return!t.linkCtx&&t.linked?Y.html(r):r}function $(e){M("Syntax error\n"+e)}function N(e,t,n,r,i){function a(t){t-=f,t&&v.push(e.substr(f,t).replace(fe,"\\n"))}function s(t,n){t&&(t+="}}",$((n?"{{"+n+"}} block has {{/"+t+" without {{"+t:"Unmatched or missing {{/"+t)+", in template:\n"+e))}function o(o,d,c,h,w,x,b,_,y,k,j){(b&&d||y&&!c||_&&":"===_.slice(-1))&&$(o),x&&(w=":",h=Ce),y=y||n&&!i;var C=(d||n)&&[[]],T="",A="",R="",V="",M="",N="",E="",S="",U=!y&&!w;c=c||(_=_||"#data",w),a(j),f=j+o.length,b?u&&v.push(["*","\n"+_.replace(/^:/,"ret+= ").replace(ge,"$1")+";\n"]):c?("else"===c&&(he.test(_)&&$('for "{{else if expr}}" use "{{else expr}}"'),C=m[7]&&[[]],m[8]=e.substring(m[8],j),m=g.pop(),v=m[2],U=!0),_&&I(_.replace(fe," "),C,t).replace(me,function(e,t,n,r,i,a,s,o){return r="'"+i+"':",s?(A+=a+",",V+="'"+o+"',"):n?(R+=r+a+",",N+=r+"'"+o+"',"):t?E+=a:("trigger"===i&&(S+=a),T+=r+a+",",M+=r+"'"+o+"',",l=l||_e.test(i)),""}).slice(0,-1),C&&C[0]&&C.pop(),p=[c,h||!!r||l||"",U&&[],F(V,M,N),F(A,T,R),E,S,C||0],v.push(p),U&&(g.push(m),m=p,m[8]=f)):k&&(s(k!==m[0]&&"else"!==m[0]&&k,m[0]),m[8]=e.substring(m[8],j),m=g.pop()),s(!m&&k),v=m[2]}var d,p,l,u=re.allowCode||t&&t.allowCode,c=[],f=0,g=[],v=c,m=[,,c];return u&&(t.allowCode=u),n&&(void 0!==r&&(e=e.slice(0,-r.length-2)+pe),e=se+e+pe),s(g[0]&&g[0][2].pop()[0]),e.replace(D,o),a(e.length),(f=c[c.length-1])&&s(""+f!==f&&+f[8]===f[8]&&f[0]),n?(d=U(c,e,n),E(d,[c[0][7]])):d=U(c,t),d}function E(e,t){var n,r,i=0,a=t.length;for(e.deps=[];a>i;i++){r=t[i];for(n in r)"_jsvto"!==n&&r[n].length&&(e.deps=e.deps.concat(r[n]))}e.paths=r}function F(e,t,n){return[e.slice(0,-1),t.slice(0,-1),n.slice(0,-1)]}function S(e,t){return"\n	"+(t?t+":{":"")+"args:["+e[0]+"]"+(e[1]||!t?",\n	props:{"+e[1]+"}":"")+(e[2]?",\n	ctx:{"+e[2]+"}":"")}function I(e,t,n){function r(r,h,w,x,b,_,y,k,j,C,T,A,R,V,M,E,F,S,I,U){function K(e,n,r,s,o,d,u,c){var f="."===r;if(r&&(b=b.slice(n.length),f||(e=(s?'view.hlp("'+s+'")':o?"view":"data")+(c?(d?"."+d:s?"":o?"":"."+r)+(u||""):(c=s?"":o?d||"":r,"")),e+=c?"."+c:"",e=n+("view.data"===e.slice(0,9)?e.slice(5):e)),p)){if(q="linkTo"===i?a=t._jsvto=t._jsvto||[]:l.bd,B=f&&q[q.length-1]){if(B._jsv){for(;B.sb;)B=B.sb;B.bnd&&(b="^"+b.slice(1)),B.sb=b,B.bnd=B.bnd||"^"===b.charAt(0)}}else q.push(b);m[g]=I+(f?1:0)}return e}x=p&&x,x&&!k&&(b=x+b),_=_||"",w=w||h||A,b=b||j,C=C||F||"";var J,O,q,B,L;if(!y||d||o){if(p&&E&&!d&&!o&&(!i||s||a)&&(J=m[g-1],U.length-1>I-(J||0))){if(J=U.slice(J,I+r.length),O!==!0)if(q=a||u[g-1].bd,B=q[q.length-1],B&&B.prm){for(;B.sb&&B.sb.prm;)B=B.sb;L=B.sb={path:B.sb,bnd:B.bnd}}else q.push(L={path:q.pop()});E=oe+":"+J+" onerror=''"+de,O=f[E],O||(f[E]=!0,f[E]=O=N(E,n,!0)),O!==!0&&L&&(L._jsv=O,L.prm=l.bd,L.bnd=L.bnd||L.path&&L.path.indexOf("^")>=0)}return d?(d=!R,d?r:A+'"'):o?(o=!V,o?r:A+'"'):(w?(m[g]=I++,l=u[++g]={bd:[]},w):"")+(S?g?"":(c=U.slice(c,I),(i?(i=s=a=!1,"\b"):"\b,")+c+(c=I+r.length,p&&t.push(l.bd=[]),"\b")):k?(g&&$(e),p&&t.pop(),i=b,s=x,c=I+r.length,x&&(p=l.bd=t[i]=[]),b+":"):b?b.split("^").join(".").replace(ue,K)+(C?(l=u[++g]={bd:[]},v[g]=!0,C):_):_?_:M?(v[g]=!1,l=u[--g],M+(C?(l=u[++g],v[g]=!0,C):"")):T?(v[g]||$(e),","):h?"":(d=R,o=V,'"'))}$(e)}var i,a,s,o,d,p=t&&t[0],l={bd:p},u={0:l},c=0,f=n?n.links:p&&(p.links=p.links||{}),g=0,v={},m={},h=(e+(n?" ":"")).replace(ce,r);return!g&&h||$(e)}function U(e,t,n){var r,i,a,s,o,d,p,l,u,c,f,g,v,m,h,w,x,b,_,y,k,j,C,A,R,V,M,N,F,I,K=0,J=re.useViews||t.useViews||t.tags||t.templates||t.helpers||t.converters,O="",q={},B=e.length;for(""+t===t?(b=n?'data-link="'+t.replace(fe," ").slice(1,-1)+'"':t,t=0):(b=t.tmplName||"unnamed",t.allowCode&&(q.allowCode=!0),t.debug&&(q.debug=!0),f=t.bnds,x=t.tmpls),r=0;B>r;r++)if(i=e[r],""+i===i)O+='\n+"'+i+'"';else if(a=i[0],"*"===a)O+=";\n"+i[1]+"\nret=ret";else{if(s=i[1],k=!n&&i[2],o=S(i[3],"params")+"},"+S(v=i[4]),N=i[5],I=i[6],j=i[8]&&i[8].replace(ge,"$1"),(R="else"===a)?g&&g.push(i[7]):(K=0,f&&(g=i[7])&&(g=[g],K=f.push(1))),J=J||v[1]||v[2]||g||/view.(?!index)/.test(v[0]),(V=":"===a)?s&&(a=s===Ce?">":s+a):(k&&(_=T(j,q),_.tmplName=b+"/"+a,_.useViews=_.useViews||J,U(k,_),J=_.useViews,x.push(_)),R||(y=a,J=J||a&&(!te[a]||!te[a].flow),A=O,O=""),C=e[r+1],C=C&&"else"===C[0]),F=N?";\ntry{\nret+=":"\n+",m="",h="",V&&(g||I||s&&s!==Ce)){if(M="return {"+o+"};",w='c("'+s+'",view,',M=new Function("data,view,j,u"," // "+b+" "+K+" "+a+"\n"+M),M._er=N,m=w+K+",",h=")",M._tag=a,n)return M;E(M,g),c=!0}if(O+=V?(n?(N?"\ntry{\n":"")+"return ":F)+(c?(c=void 0,J=u=!0,w+(g?(f[K-1]=M,K):"{"+o+"}")+")"):">"===a?(p=!0,"h("+v[0]+")"):(l=!0,"((v="+(v[0]||"data")+')!=null?v:"")')):(d=!0,"\n{view:view,tmpl:"+(k?x.length:"0")+","+o+"},"),y&&!C){if(O="["+O.slice(0,-1)+"]",w='t("'+y+'",view,this,',n||g){if(O=new Function("data,view,j,u"," // "+b+" "+K+" "+y+"\nreturn "+O+";"),O._er=N,O._tag=y,g&&E(f[K-1]=O,g),n)return O;m=w+K+",undefined,",h=")"}O=A+F+w+(K||O)+")",g=0,y=0}N&&(J=!0,O+=";\n}catch(e){ret"+(n?"urn ":"+=")+m+"j._err(e,view,"+N+")"+h+";}\n"+(n?"":"ret=ret"))}O="// "+b+"\nvar v"+(d?",t=j._tag":"")+(u?",c=j._cnvt":"")+(p?",h=j.converters.html":"")+(n?";\n":',ret=""\n')+(q.debug?"debugger;":"")+O+(n?"\n":";\nreturn ret;"),re._dbgMode&&(O="try {\n"+O+"\n}catch(e){\nreturn j._err(e, view);\n}");try{O=new Function("data,view,j,u",O)}catch(L){$("Compiled template code:\n\n"+O+'\n: "'+L.message+'"')}return t&&(t.fn=O,t.useViews=!!J),O}function K(e,t){return e&&e!==t?t?p(p({},t),e):e:t&&p({},t)}function J(e){return je[e]||(je[e]="&#"+e.charCodeAt(0)+";")}function O(e){var t,n,r=[];if(typeof e===Te)for(t in e)n=e[t],n&&n.toJSON&&!n.toJSON()||G(n)||r.push({key:t,prop:n});return r}function q(t,n,r){var i=this.jquery&&(this[0]||M('Unknown template: "'+this.selector+'"')),a=i.getAttribute(Ae);return R.call(a?e.data(i)[Re]:X(i),t,n,r)}function B(e){return void 0!=e?be.test(e)&&(""+e).replace(ye,J)||e:""}var L=(0,eval)("this"),Q=e===!1;e=e&&e.fn?e:L.jQuery;var H,D,P,Z,z,G,W,X,Y,ee,te,ne,re,ie,ae="v0.9.72",se="{",oe="{",de="}",pe="}",le="^",ue=/^(!*?)(?:null|true|false|\d[\d.]*|([\w$]+|\.|~([\w$]+)|#(view|([\w$]+))?)([\w$.^]*?)(?:[.[^]([\w$]+)\]?)?)$/g,ce=/(\()(?=\s*\()|(?:([([])\s*)?(?:(\^?)(!*?[#~]?[\w$.^]+)?\s*((\+\+|--)|\+|-|&&|\|\||===|!==|==|!=|<=|>=|[<>%*:?\/]|(=))\s*|(!*?[#~]?[\w$.^]+)([([])?)|(,\s*)|(\(?)\\?(?:(')|("))|(?:\s*(([)\]])(?=\s*[.^]|\s*$|[^([])|[)\]])([([]?))|(\s+)/g,fe=/[ \t]*(\r\n|\n|\r)/g,ge=/\\(['"])/g,ve=/['"\\]/g,me=/(?:\x08|^)(onerror:)?(?:(~?)(([\w$_\.]+):)?([^\x08]+))\x08(,)?([^\x08]+)/gi,he=/^if\s/,we=/<(\w+)[>\s]/,xe=/[\x00`><"'&]/g,be=/[\x00`><\"'&]/,_e=/^on[A-Z]|^convert(Back)?$/,ye=xe,ke=0,je={"&":"&amp;","<":"&lt;",">":"&gt;","\x00":"&#0;","'":"&#39;",'"':"&#34;","`":"&#96;"},Ce="html",Te="object",Ae="data-jsv-tmpl",Re="jsvTmpl",Ve="For #index in nested block use #getIndex().",Me={},$e=L.jsrender,Ne=$e&&e&&!e.render,Ee={template:{compile:j},tag:{compile:y},helper:{},converter:{}};if(z={jsviews:ae,settings:function(e){p(re,e),o(re._dbgMode),re.jsv&&re.jsv()},sub:{View:b,Err:d,tmplFn:N,parse:I,extend:p,extendCtx:K,syntaxErr:$,onStore:{},_ths:r,_tg:function(){}},map:C,_cnvt:m,_tag:x,_err:M},(d.prototype=new Error).constructor=d,c.depends=function(){return[this.get("item"),"index"]},f.depends="index",b.prototype={get:u,getIndex:f,getRsc:w,getTmpl:v,hlp:g,_is:"view"},!($e||e&&e.render)){for(H in Ee)A(H,Ee[H]);X=z.templates,Y=z.converters,ee=z.helpers,te=z.tags,ne=z.sub,re=z.settings,ne._tg.prototype={baseApply:k,cvtArgs:h},Z=ne.topView=new b,e?(e.fn.render=q,e.observable&&(p(ne,e.views.sub),z.map=e.views.map)):(e={},Q&&(L.jsrender=e),e.renderFile=e.__express=e.compile=function(){throw"Node.js: use npm jsrender, or jsrender-node.js"},e.isFunction=function(e){return"function"==typeof e},e.isArray=Array.isArray||function(e){return"[object Array]"==={}.toString.call(e)},ne._jq=function(t){t!==e&&(p(t,e),e=t,e.fn.render=q,delete e.jsrender)},e.jsrender=ae),G=e.isFunction,W=e.isArray,e.render=Me,e.views=z,e.templates=X=z.templates,re({debugMode:o,delimiters:l,onError:function(e,t,n){return t&&(e=void 0===n?"{Error: "+(e.message||e)+"}":G(n)?n(e,t):n),void 0==e?"":e},_dbgMode:!1}),te({"if":{render:function(e){var t=this,n=t.tagCtx,r=t.rendering.done||!e&&(arguments.length||!n.index)?"":(t.rendering.done=!0,t.selected=n.index,n.render(n.view,!0));return r},flow:!0},"for":{render:function(e){var t,n=!arguments.length,r=this,i=r.tagCtx,a="",s=0;return r.rendering.done||(t=n?i.view.data:e,void 0!==t&&(a+=i.render(t,n),s+=W(t)?t.length:1),(r.rendering.done=s)&&(r.selected=i.index)),a},flow:!0},props:{baseTag:"for",dataMap:C(O),flow:!0},include:{flow:!0},"*":{render:i,flow:!0},":*":{render:i,flow:!0},dbg:ee.dbg=Y.dbg=s}),Y({html:B,attr:B,url:function(e){return void 0!=e?encodeURI(""+e):null===e?e:""}}),l()}return Ne&&$e.views.sub._jq(e),e||$e});
//# sourceMappingURL=jsrender.min.js.map;
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
      axis: "y",
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
          self.moveLayout($(this).data().object, $(this).data().parent);
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

