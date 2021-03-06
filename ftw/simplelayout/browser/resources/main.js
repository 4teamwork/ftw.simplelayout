(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(["jquery", "ftw.simplelayout"], factory);
  } else {
    factory(root.jQuery, root.ftw.simplelayout);
  }
}(typeof self !== 'undefined' ? self : this, function ($, ftwsimplelayout) {
  var global = window;
  "use strict";

  // Disable inline validation of the Plone forms in the overlay.
  $(document).on('onLoad OverlayContentReloaded', '.overlay', function(){
    $('.z3cformInlineValidation').removeClass('z3cformInlineValidation');
  });

  function markLinks(element) {
    if (typeof global.external_links_open_new_window === "string" && global.external_links_open_new_window.toLowerCase() === "true") {
      var url = window.location.protocol + "//" + window.location.host;
      // all http links (without the link-plain class), not within this site
      $("a[href^=\"http\"]:not(.link-plain):not([href^=\"" + url + "\"])", element).attr("target", "_blank");
    }
  }

  function inAliasblock(idx, element) {
    return $(element).closest('.sl-alias-block').length === 0;
  }

  function initDropZone(element) {
    var target = $(element).find('.filedropzone');
    if (target.length === 0) {
      return;
    }
    var button = target.next();
    target.dropzone({
      url: target.data('endpoint'),
      autoProcessQueue: false,
      parallelUploads: 1,
      uploadMultiple: false,
      previewTemplate: $(element).find('#dropzone-tmpl').html(),
      init: function () {
        var dropzoneObj = this;
        button.on('click', function(event){
          event.stopPropagation();
          event.preventDefault();
          dropzoneObj.processQueue();
        });
        dropzoneObj.on("success", function(file) {
          dropzoneObj.removeFile(file);
          dropzoneObj.options.autoProcessQueue = true;
        });
        dropzoneObj.on("error", function(file, response, xhr) {
          if (xhr !== null) {
            $(file.previewElement).addClass("dz-error").find('.dz-error-message').text(response.error); 
          }
          dropzoneObj.options.autoProcessQueue = true;
        });
        dropzoneObj.on('addedfile', function (file) {
          var timestamp = new Date().getTime();
          var unique_field_prefix = file.name + '_' + timestamp;
          $(file.previewElement).find('.dz-file-metadata').children('input').each(function() {
            var new_id = $(this).attr('id').replace('MAKEUNIQUE', unique_field_prefix);
            $(this).attr('id', new_id);
            if ($(this).attr('name') == 'title') {
              $(this).val(file.name);
            }
          });
          $(file.previewElement).find('.dz-file-metadata').children('label').each(function() {
            var new_for = $(this).attr('for').replace('MAKEUNIQUE', unique_field_prefix);
            $(this).attr('for', new_for);
          });
        });
      },
    });

    var dropzoneObj = target[0].dropzone;

    dropzoneObj.on('sending', function(file, xhr, formData){
      var title = file.previewElement.querySelector("input[name='title']");
      var description = file.previewElement.querySelector("input[name='description']");
      formData.append("title", $(title).val());
      formData.append("description", $(description).val());
      formData.append('_authenticator', $('[name="_authenticator"]').val());
    });
    dropzoneObj.on('queuecomplete', function(){
      var block = target.parents(".sl-block").data().object;
      var payLoad = { uid: block.represents };
      var configRequest = $.post('./sl-ajax-reload-block-view', { "data": JSON.stringify(payLoad) });
      configRequest.done(function(blockContent) {
        dropzoneObj.options.autoProcessQueue = false;
        var dropzone = target.parents(".sl-block").find('.dropzonewrapper').detach();
        block.content(blockContent);
        block.element.find('.dropzonewrapper').replaceWith(dropzone);
      });
    });
  }

  $(document).ready(function(){
    $('.sl-block').filter(inAliasblock).each(function(){
      initDropZone(this);
    });
  });


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

    var baseUrl = $("base").length === 1 ? $("base").attr("href") : $("body").data("base-url") + "/";

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
    var addOverlay = new global.FormOverlay({cssclass: "overlay-add"});
    var cropImageOverlay = new global.FormOverlay({cssclass: "crop-image"});
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
        $(".sl-layout", manager).filter(inAliasblock).each(function(layIdx, layout) {
          state[manager.id][layIdx] = {};
          state[manager.id][layIdx].cols = [];
          state[manager.id][layIdx].config = $(layout).data().object.config();
          $(".sl-column", layout).filter(inAliasblock).each(function(colIdx, column) {
            state[manager.id][layIdx].cols[colIdx] = { blocks: [] };
            $(".sl-block", column).filter(inAliasblock).each(function(bloIdx, block) {
              state[manager.id][layIdx].cols[colIdx].blocks[bloIdx] = { uid: $(block).data().represents };
            });
          });
        });
      });
      $.post(options.endpoints.state, {
        data: JSON.stringify(state),
        _authenticator: $('input[name="_authenticator"]').val()
      }).done(function() {
        $(document).trigger('sl-state-updated');
      });
    };

    loadComponents(function(settings) {

      settings = $.extend(settings, options);

      toolbox = new ftwsimplelayout.toolbox(settings);
      toolbox.attachTo(target);

      simplelayout = new ftwsimplelayout.simplelayout({ toolbox: toolbox, editLayouts: settings.canChangeLayout });

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
          block.content(data.content, data.id);
          block.commit();
          saveState();
          initializeColorbox();
          initDropZone(block.element);
          this.close();
          $(document).trigger('block-added', [block]);
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
        toolbox.blocksEnabled(true);
      });

      simplelayout.on("layout-committed", function() {
        statekeeper.update();
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

    });

    $(global.document).on("click", ".sl-layout .delete", function() {
      var layout = $(this).parents(".sl-layout").data().object;
      if(!layout.hasBlocks()) {
        layout.remove().delete();
      }
    });

    $(global.document).on("click", ".sl-layout .reload", function(event) {
      event.preventDefault();
      var action = $(this);
      var layout = action.parents(".sl-layout").data().object;
      var container = layout.parent;
      var payload = {
        name: container.represents,
        layoutindex: container.element.find('.sl-layout').index(layout.element)
      };
      $.extend(payload, { config: action.data() });

      var configRequest = $.post(action.attr("href"), { "data": JSON.stringify(payload) });
      configRequest.done(function(layoutdata) {
        layout.content(layoutdata.content);
      });
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
        $(document).trigger('block-edited', [block]);
        block.content(data.content);
        initializeColorbox();
        initDropZone(block.element);
        this.close();
      });
    });

    $(global.document).on("click", ".sl-block .crop-image", function(event) {
      event.preventDefault();
      var block = $(this).parents(".sl-block").data().object;
      var blockUID = $(this).data('uid');
      if (!blockUID) {
        blockUID = block.represents;
      };

      var cropper = null;
      cropImageOverlay.load($(this).attr("href"), {"data": JSON.stringify({ "block": blockUID })}, function() {
        if ($('.croppingImage ', this.element).length > 0) {
          cropper = new ftwsimplelayout.Cropper($('.imageCropperWrapper', this.element)[0])
          cropper.run();
        }
      });
      cropImageOverlay.onSubmit(function(data) {
        $(document).trigger('block-edited', [block]);
        block.content(data.content);
        initializeColorbox();
        this.close();
      });
      cropImageOverlay.onProcessFormData(function(form) {
        var fd =  new global.FormData(form);
        if (cropper !== null) {
          cropper.processFormData(fd)
        }
        return fd
      })
    });

    $(global.document).on("click", ".sl-block .inneredit", function(event) {
      event.preventDefault();
      var block = $(this).parents(".sl-block").data().object;
      editOverlay.load($(this).attr("href"), {"data": JSON.stringify({ "uid": $(this).data('uid') })});
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

    $(global.document).on("click", ".block-server-action", function(event) {
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

  };

  $(init);

}));
