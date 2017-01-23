(function(f){if(typeof exports==="object"&&typeof module!=="undefined"){module.exports=f()}else if(typeof define==="function"&&define.amd){define([],f)}else{var g;if(typeof window!=="undefined"){g=window}else if(typeof global!=="undefined"){g=global}else if(typeof self!=="undefined"){g=self}else{g=this}(g.ftw || (g.ftw = {})).simplelayout = f()}})(function(){var define,module,exports;return (function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
"use strict";

var _Toolbox = require("toolbox/Toolbox");

var _Toolbox2 = _interopRequireDefault(_Toolbox);

var _Simplelayout = require("simplelayout/Simplelayout");

var _Simplelayout2 = _interopRequireDefault(_Simplelayout);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

module.exports = {
  simplelayout: _Simplelayout2.default,
  toolbox: _Toolbox2.default
};

},{"simplelayout/Simplelayout":9,"toolbox/Toolbox":12}],2:[function(require,module,exports){
(function (global){
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.default = handlebarsTimes;

var _handlebars = (typeof window !== "undefined" ? window['Handlebars'] : typeof global !== "undefined" ? global['Handlebars'] : null);

var _handlebars2 = _interopRequireDefault(_handlebars);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

_handlebars2.default.registerHelper('times', function (n, block) {
    var accum = '';
    for (var i = 0; i < n; ++i) {
        accum += block.fn(i);
    }return accum;
});

function handlebarsTimes() {}

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})
},{}],3:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.default = createGUID;
function createGUID() {
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0;
        var v = c === "x" ? r : r & 0x3 | 0x8;
        return v.toString(16);
    });
}

},{}],4:[function(require,module,exports){
(function (global){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = Block;

var _EventEmitter = require("simplelayout/EventEmitter");

var _EventEmitter2 = _interopRequireDefault(_EventEmitter);

var _transactional = require("simplelayout/transactional");

var _transactional2 = _interopRequireDefault(_transactional);

var _Element = require("simplelayout/Element");

var _Element2 = _interopRequireDefault(_Element);

var _jquery = (typeof window !== "undefined" ? window['$'] : typeof global !== "undefined" ? global['$'] : null);

var _jquery2 = _interopRequireDefault(_jquery);

var _handlebars = (typeof window !== "undefined" ? window['Handlebars'] : typeof global !== "undefined" ? global['Handlebars'] : null);

var _handlebars2 = _interopRequireDefault(_handlebars);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var EE = _EventEmitter2.default.getInstance();

function Block(content, type) {

  if (!(this instanceof Block)) {
    throw new TypeError("Block constructor cannot be called as a function.");
  }

  this.name = "block";

  this.type = type;

  var frame = (0, _jquery2.default)(_handlebars2.default.compile('<div class="iFrameFix"></div>')());

  var template = "<div data-type=\"{{type}}\" class=\"sl-block {{type}}\"><div class=\"sl-block-content\">{{{content}}}</div></div>";

  _Element2.default.call(this, template);

  this.create({ type: type, content: content });

  this.content = function (toReplace) {
    (0, _jquery2.default)(".sl-block-content", this.element).html(toReplace);
    EE.trigger("blockReplaced", [this]);
    return this;
  };

  this.delete = function () {
    return this.parent.deleteBlock(this.id);
  };

  this.fixFrame = function () {
    this.element.prepend(frame);
    return this;
  };

  this.fixFrame();

  this.enableFrame = function () {
    frame.css("display", "block");
    return this;
  };

  this.disableFrame = function () {
    frame.css("display", "none");
    return this;
  };

  this.restore = function (restoreElement, restoreParent, restoreType, represents) {
    this.type = restoreType;
    Block.prototype.restore.call(this, restoreElement, restoreParent, represents);
    this.fixFrame();
    this.commit();
  };

  this.toJSON = function () {
    return { represents: this.represents, type: this.type };
  };
};

_transactional2.default.call(Block.prototype);
_Element2.default.call(Block.prototype);

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})
},{"simplelayout/Element":5,"simplelayout/EventEmitter":6,"simplelayout/transactional":11}],5:[function(require,module,exports){
(function (global){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = Element;

var _idHelper = require("helpers/idHelper");

var _idHelper2 = _interopRequireDefault(_idHelper);

var _jquery = (typeof window !== "undefined" ? window['$'] : typeof global !== "undefined" ? global['$'] : null);

var _jquery2 = _interopRequireDefault(_jquery);

var _handlebars = (typeof window !== "undefined" ? window['Handlebars'] : typeof global !== "undefined" ? global['Handlebars'] : null);

var _handlebars2 = _interopRequireDefault(_handlebars);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function Element(template, represents) {

  this.template = _handlebars2.default.compile(template || "");
  this.represents = represents;
  this.enabled = true;

  this.create = function (data) {
    this.element = (0, _jquery2.default)(this.template(data));
    this.id = (0, _idHelper2.default)();
    this.element.data({ id: this.id, object: this });
    return this.element;
  };

  this.data = function (data) {
    if (data) {
      return this.element.data(data);
    }
    return this.element.data();
  };

  this.remove = function () {
    this.element.remove();
    return this;
  };

  this.detach = function () {
    this.element.detach();
    return this;
  };

  this.attachToolbar = function (toolbar) {
    this.toolbar = toolbar;
    this.element.append(toolbar.element);
    return this;
  };

  this.isEnabled = function (state) {
    this.element.toggleClass("disabled", !state);
    this.enabled = state;
    return this;
  };

  this.restore = function (restoreElement, restoreParent, restoreRepresents) {
    this.element = (0, _jquery2.default)(restoreElement);
    this.parent = restoreParent;
    this.data({ id: this.id, object: this, parent: restoreParent, represents: restoreRepresents });
    this.represents = restoreRepresents;
  };

  return this;
}

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})
},{"helpers/idHelper":3}],6:[function(require,module,exports){
(function (global){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = EventEmitter;

var _jquery = (typeof window !== "undefined" ? window['$'] : typeof global !== "undefined" ? global['$'] : null);

var _jquery2 = _interopRequireDefault(_jquery);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var EE = require("wolfy87-eventemitter");

var instance = null;
var eventEmitter = null;

function EventEmitter() {
  this.trigger = function (eventType, data) {
    (0, _jquery2.default)(document).trigger(eventType, data);
    eventEmitter.trigger(eventType, data);
  };

  this.on = function (eventType, callback) {
    eventEmitter.on(eventType, callback);
  };
}

EventEmitter.getInstance = function () {

  if (instance === null) {
    eventEmitter = new EE();
    instance = new EventEmitter();
  }

  return instance;
};

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})
},{"wolfy87-eventemitter":15}],7:[function(require,module,exports){
(function (global){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = Layout;

var _Block = require("simplelayout/Block");

var _Block2 = _interopRequireDefault(_Block);

var _EventEmitter = require("simplelayout/EventEmitter");

var _EventEmitter2 = _interopRequireDefault(_EventEmitter);

var _transactional = require("simplelayout/transactional");

var _transactional2 = _interopRequireDefault(_transactional);

var _Element = require("simplelayout/Element");

var _Element2 = _interopRequireDefault(_Element);

var _Toolbar = require("simplelayout/Toolbar");

var _Toolbar2 = _interopRequireDefault(_Toolbar);

var _handlebars = require("helpers/handlebars");

var _handlebars2 = _interopRequireDefault(_handlebars);

var _jquery = (typeof window !== "undefined" ? window['$'] : typeof global !== "undefined" ? global['$'] : null);

var _jquery2 = _interopRequireDefault(_jquery);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var EE = _EventEmitter2.default.getInstance();

function Layout(columns) {
  if (!(this instanceof Layout)) {
    throw new TypeError("Layout constructor cannot be called as a function.");
  }

  columns = columns || 4;

  var template = "<div class='sl-layout'>{{#times columns}}<div class='sl-column sl-col-{{../columns}}'></div>{{/times}}</div>";

  _Element2.default.call(this, template);

  this.name = "layout";

  this.create({ columns: columns });

  this.columns = columns;

  this.blocks = {};

  this.toolbar = new _Toolbar2.default();

  this.hasBlocks = function () {
    return Object.keys(this.blocks).length > 0;
  };

  this.delete = function () {
    return this.parent.deleteLayout(this.id);
  };

  this.insertBlock = function (content, type) {
    var block = new _Block2.default(content, type);
    block.parent = this;
    block.data({ parent: this });
    this.blocks[block.id] = block;
    EE.trigger("blockInserted", [block]);
    return block;
  };

  this.deleteBlock = function (id) {
    var block = this.blocks[id];
    delete this.blocks[id];
    EE.trigger("blockDeleted", [block]);
    return block;
  };

  this.getCommittedBlocks = function () {
    return _jquery2.default.grep(_jquery2.default.map(this.blocks, function (block) {
      return block;
    }), function (block) {
      return block.committed;
    });
  };

  this.getInsertedBlocks = function () {
    return _jquery2.default.grep(_jquery2.default.map(this.blocks, function (block) {
      return block;
    }), function (block) {
      return !block.committed;
    });
  };

  this.moveBlock = function (block, target) {
    EE.trigger("beforeBlockMoved", [block]);
    this.deleteBlock(block.id);
    block.parent = target;
    block.data({ parent: target });
    target.blocks[block.id] = block;
    EE.trigger("blockMoved", [block]);
    return this;
  };

  this.restore = function (restoreElement, restoreParent, restoreColumn, represents) {
    var self = this;
    this.columns = restoreColumn;
    Layout.prototype.restore.call(this, restoreElement, restoreParent, represents);
    this.commit();
    (0, _jquery2.default)(".sl-block", restoreElement).each(function () {
      self.insertBlock().restore(this, self, (0, _jquery2.default)(this).data().type, (0, _jquery2.default)(this).data().uid);
    });
  };

  this.toJSON = function () {
    return { columns: this.columns, blocks: this.blocks };
  };
};

_transactional2.default.call(Layout.prototype);
_Element2.default.call(Layout.prototype);

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})
},{"helpers/handlebars":2,"simplelayout/Block":4,"simplelayout/Element":5,"simplelayout/EventEmitter":6,"simplelayout/Toolbar":10,"simplelayout/transactional":11}],8:[function(require,module,exports){
(function (global){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = Layoutmanager;

var _Layout = require("simplelayout/Layout");

var _Layout2 = _interopRequireDefault(_Layout);

var _Block = require("simplelayout/Block");

var _Block2 = _interopRequireDefault(_Block);

var _EventEmitter = require("simplelayout/EventEmitter");

var _EventEmitter2 = _interopRequireDefault(_EventEmitter);

var _Element = require("simplelayout/Element");

var _Element2 = _interopRequireDefault(_Element);

var _transactional = require("simplelayout/transactional");

var _transactional2 = _interopRequireDefault(_transactional);

var _jquery = (typeof window !== "undefined" ? window['$'] : typeof global !== "undefined" ? global['$'] : null);

var _jquery2 = _interopRequireDefault(_jquery);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var EE = _EventEmitter2.default.getInstance();

function Layoutmanager() {

  if (!(this instanceof Layoutmanager)) {
    throw new TypeError("Layoutmanager constructor cannot be called as a function.");
  }

  var template = "<div class='sl-simplelayout'></div>";

  _Element2.default.call(this, template);

  this.name = "layoutmanager";

  this.create();

  this.layouts = {};

  this.attachTo = function (target) {
    (0, _jquery2.default)(target).append(this.element);
    return this;
  };

  this.insertLayout = function (columns) {
    var layout = new _Layout2.default(columns);
    layout.parent = this;
    layout.data({ parent: this });
    this.layouts[layout.id] = layout;
    EE.trigger("layoutInserted", [layout]);
    return layout;
  };

  this.deleteLayout = function (id) {
    var layout = this.layouts[id];
    delete this.layouts[id];
    EE.trigger("layoutDeleted", [layout]);
    return layout;
  };

  this.hasLayouts = function () {
    return Object.keys(this.layouts).length > 0;
  };

  this.getInsertedBlocks = function () {
    return _jquery2.default.map(this.layouts, function (layout) {
      return layout.getInsertedBlocks();
    });
  };

  this.getCommittedBlocks = function () {
    return _jquery2.default.map(this.layouts, function (layout) {
      return layout.getCommittedBlocks();
    });
  };

  this.moveBlock = function (block, target) {
    block.parent.moveBlock(block, target);
    return this;
  };

  this.restore = function (restoreElement, represents) {
    var self = this;
    Layoutmanager.prototype.restore.call(this, restoreElement, null, represents);
    this.commit();
    (0, _jquery2.default)(".sl-layout", restoreElement).each(function () {
      self.insertLayout().restore(this, self, (0, _jquery2.default)(".sl-column", this).length);
    });
  };

  this.toJSON = function () {
    return { layouts: this.layouts, represents: this.represents };
  };
};

_Element2.default.call(Layoutmanager.prototype);
_transactional2.default.call(Layoutmanager.prototype);

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})
},{"simplelayout/Block":4,"simplelayout/Element":5,"simplelayout/EventEmitter":6,"simplelayout/Layout":7,"simplelayout/transactional":11}],9:[function(require,module,exports){
(function (global){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = Simplelayout;

var _Layoutmanager = require("simplelayout/Layoutmanager");

var _Layoutmanager2 = _interopRequireDefault(_Layoutmanager);

var _Toolbar = require("simplelayout/Toolbar");

var _Toolbar2 = _interopRequireDefault(_Toolbar);

var _Toolbox = require("toolbox/Toolbox");

var _Toolbox2 = _interopRequireDefault(_Toolbox);

var _EventEmitter = require("simplelayout/EventEmitter");

var _EventEmitter2 = _interopRequireDefault(_EventEmitter);

var _jquery = (typeof window !== "undefined" ? window['$'] : typeof global !== "undefined" ? global['$'] : null);

var _jquery2 = _interopRequireDefault(_jquery);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

(typeof window !== "undefined" ? window['$']['ui'] : typeof global !== "undefined" ? global['$']['ui'] : null);

var EE = _EventEmitter2.default.getInstance();

function Simplelayout(options) {

  if (!(this instanceof Simplelayout)) {
    throw new TypeError("Simplelayout constructor cannot be called as a function.");
  }

  var root = (0, _jquery2.default)(":root");

  var self = this;

  var sortableHelper = function sortableHelper() {
    return (0, _jquery2.default)('<div class="draggableHelper"><div>');
  };

  var LAYOUT_SORTABLE = {
    connectWith: ".sl-simplelayout",
    items: ".sl-layout",
    handle: ".sl-toolbar-layout .move",
    placeholder: "layout-placeholder",
    cursorAt: { left: 50, top: 50 },
    forcePlaceholderSize: true,
    helper: sortableHelper,
    receive: function receive(event, ui) {
      var layout;
      if (ui.item.hasClass("sl-toolbox-layout")) {
        var item = (0, _jquery2.default)(this).find(".ui-draggable");
        layout = (0, _jquery2.default)(this).data().object.insertLayout(ui.item.data().columns);
        layout.element.insertAfter(item);
        item.remove();
      } else {
        self.moveLayout((0, _jquery2.default)(ui.item).data().object, (0, _jquery2.default)(this).data().object);
        self.disableFrames();
      }
    },
    beforeStart: function beforeStart(event, ui) {
      if (ui.item.hasClass("sl-layout")) {
        self.restrictLayout(ui.item.data().object.columns);
      }
    },
    start: function start() {
      self.enableFrames();
      root.addClass("sl-layout-dragging");
      (0, _jquery2.default)(".sl-simplelayout").sortable("refreshPositions");
    },
    update: function update(event, ui) {
      if (ui.item.parent()[0] === this && !ui.sender) {
        _EventEmitter2.default.trigger("layoutMoved", [ui.item.data().object]);
      }
    },
    stop: function stop(event, ui) {
      if (ui.item.hasClass("sl-layout")) {
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
    receive: function receive(event, ui) {
      var block;
      if ((0, _jquery2.default)(ui.item).hasClass("sl-toolbox-block")) {
        var item = (0, _jquery2.default)(this).find(".ui-draggable");
        var layout = (0, _jquery2.default)(this).parents(".sl-layout").data().object;
        block = layout.insertBlock("", (0, _jquery2.default)(ui.item).data().type);
        block.element.insertAfter(item);
        item.remove();
      } else {
        var sourceLayout = ui.sender.parents(".sl-layout").data().object;
        sourceLayout.moveBlock(ui.item.data().object, (0, _jquery2.default)(this).parents(".sl-layout").data().object);
      }
    },
    start: function start() {
      self.enableFrames();
      root.addClass("sl-block-dragging");
      (0, _jquery2.default)(".sl-column").sortable("refreshPositions");
    },
    stop: function stop() {
      self.disableFrames();
      root.removeClass("sl-block-dragging");
    },
    update: function update(event, ui) {
      if (ui.item.parent()[0] === this && !ui.sender) {
        EE.trigger("blockMoved", [ui.item.data().object]);
      }
    }
  };

  this.options = _jquery2.default.extend({
    toolbox: new _Toolbox2.default(),
    editLayouts: true,
    layoutRestrictions: {}
  }, options || {});

  this.managers = {};

  this.insertManager = function () {
    var manager = new _Layoutmanager2.default();
    this.managers[manager.id] = manager;
    return manager;
  };

  this.moveLayout = function (layout, target) {
    var source = layout.parent;

    layout.data({ parent: target });
    layout.parent = target;
    target.layouts[layout.id] = layout;

    source.deleteLayout(layout.id);
    EE.trigger("layoutMoved", [layout]);
    return this;
  };

  this.getCommittedBlocks = function () {
    return _jquery2.default.map(this.managers, function (manager) {
      return manager.getCommittedBlocks();
    });
  };

  this.getInsertedBlocks = function () {
    return _jquery2.default.map(this.managers, function (manager) {
      return manager.getInsertedBlocks();
    });
  };

  this.disableFrames = function () {
    _jquery2.default.each(this.getCommittedBlocks(), function (idx, block) {
      block.disableFrame();
    });
    return this;
  };

  this.enableFrames = function () {
    _jquery2.default.each(this.getCommittedBlocks(), function (idx, block) {
      block.enableFrame();
    });
    return this;
  };

  this.restrictLayout = function (layout) {
    if (this.options.layoutRestrictions[layout]) {
      _jquery2.default.each(this.options.layoutRestrictions[layout], function (idx, managerId) {
        self.managers[managerId].isEnabled(false).element.sortable("disable");
      });
    }
  };

  this.allowLayout = function (layout) {
    if (this.options.layoutRestrictions[layout]) {
      _jquery2.default.each(this.options.layoutRestrictions[layout], function (idx, managerId) {
        self.managers[managerId].isEnabled(true).element.sortable("enable");
      });
    }
  };

  this.on = function (eventType, callback) {
    EE.on(eventType, callback);
    return this;
  };

  this.serialize = function () {
    return JSON.stringify(this.managers);
  };

  this.restore = function (source) {
    this.source = source;
    (0, _jquery2.default)(".sl-simplelayout", source).each(function () {
      self.insertManager().restore(this, (0, _jquery2.default)(this).attr("id"));
    });
    (0, _jquery2.default)(".sl-simplelayout", this.source).sortable(LAYOUT_SORTABLE);
    (0, _jquery2.default)(".sl-column", this.source).sortable(BLOCK_SORTABLE);
    return this;
  };

  var TOOLBOX_COMPONENT_DRAGGABLE_SETTINGS = {
    helper: "clone",
    cursor: "pointer",
    beforeStart: function beforeStart() {
      if ((0, _jquery2.default)(this).hasClass("sl-toolbox-layout")) {
        self.restrictLayout((0, _jquery2.default)(this).data().columns);
      }
    },
    start: function start() {
      self.enableFrames();
      if ((0, _jquery2.default)(this).hasClass("sl-toolbox-block")) {
        root.addClass("sl-block-dragging");
      } else {
        root.addClass("sl-layout-dragging");
      }
    },
    stop: function stop() {
      self.allowLayout((0, _jquery2.default)(this).data().columns);
      self.disableFrames();
      root.removeClass("sl-block-dragging sl-layout-dragging");
    }
  };

  this.on("layout-committed", function (layout) {
    if (self.options.editLayouts) {
      var layoutToolbar = new _Toolbar2.default(self.options.toolbox.options.layoutActions, "vertical", "layout");
      layout.attachToolbar(layoutToolbar);
      (0, _jquery2.default)(".sl-column", layout.element).sortable(BLOCK_SORTABLE);
    }
  });

  this.on("block-committed", function (block) {
    if (self.options.toolbox.options.blocks[block.type]) {
      var blockToolbar = new _Toolbar2.default(self.options.toolbox.options.blocks[block.type].actions, "horizontal", "block");
      block.attachToolbar(blockToolbar);
    }
  });

  this.options.toolbox.element.find(".sl-toolbox-block, .sl-toolbox-layout").draggable(TOOLBOX_COMPONENT_DRAGGABLE_SETTINGS);
  this.options.toolbox.element.find(".sl-toolbox-layout").draggable("option", "connectToSortable", ".sl-simplelayout");
  this.options.toolbox.element.find(".sl-toolbox-block").draggable("option", "connectToSortable", ".sl-column");

  (0, _jquery2.default)(".sl-simplelayout").sortable(LAYOUT_SORTABLE);
  (0, _jquery2.default)(".sl-column").sortable(BLOCK_SORTABLE);

  root.addClass("simplelayout-initialized");

  /* Patch for registring beforeStart event */
  var oldMouseStart = _jquery2.default.ui.sortable.prototype._mouseStart;
  _jquery2.default.ui.sortable.prototype._mouseStart = function (event, overrideHandle, noActivation) {
    this._trigger("beforeStart", event, this._uiHash());
    oldMouseStart.apply(this, [event, overrideHandle, noActivation]);
  };
};

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})
},{"simplelayout/EventEmitter":6,"simplelayout/Layoutmanager":8,"simplelayout/Toolbar":10,"toolbox/Toolbox":12}],10:[function(require,module,exports){
(function (global){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = Toolbar;

var _Element = require("simplelayout/Element");

var _Element2 = _interopRequireDefault(_Element);

var _jquery = (typeof window !== "undefined" ? window['$'] : typeof global !== "undefined" ? global['$'] : null);

var _jquery2 = _interopRequireDefault(_jquery);

var _handlebars = (typeof window !== "undefined" ? window['Handlebars'] : typeof global !== "undefined" ? global['Handlebars'] : null);

var _handlebars2 = _interopRequireDefault(_handlebars);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function Toolbar(actions, orientation, type) {

  if (!(this instanceof Toolbar)) {
    throw new TypeError("Toolbar constructor cannot be called as a function.");
  }

  actions = actions || {};

  var template = "\n    <ul class='sl-toolbar{{#if type}}-{{type}}{{/if}}{{#if orientation}} {{orientation}}{{/if}}'>\n      {{#each actions}}\n        <li>\n          <a\n            {{#each this}}\n            {{@key}}=\"{{this}}\"\n            {{/each}}\n          >\n          </a>\n        </li>\n        <li class='delimiter'></li>\n      {{/each}}\n    </ul>\n  ";

  _Element2.default.call(this, template);

  this.create({ actions: actions, orientation: orientation, type: type });

  this.disable = function (action) {
    (0, _jquery2.default)("." + action, this.element).css("display", "none");
  };

  this.enable = function (action) {
    (0, _jquery2.default)("." + action, this.element).css("display", "block");
  };
};

_Element2.default.call(Toolbar.prototype);

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})
},{"simplelayout/Element":5}],11:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = transactional;

var _EventEmitter = require("simplelayout/EventEmitter");

var _EventEmitter2 = _interopRequireDefault(_EventEmitter);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var EE = _EventEmitter2.default.getInstance();

function transactional() {

  this.committed = false;

  this.commit = function () {
    if (this.committed) {
      throw new Error("Transaction is already committed");
    }
    this.committed = true;
    EE.trigger(this.name + "-committed", [this]);
    return this;
  };

  this.rollback = function () {
    if (!this.committed) {
      throw new Error("Transaction on not yet committed");
    }
    this.committed = false;
    EE.trigger(this.name + "-rollbacked", [this]);
    return this;
  };
};

},{"simplelayout/EventEmitter":6}],12:[function(require,module,exports){
(function (global){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = Toolbox;

var _Element = require("simplelayout/Element");

var _Element2 = _interopRequireDefault(_Element);

var _path = require("path");

var _path2 = _interopRequireDefault(_path);

var _handlebars = (typeof window !== "undefined" ? window['Handlebars'] : typeof global !== "undefined" ? global['Handlebars'] : null);

var _handlebars2 = _interopRequireDefault(_handlebars);

var _jquery = (typeof window !== "undefined" ? window['$'] : typeof global !== "undefined" ? global['$'] : null);

var _jquery2 = _interopRequireDefault(_jquery);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

(typeof window !== "undefined" ? window['$']['ui'] : typeof global !== "undefined" ? global['$']['ui'] : null);

function Toolbox(options) {

  if (!(this instanceof Toolbox)) {
    throw new TypeError("Toolbox constructor cannot be called as a function.");
  }

  var template = "\n  <div id='sl-toolbox' class='sl-toolbox'>\n    <div>\n      <a class='sl-toolbox-header blocks'>\n        <span></span>\n      </a>\n        <div class='sl-toolbox-blocks'>\n          {{#each blocks}}\n            <a class='sl-toolbox-block {{contentType}}' data-type='{{contentType}}' data-form-url='{{formUrl}}'>\n              <span class='icon-{{contentType}}'></span>\n              <span class='description'>{{title}}</span>\n            </a>\n          {{/each}}\n        </div>\n        {{#if canChangeLayout}}\n          <a class='sl-toolbox-header layouts'>\n            <span></span>\n          </a>\n          <div class='sl-toolbox-layouts'>\n            {{#each layouts}}\n              <a class='sl-toolbox-layout' data-columns='{{this}}'>\n                <span>{{this}}</span>\n                <span class='description'>{{this}}{{../labels.labelColumnPostfix}}</span>\n              </a>\n            {{/each}}\n          </div>\n        {{/if}}\n      </div>\n    </div>\n    ";

  _Element2.default.call(this, template);

  this.options = _jquery2.default.extend({
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
  _jquery2.default.each(this.options.blocks, function (idx, block) {
    blockObjects[block.contentType] = block;
  });

  this.options.blocks = blockObjects;

  this.attachTo = function (target) {
    target.append(this.element);
  };

  this.blocksEnabled = function (state) {
    (0, _jquery2.default)(".sl-toolbox-blocks", this.element).toggleClass("disabled", !state);
  };

  /* Patch for registring beforeStart event */
  var oldMouseStart = _jquery2.default.ui.draggable.prototype._mouseStart;
  _jquery2.default.ui.draggable.prototype._mouseStart = function (event, overrideHandle, noActivation) {
    this._trigger("beforeStart", event, this._uiHash());
    oldMouseStart.apply(this, [event, overrideHandle, noActivation]);
  };
};

_Element2.default.call(Toolbox.prototype);

}).call(this,typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})
},{"path":13,"simplelayout/Element":5}],13:[function(require,module,exports){
(function (process){
// Copyright Joyent, Inc. and other Node contributors.
//
// Permission is hereby granted, free of charge, to any person obtaining a
// copy of this software and associated documentation files (the
// "Software"), to deal in the Software without restriction, including
// without limitation the rights to use, copy, modify, merge, publish,
// distribute, sublicense, and/or sell copies of the Software, and to permit
// persons to whom the Software is furnished to do so, subject to the
// following conditions:
//
// The above copyright notice and this permission notice shall be included
// in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
// MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
// NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
// DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
// OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
// USE OR OTHER DEALINGS IN THE SOFTWARE.

// resolves . and .. elements in a path array with directory names there
// must be no slashes, empty elements, or device names (c:\) in the array
// (so also no leading and trailing slashes - it does not distinguish
// relative and absolute paths)
function normalizeArray(parts, allowAboveRoot) {
  // if the path tries to go above the root, `up` ends up > 0
  var up = 0;
  for (var i = parts.length - 1; i >= 0; i--) {
    var last = parts[i];
    if (last === '.') {
      parts.splice(i, 1);
    } else if (last === '..') {
      parts.splice(i, 1);
      up++;
    } else if (up) {
      parts.splice(i, 1);
      up--;
    }
  }

  // if the path is allowed to go above the root, restore leading ..s
  if (allowAboveRoot) {
    for (; up--; up) {
      parts.unshift('..');
    }
  }

  return parts;
}

// Split a filename into [root, dir, basename, ext], unix version
// 'root' is just a slash, or nothing.
var splitPathRe =
    /^(\/?|)([\s\S]*?)((?:\.{1,2}|[^\/]+?|)(\.[^.\/]*|))(?:[\/]*)$/;
var splitPath = function(filename) {
  return splitPathRe.exec(filename).slice(1);
};

// path.resolve([from ...], to)
// posix version
exports.resolve = function() {
  var resolvedPath = '',
      resolvedAbsolute = false;

  for (var i = arguments.length - 1; i >= -1 && !resolvedAbsolute; i--) {
    var path = (i >= 0) ? arguments[i] : process.cwd();

    // Skip empty and invalid entries
    if (typeof path !== 'string') {
      throw new TypeError('Arguments to path.resolve must be strings');
    } else if (!path) {
      continue;
    }

    resolvedPath = path + '/' + resolvedPath;
    resolvedAbsolute = path.charAt(0) === '/';
  }

  // At this point the path should be resolved to a full absolute path, but
  // handle relative paths to be safe (might happen when process.cwd() fails)

  // Normalize the path
  resolvedPath = normalizeArray(filter(resolvedPath.split('/'), function(p) {
    return !!p;
  }), !resolvedAbsolute).join('/');

  return ((resolvedAbsolute ? '/' : '') + resolvedPath) || '.';
};

// path.normalize(path)
// posix version
exports.normalize = function(path) {
  var isAbsolute = exports.isAbsolute(path),
      trailingSlash = substr(path, -1) === '/';

  // Normalize the path
  path = normalizeArray(filter(path.split('/'), function(p) {
    return !!p;
  }), !isAbsolute).join('/');

  if (!path && !isAbsolute) {
    path = '.';
  }
  if (path && trailingSlash) {
    path += '/';
  }

  return (isAbsolute ? '/' : '') + path;
};

// posix version
exports.isAbsolute = function(path) {
  return path.charAt(0) === '/';
};

// posix version
exports.join = function() {
  var paths = Array.prototype.slice.call(arguments, 0);
  return exports.normalize(filter(paths, function(p, index) {
    if (typeof p !== 'string') {
      throw new TypeError('Arguments to path.join must be strings');
    }
    return p;
  }).join('/'));
};


// path.relative(from, to)
// posix version
exports.relative = function(from, to) {
  from = exports.resolve(from).substr(1);
  to = exports.resolve(to).substr(1);

  function trim(arr) {
    var start = 0;
    for (; start < arr.length; start++) {
      if (arr[start] !== '') break;
    }

    var end = arr.length - 1;
    for (; end >= 0; end--) {
      if (arr[end] !== '') break;
    }

    if (start > end) return [];
    return arr.slice(start, end - start + 1);
  }

  var fromParts = trim(from.split('/'));
  var toParts = trim(to.split('/'));

  var length = Math.min(fromParts.length, toParts.length);
  var samePartsLength = length;
  for (var i = 0; i < length; i++) {
    if (fromParts[i] !== toParts[i]) {
      samePartsLength = i;
      break;
    }
  }

  var outputParts = [];
  for (var i = samePartsLength; i < fromParts.length; i++) {
    outputParts.push('..');
  }

  outputParts = outputParts.concat(toParts.slice(samePartsLength));

  return outputParts.join('/');
};

exports.sep = '/';
exports.delimiter = ':';

exports.dirname = function(path) {
  var result = splitPath(path),
      root = result[0],
      dir = result[1];

  if (!root && !dir) {
    // No dirname whatsoever
    return '.';
  }

  if (dir) {
    // It has a dirname, strip trailing slash
    dir = dir.substr(0, dir.length - 1);
  }

  return root + dir;
};


exports.basename = function(path, ext) {
  var f = splitPath(path)[2];
  // TODO: make this comparison case-insensitive on windows?
  if (ext && f.substr(-1 * ext.length) === ext) {
    f = f.substr(0, f.length - ext.length);
  }
  return f;
};


exports.extname = function(path) {
  return splitPath(path)[3];
};

function filter (xs, f) {
    if (xs.filter) return xs.filter(f);
    var res = [];
    for (var i = 0; i < xs.length; i++) {
        if (f(xs[i], i, xs)) res.push(xs[i]);
    }
    return res;
}

// String.prototype.substr - negative index don't work in IE8
var substr = 'ab'.substr(-1) === 'b'
    ? function (str, start, len) { return str.substr(start, len) }
    : function (str, start, len) {
        if (start < 0) start = str.length + start;
        return str.substr(start, len);
    }
;

}).call(this,require('_process'))
},{"_process":14}],14:[function(require,module,exports){
// shim for using process in browser
var process = module.exports = {};

// cached from whatever global is present so that test runners that stub it
// don't break things.  But we need to wrap it in a try catch in case it is
// wrapped in strict mode code which doesn't define any globals.  It's inside a
// function because try/catches deoptimize in certain engines.

var cachedSetTimeout;
var cachedClearTimeout;

function defaultSetTimout() {
    throw new Error('setTimeout has not been defined');
}
function defaultClearTimeout () {
    throw new Error('clearTimeout has not been defined');
}
(function () {
    try {
        if (typeof setTimeout === 'function') {
            cachedSetTimeout = setTimeout;
        } else {
            cachedSetTimeout = defaultSetTimout;
        }
    } catch (e) {
        cachedSetTimeout = defaultSetTimout;
    }
    try {
        if (typeof clearTimeout === 'function') {
            cachedClearTimeout = clearTimeout;
        } else {
            cachedClearTimeout = defaultClearTimeout;
        }
    } catch (e) {
        cachedClearTimeout = defaultClearTimeout;
    }
} ())
function runTimeout(fun) {
    if (cachedSetTimeout === setTimeout) {
        //normal enviroments in sane situations
        return setTimeout(fun, 0);
    }
    // if setTimeout wasn't available but was latter defined
    if ((cachedSetTimeout === defaultSetTimout || !cachedSetTimeout) && setTimeout) {
        cachedSetTimeout = setTimeout;
        return setTimeout(fun, 0);
    }
    try {
        // when when somebody has screwed with setTimeout but no I.E. maddness
        return cachedSetTimeout(fun, 0);
    } catch(e){
        try {
            // When we are in I.E. but the script has been evaled so I.E. doesn't trust the global object when called normally
            return cachedSetTimeout.call(null, fun, 0);
        } catch(e){
            // same as above but when it's a version of I.E. that must have the global object for 'this', hopfully our context correct otherwise it will throw a global error
            return cachedSetTimeout.call(this, fun, 0);
        }
    }


}
function runClearTimeout(marker) {
    if (cachedClearTimeout === clearTimeout) {
        //normal enviroments in sane situations
        return clearTimeout(marker);
    }
    // if clearTimeout wasn't available but was latter defined
    if ((cachedClearTimeout === defaultClearTimeout || !cachedClearTimeout) && clearTimeout) {
        cachedClearTimeout = clearTimeout;
        return clearTimeout(marker);
    }
    try {
        // when when somebody has screwed with setTimeout but no I.E. maddness
        return cachedClearTimeout(marker);
    } catch (e){
        try {
            // When we are in I.E. but the script has been evaled so I.E. doesn't  trust the global object when called normally
            return cachedClearTimeout.call(null, marker);
        } catch (e){
            // same as above but when it's a version of I.E. that must have the global object for 'this', hopfully our context correct otherwise it will throw a global error.
            // Some versions of I.E. have different rules for clearTimeout vs setTimeout
            return cachedClearTimeout.call(this, marker);
        }
    }



}
var queue = [];
var draining = false;
var currentQueue;
var queueIndex = -1;

function cleanUpNextTick() {
    if (!draining || !currentQueue) {
        return;
    }
    draining = false;
    if (currentQueue.length) {
        queue = currentQueue.concat(queue);
    } else {
        queueIndex = -1;
    }
    if (queue.length) {
        drainQueue();
    }
}

function drainQueue() {
    if (draining) {
        return;
    }
    var timeout = runTimeout(cleanUpNextTick);
    draining = true;

    var len = queue.length;
    while(len) {
        currentQueue = queue;
        queue = [];
        while (++queueIndex < len) {
            if (currentQueue) {
                currentQueue[queueIndex].run();
            }
        }
        queueIndex = -1;
        len = queue.length;
    }
    currentQueue = null;
    draining = false;
    runClearTimeout(timeout);
}

process.nextTick = function (fun) {
    var args = new Array(arguments.length - 1);
    if (arguments.length > 1) {
        for (var i = 1; i < arguments.length; i++) {
            args[i - 1] = arguments[i];
        }
    }
    queue.push(new Item(fun, args));
    if (queue.length === 1 && !draining) {
        runTimeout(drainQueue);
    }
};

// v8 likes predictible objects
function Item(fun, array) {
    this.fun = fun;
    this.array = array;
}
Item.prototype.run = function () {
    this.fun.apply(null, this.array);
};
process.title = 'browser';
process.browser = true;
process.env = {};
process.argv = [];
process.version = ''; // empty string to avoid regexp issues
process.versions = {};

function noop() {}

process.on = noop;
process.addListener = noop;
process.once = noop;
process.off = noop;
process.removeListener = noop;
process.removeAllListeners = noop;
process.emit = noop;

process.binding = function (name) {
    throw new Error('process.binding is not supported');
};

process.cwd = function () { return '/' };
process.chdir = function (dir) {
    throw new Error('process.chdir is not supported');
};
process.umask = function() { return 0; };

},{}],15:[function(require,module,exports){
/*!
 * EventEmitter v5.1.0 - git.io/ee
 * Unlicense - http://unlicense.org/
 * Oliver Caldwell - http://oli.me.uk/
 * @preserve
 */

;(function (exports) {
    'use strict';

    /**
     * Class for managing events.
     * Can be extended to provide event functionality in other classes.
     *
     * @class EventEmitter Manages event registering and emitting.
     */
    function EventEmitter() {}

    // Shortcuts to improve speed and size
    var proto = EventEmitter.prototype;
    var originalGlobalValue = exports.EventEmitter;

    /**
     * Finds the index of the listener for the event in its storage array.
     *
     * @param {Function[]} listeners Array of listeners to search through.
     * @param {Function} listener Method to look for.
     * @return {Number} Index of the specified listener, -1 if not found
     * @api private
     */
    function indexOfListener(listeners, listener) {
        var i = listeners.length;
        while (i--) {
            if (listeners[i].listener === listener) {
                return i;
            }
        }

        return -1;
    }

    /**
     * Alias a method while keeping the context correct, to allow for overwriting of target method.
     *
     * @param {String} name The name of the target method.
     * @return {Function} The aliased method
     * @api private
     */
    function alias(name) {
        return function aliasClosure() {
            return this[name].apply(this, arguments);
        };
    }

    /**
     * Returns the listener array for the specified event.
     * Will initialise the event object and listener arrays if required.
     * Will return an object if you use a regex search. The object contains keys for each matched event. So /ba[rz]/ might return an object containing bar and baz. But only if you have either defined them with defineEvent or added some listeners to them.
     * Each property in the object response is an array of listener functions.
     *
     * @param {String|RegExp} evt Name of the event to return the listeners from.
     * @return {Function[]|Object} All listener functions for the event.
     */
    proto.getListeners = function getListeners(evt) {
        var events = this._getEvents();
        var response;
        var key;

        // Return a concatenated array of all matching events if
        // the selector is a regular expression.
        if (evt instanceof RegExp) {
            response = {};
            for (key in events) {
                if (events.hasOwnProperty(key) && evt.test(key)) {
                    response[key] = events[key];
                }
            }
        }
        else {
            response = events[evt] || (events[evt] = []);
        }

        return response;
    };

    /**
     * Takes a list of listener objects and flattens it into a list of listener functions.
     *
     * @param {Object[]} listeners Raw listener objects.
     * @return {Function[]} Just the listener functions.
     */
    proto.flattenListeners = function flattenListeners(listeners) {
        var flatListeners = [];
        var i;

        for (i = 0; i < listeners.length; i += 1) {
            flatListeners.push(listeners[i].listener);
        }

        return flatListeners;
    };

    /**
     * Fetches the requested listeners via getListeners but will always return the results inside an object. This is mainly for internal use but others may find it useful.
     *
     * @param {String|RegExp} evt Name of the event to return the listeners from.
     * @return {Object} All listener functions for an event in an object.
     */
    proto.getListenersAsObject = function getListenersAsObject(evt) {
        var listeners = this.getListeners(evt);
        var response;

        if (listeners instanceof Array) {
            response = {};
            response[evt] = listeners;
        }

        return response || listeners;
    };

    function isValidListener (listener) {
        if (typeof listener === 'function' || listener instanceof RegExp) {
            return true
        } else if (listener && typeof listener === 'object') {
            return isValidListener(listener.listener)
        } else {
            return false
        }
    }

    /**
     * Adds a listener function to the specified event.
     * The listener will not be added if it is a duplicate.
     * If the listener returns true then it will be removed after it is called.
     * If you pass a regular expression as the event name then the listener will be added to all events that match it.
     *
     * @param {String|RegExp} evt Name of the event to attach the listener to.
     * @param {Function} listener Method to be called when the event is emitted. If the function returns true then it will be removed after calling.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.addListener = function addListener(evt, listener) {
        if (!isValidListener(listener)) {
            throw new TypeError('listener must be a function');
        }

        var listeners = this.getListenersAsObject(evt);
        var listenerIsWrapped = typeof listener === 'object';
        var key;

        for (key in listeners) {
            if (listeners.hasOwnProperty(key) && indexOfListener(listeners[key], listener) === -1) {
                listeners[key].push(listenerIsWrapped ? listener : {
                    listener: listener,
                    once: false
                });
            }
        }

        return this;
    };

    /**
     * Alias of addListener
     */
    proto.on = alias('addListener');

    /**
     * Semi-alias of addListener. It will add a listener that will be
     * automatically removed after its first execution.
     *
     * @param {String|RegExp} evt Name of the event to attach the listener to.
     * @param {Function} listener Method to be called when the event is emitted. If the function returns true then it will be removed after calling.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.addOnceListener = function addOnceListener(evt, listener) {
        return this.addListener(evt, {
            listener: listener,
            once: true
        });
    };

    /**
     * Alias of addOnceListener.
     */
    proto.once = alias('addOnceListener');

    /**
     * Defines an event name. This is required if you want to use a regex to add a listener to multiple events at once. If you don't do this then how do you expect it to know what event to add to? Should it just add to every possible match for a regex? No. That is scary and bad.
     * You need to tell it what event names should be matched by a regex.
     *
     * @param {String} evt Name of the event to create.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.defineEvent = function defineEvent(evt) {
        this.getListeners(evt);
        return this;
    };

    /**
     * Uses defineEvent to define multiple events.
     *
     * @param {String[]} evts An array of event names to define.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.defineEvents = function defineEvents(evts) {
        for (var i = 0; i < evts.length; i += 1) {
            this.defineEvent(evts[i]);
        }
        return this;
    };

    /**
     * Removes a listener function from the specified event.
     * When passed a regular expression as the event name, it will remove the listener from all events that match it.
     *
     * @param {String|RegExp} evt Name of the event to remove the listener from.
     * @param {Function} listener Method to remove from the event.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.removeListener = function removeListener(evt, listener) {
        var listeners = this.getListenersAsObject(evt);
        var index;
        var key;

        for (key in listeners) {
            if (listeners.hasOwnProperty(key)) {
                index = indexOfListener(listeners[key], listener);

                if (index !== -1) {
                    listeners[key].splice(index, 1);
                }
            }
        }

        return this;
    };

    /**
     * Alias of removeListener
     */
    proto.off = alias('removeListener');

    /**
     * Adds listeners in bulk using the manipulateListeners method.
     * If you pass an object as the first argument you can add to multiple events at once. The object should contain key value pairs of events and listeners or listener arrays. You can also pass it an event name and an array of listeners to be added.
     * You can also pass it a regular expression to add the array of listeners to all events that match it.
     * Yeah, this function does quite a bit. That's probably a bad thing.
     *
     * @param {String|Object|RegExp} evt An event name if you will pass an array of listeners next. An object if you wish to add to multiple events at once.
     * @param {Function[]} [listeners] An optional array of listener functions to add.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.addListeners = function addListeners(evt, listeners) {
        // Pass through to manipulateListeners
        return this.manipulateListeners(false, evt, listeners);
    };

    /**
     * Removes listeners in bulk using the manipulateListeners method.
     * If you pass an object as the first argument you can remove from multiple events at once. The object should contain key value pairs of events and listeners or listener arrays.
     * You can also pass it an event name and an array of listeners to be removed.
     * You can also pass it a regular expression to remove the listeners from all events that match it.
     *
     * @param {String|Object|RegExp} evt An event name if you will pass an array of listeners next. An object if you wish to remove from multiple events at once.
     * @param {Function[]} [listeners] An optional array of listener functions to remove.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.removeListeners = function removeListeners(evt, listeners) {
        // Pass through to manipulateListeners
        return this.manipulateListeners(true, evt, listeners);
    };

    /**
     * Edits listeners in bulk. The addListeners and removeListeners methods both use this to do their job. You should really use those instead, this is a little lower level.
     * The first argument will determine if the listeners are removed (true) or added (false).
     * If you pass an object as the second argument you can add/remove from multiple events at once. The object should contain key value pairs of events and listeners or listener arrays.
     * You can also pass it an event name and an array of listeners to be added/removed.
     * You can also pass it a regular expression to manipulate the listeners of all events that match it.
     *
     * @param {Boolean} remove True if you want to remove listeners, false if you want to add.
     * @param {String|Object|RegExp} evt An event name if you will pass an array of listeners next. An object if you wish to add/remove from multiple events at once.
     * @param {Function[]} [listeners] An optional array of listener functions to add/remove.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.manipulateListeners = function manipulateListeners(remove, evt, listeners) {
        var i;
        var value;
        var single = remove ? this.removeListener : this.addListener;
        var multiple = remove ? this.removeListeners : this.addListeners;

        // If evt is an object then pass each of its properties to this method
        if (typeof evt === 'object' && !(evt instanceof RegExp)) {
            for (i in evt) {
                if (evt.hasOwnProperty(i) && (value = evt[i])) {
                    // Pass the single listener straight through to the singular method
                    if (typeof value === 'function') {
                        single.call(this, i, value);
                    }
                    else {
                        // Otherwise pass back to the multiple function
                        multiple.call(this, i, value);
                    }
                }
            }
        }
        else {
            // So evt must be a string
            // And listeners must be an array of listeners
            // Loop over it and pass each one to the multiple method
            i = listeners.length;
            while (i--) {
                single.call(this, evt, listeners[i]);
            }
        }

        return this;
    };

    /**
     * Removes all listeners from a specified event.
     * If you do not specify an event then all listeners will be removed.
     * That means every event will be emptied.
     * You can also pass a regex to remove all events that match it.
     *
     * @param {String|RegExp} [evt] Optional name of the event to remove all listeners for. Will remove from every event if not passed.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.removeEvent = function removeEvent(evt) {
        var type = typeof evt;
        var events = this._getEvents();
        var key;

        // Remove different things depending on the state of evt
        if (type === 'string') {
            // Remove all listeners for the specified event
            delete events[evt];
        }
        else if (evt instanceof RegExp) {
            // Remove all events matching the regex.
            for (key in events) {
                if (events.hasOwnProperty(key) && evt.test(key)) {
                    delete events[key];
                }
            }
        }
        else {
            // Remove all listeners in all events
            delete this._events;
        }

        return this;
    };

    /**
     * Alias of removeEvent.
     *
     * Added to mirror the node API.
     */
    proto.removeAllListeners = alias('removeEvent');

    /**
     * Emits an event of your choice.
     * When emitted, every listener attached to that event will be executed.
     * If you pass the optional argument array then those arguments will be passed to every listener upon execution.
     * Because it uses `apply`, your array of arguments will be passed as if you wrote them out separately.
     * So they will not arrive within the array on the other side, they will be separate.
     * You can also pass a regular expression to emit to all events that match it.
     *
     * @param {String|RegExp} evt Name of the event to emit and execute listeners for.
     * @param {Array} [args] Optional array of arguments to be passed to each listener.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.emitEvent = function emitEvent(evt, args) {
        var listenersMap = this.getListenersAsObject(evt);
        var listeners;
        var listener;
        var i;
        var key;
        var response;

        for (key in listenersMap) {
            if (listenersMap.hasOwnProperty(key)) {
                listeners = listenersMap[key].slice(0);

                for (i = 0; i < listeners.length; i++) {
                    // If the listener returns true then it shall be removed from the event
                    // The function is executed either with a basic call or an apply if there is an args array
                    listener = listeners[i];

                    if (listener.once === true) {
                        this.removeListener(evt, listener.listener);
                    }

                    response = listener.listener.apply(this, args || []);

                    if (response === this._getOnceReturnValue()) {
                        this.removeListener(evt, listener.listener);
                    }
                }
            }
        }

        return this;
    };

    /**
     * Alias of emitEvent
     */
    proto.trigger = alias('emitEvent');

    /**
     * Subtly different from emitEvent in that it will pass its arguments on to the listeners, as opposed to taking a single array of arguments to pass on.
     * As with emitEvent, you can pass a regex in place of the event name to emit to all events that match it.
     *
     * @param {String|RegExp} evt Name of the event to emit and execute listeners for.
     * @param {...*} Optional additional arguments to be passed to each listener.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.emit = function emit(evt) {
        var args = Array.prototype.slice.call(arguments, 1);
        return this.emitEvent(evt, args);
    };

    /**
     * Sets the current value to check against when executing listeners. If a
     * listeners return value matches the one set here then it will be removed
     * after execution. This value defaults to true.
     *
     * @param {*} value The new value to check for when executing listeners.
     * @return {Object} Current instance of EventEmitter for chaining.
     */
    proto.setOnceReturnValue = function setOnceReturnValue(value) {
        this._onceReturnValue = value;
        return this;
    };

    /**
     * Fetches the current value to check against when executing listeners. If
     * the listeners return value matches this one then it should be removed
     * automatically. It will return true by default.
     *
     * @return {*|Boolean} The current value to check for or the default, true.
     * @api private
     */
    proto._getOnceReturnValue = function _getOnceReturnValue() {
        if (this.hasOwnProperty('_onceReturnValue')) {
            return this._onceReturnValue;
        }
        else {
            return true;
        }
    };

    /**
     * Fetches the events object and creates one if required.
     *
     * @return {Object} The events storage object.
     * @api private
     */
    proto._getEvents = function _getEvents() {
        return this._events || (this._events = {});
    };

    /**
     * Reverts the global {@link EventEmitter} to its previous value and returns a reference to this version.
     *
     * @return {Function} Non conflicting EventEmitter class.
     */
    EventEmitter.noConflict = function noConflict() {
        exports.EventEmitter = originalGlobalValue;
        return EventEmitter;
    };

    // Expose the class either via AMD, CommonJS or the global object
    if (typeof define === 'function' && define.amd) {
        define(function () {
            return EventEmitter;
        });
    }
    else if (typeof module === 'object' && module.exports){
        module.exports = EventEmitter;
    }
    else {
        exports.EventEmitter = EventEmitter;
    }
}(this || {}));

},{}]},{},[1])(1)
});