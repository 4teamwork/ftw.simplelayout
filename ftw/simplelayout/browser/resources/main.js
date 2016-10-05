(function(global, $) {

  "use strict";

  function markLinks(element) {
    if (typeof global.external_links_open_new_window === "string" && global.external_links_open_new_window.toLowerCase() === "true") {
      var url = window.location.protocol + "//" + window.location.host;
      // all http links (without the link-plain class), not within this site
      $("a[href^=\"http\"]:not(.link-plain):not([href^=\"" + url + "\"])", element).attr("target", "_blank");
    }
  }

  function StateKeeper() {

    var counter = 0;

    function parseQueryString(queryString) {
      if(!queryString) {
        return {};
      }
      var params = {};
      var queries;
      var temp;
      var i;
      var l;
      queries = queryString.split("&");
      for (i = 0, l = queries.length; i < l; i++) {
        temp = queries[i].split("=");
        params[temp[0]] = temp[1];
      }
      return params;
    }

    function parseURL(url) {
      url = url || document.URL;
      var parser = document.createElement("a");
      parser.href = url;
      return parser;
    }

    function restore() { counter = parseInt(global.localStorage.getItem("sl-state-counter"), 10) || 0; }

    function createURL() {
      var url = parseURL();
      var queryString = parseQueryString(url.search.replace(/^\?/, ""));
      queryString["sl-state-counter"] = counter;
      return url.protocol + "//" + url.host + url.pathname.replace(/^\/?/, '/') + "?" + global.decodeURIComponent($.param(queryString)) + url.hash;
    }

    function update() {
      counter += 1;
      global.localStorage.setItem("sl-state-counter", counter);
      global.history.pushState({}, "", createURL());
    }

    restore();

    return Object.freeze({ update: update });

  }

  var statekeeper = StateKeeper();

  var init = function() {

    var target = $("body");

    var baseUrl = $("body").data("base-url") ? $("body").data("base-url") + "/" : $("base").attr("href");

    var isUploading = function() { return global["xhr_" + $(".main-uploader").attr("id")]._filesInProgress > 0; };

    var initializeColorbox = function() {
      if($(".colorboxLink").length > 0) {
        if (typeof global.ftwColorboxInitialize !== "undefined" && $.isFunction(global.ftwColorboxInitialize)) {
          global.ftwColorboxInitialize();
        }
      }
    };

    var options = $.extend({
      canChangeLayout: false,
      canEdit: false,
      endpoints: {
        toolbox: baseUrl + "sl-toolbox-view",
        state: baseUrl + "sl-ajax-save-state-view"
      }
    }, $(".sl-simplelayout").data("slSettings"));

    if (!options.canEdit) { return false; }

    var deleteOverlay = new global.FormOverlay({cssclass: "overlay-delete"});
    var editOverlay = new global.FormOverlay({cssclass: "overlay-edit"});
    var uploadOverlay = new global.FormOverlay({ cssclass: "overlay-upload", disableClose: isUploading });
    var addOverlay = new global.FormOverlay({cssclass: "overlay-add"});
    var toolbox;
    var simplelayout;

    var loadComponents = function(callback) {
      $.get(options.endpoints.toolbox).done(function(data, textStatus, request) {
        var contentType = request.getResponseHeader("Content-Type");
        if (contentType.indexOf("application/json") < 0) {
          throw new Error("Bad response [content-type: " + contentType + "]");
        }
        callback(data);
      });
    };

    var saveState = function() {
      var state = {};
      $(".sl-simplelayout").each(function(manIdx, manager) {
        state[manager.id] = [];
        $(".sl-layout", manager).each(function(layIdx, layout) {
          state[manager.id][layIdx] = {};
          state[manager.id][layIdx].cols = [];
          $(".sl-column", layout).each(function(colIdx, column) {
            state[manager.id][layIdx].cols[colIdx] = { blocks: [] };
            $(".sl-block", column).each(function(bloIdx, block) {
              state[manager.id][layIdx].cols[colIdx].blocks[bloIdx] = { uid: $(block).data().represents };
            });
          });
        });
      });
      $.post(options.endpoints.state, {
        data: JSON.stringify(state),
        _authenticator: $('input[name="_authenticator"]').val()
      });
    };

    loadComponents(function(settings) {

      settings = $.extend(settings, options);

      toolbox = new global.Toolbox(settings);
      toolbox.attachTo(target);

      simplelayout = new global.Simplelayout({ toolbox: toolbox, editLayouts: settings.canChangeLayout });

      simplelayout.on("blockInserted", function(block) {
        var layout = block.parent;
        if(layout.hasBlocks()) {
          layout.toolbar.disable("delete");
        }
        if(block.type) {
          addOverlay.load(toolbox.options.blocks[block.type].formUrl);
        }
        addOverlay.onSubmit(function(data) {
          block.represents = data.uid;
          block.data({ represents: data.uid, url: data.url });
          block.content(data.content);
          block.commit();
          saveState();
          initializeColorbox();
          this.close();
        });
        addOverlay.onCancel(function() {
          if(!block.committed) {
            block.remove().delete();
          }
        });
      });

      simplelayout.restore(target);

      simplelayout.on("block-committed", function(block) {
        block.element.on("animationend webkitAnimationEnd", function() { block.element.removeClass("dropped"); });
        block.element.addClass("dropped");
      });

      simplelayout.on("blockDeleted", function(block) {
        var layout = block.parent;
        if(!layout.hasBlocks()) {
          layout.toolbar.enable("delete");
        }
        statekeeper.update();
      });

      simplelayout.on("layoutInserted", function(layout) {
        layout.commit();
        toolbox.blocksEnabled(true);
        saveState();
      });

      simplelayout.on("layoutDeleted", function(layout) {
        if(!layout.parent.hasLayouts()) {
          toolbox.blocksEnabled(false);
        }
        saveState();
      });

      simplelayout.on("blockMoved", function() { saveState(); });

      simplelayout.on("beforeBlockMoved", function(beforeBlock) {
        simplelayout.on("blockMoved", function(block) {
          var beforeLayout = beforeBlock.parent;
          var currentLayout = block.parent;
          if(beforeLayout.hasBlocks()) {
            beforeLayout.toolbar.disable("delete");
          } else {
            beforeLayout.toolbar.enable("delete");
          }
          if(currentLayout.hasBlocks()) {
            currentLayout.toolbar.disable("delete");
          } else {
            currentLayout.toolbar.enable("delete");
          }
        });
      });

      simplelayout.on("layoutMoved", function() { saveState(); });

      simplelayout.on("blockReplaced", function(block) {
        $(document).trigger("blockContentReplaced", arguments);
        statekeeper.update();
        markLinks(block.element);
      });

      $(toolbox.element).on("click", ".sl-toolbox-block, .sl-toolbox-layout", function() {
        toolbox.triggerHint($(this), $("#default"));
      });

    });

    $(global.document).on("click", ".sl-layout .delete", function() {
      var layout = $(this).parents(".sl-layout").data().object;
      if(!layout.hasBlocks()) {
        layout.remove().delete();
      }
    });

    $(global.document).on("click", ".sl-block .delete", function(event) {
      event.preventDefault();
      var block = $(this).parents(".sl-block").data().object;
      deleteOverlay.load($(this).attr("href"), { data: JSON.stringify({ block: block.represents }) });
      deleteOverlay.onSubmit(function() {
        if(block.committed) {
          block.remove().delete();
        }
        saveState();
        this.close();
      });
    });

    $(global.document).on("click", ".sl-block .edit", function(event) {
      event.preventDefault();
      var block = $(this).parents(".sl-block").data().object;
      editOverlay.load($(this).attr("href"), {"data": JSON.stringify({ "block": block.represents })});
      editOverlay.onSubmit(function(data) {
        block.content(data.content);
        initializeColorbox();
        this.close();
      });
    });

    $(global.document).on("click", ".sl-block .redirect", function(event) {
      event.preventDefault();
      var block = $(this).parents(".sl-block").data().object;
      window.location.href = block.data().url + $(this).attr("href");
    });

    $(global.document).on("click", ".server-action", function(event) {
      event.preventDefault();
      var block = $(this).parents(".sl-block").data().object;
      var payLoad = { uid: block.represents };
      var action = $(this);
      $.extend(payLoad, action.data());
      var configRequest = $.post(action.attr("href"), { "data": JSON.stringify(payLoad) });
      configRequest.done(function(blockContent) {
        block.content(blockContent);
      });
    });

    $(global.document).on("click", ".sl-block .upload", function(event) {
      event.preventDefault();
      var block = $(this).parents(".sl-block").data().object;
      uploadOverlay.load($(this).attr("href"), {"data": JSON.stringify({ "block": block.represents })}, function(){
        var self = this;
        global.Browser.onUploadComplete = function(){ return; };
        self.element.on("click", "#button-upload-done", function(uploadEvent) {
          uploadEvent.preventDefault();
          self.onFormCancel.call(self);
        });

      });
      uploadOverlay.onCancel(function(){
        var payLoad = {};
        var action = $(this);
        payLoad.uid = block.represents;
        $.extend(payLoad, action.data());
        var configRequest = $.post("./sl-ajax-reload-block-view", {"data": JSON.stringify(payLoad)});
        configRequest.done(function(blockContent) {
          block.content(blockContent);
          initializeColorbox();
        });
      });
    });

  };

  $(init);

}(window, jQuery));
