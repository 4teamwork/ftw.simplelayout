(function(global) {

  "use strict";

  // Return function that will be only called during a free painting loop
  function throttle(func) { return function() { window.requestAnimationFrame(func); }; }

  $(window).on("resize", throttle(resizeAll));

  var ratios = {};

  function resizeAll() { $.map($(".sl-youtube-video"), resizeYoutubePlayer); }

  function onPlayerReady(player) {
    var iframe = player.target.a;

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
            showInfo: 0
          },
          events: { "onReady": onPlayerReady }
        };

        var options = $.extend(defaults, config);

        new global.YT.Player(container, options);
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

        if (typeof YT === "undefined" || typeof global.YT.Player === "undefined") {
          $.getScript("//www.youtube.com/iframe_api");
        } else {
          window.onYouTubePlayerAPIReady();
        }
      }
    };


    $(document).on("onBeforeClose", ".overlay", initializeYoutubeApi);

    initializeYoutubeApi();

  });

})(window);

