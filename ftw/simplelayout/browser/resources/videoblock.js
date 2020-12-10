(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    require(["jquery"], factory);
  } else {
    factory(root.jQuery);
  }
}(typeof self !== 'undefined' ? self : this, function ($) {
  "use strict";

  // Return function that will be only called during a free painting loop
  function throttle(func) { return function() { window.requestAnimationFrame(func); }; }

  $(window).on("resize", throttle(resizeAll));

  var ratios = {};

  function resizeAll() { $.map($(".sl-youtube-video"), resizeYoutubePlayer); }

  function onPlayerReady(player) {
    var iframe = player.target.getIframe();

    ratios[iframe.id] = ratios[iframe.id] || iframe.height/iframe.width;

    iframe.width = "100%";
    resizeYoutubePlayer(iframe);
    iframe.style.visibility = "visible";
  };

  function resizeYoutubePlayer(iframe) {
    iframe.height = iframe.offsetWidth * ratios[iframe.id];
  }

  $(function() {

    var youtubePlayer = {
      playVideo: function(container, config) {
        youtubePlayer.loadPlayer(container, config);
      },

      loadPlayer: function(container, config) {

        var defaults = {
          videoId: null,
          playerVars: {
            autoplay: 0,
            controls: 1,
            rel: 0,
            showInfo: 0,
            origin:window.location.origin
          },
          events: { "onReady": onPlayerReady }
        };

        var options = $.extend(defaults, config);

        // If there are more options this could be implemented in a generic way
        if (options['playerVars-start'] !== undefined) {
          options.playerVars.start = options['playerVars-start'];
        }

        new window.YT.Player(container, options);
      }
    };


    var initializeYoutubeApi = function() {
      var youtubeVideos = $(".sl-youtube-video");
      if (youtubeVideos.length) {

        window.onYouTubePlayerAPIReady = function() {
          youtubeVideos.each(function(i, element) {
            var video = $(element);
            youtubePlayer.playVideo(video.attr("id"), video.data("youtube"));
          });
        };

        if (typeof YT === "undefined" || typeof window.YT.Player === "undefined") {
          $.getScript("//www.youtube.com/iframe_api");
        } else {
          window.onYouTubePlayerAPIReady();
        }
      }
    };


    $(document).on("onBeforeClose", ".overlay", initializeYoutubeApi);

    initializeYoutubeApi();

  });
}));

