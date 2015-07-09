(function(global) {

  "use strict";

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
            controls: 0,
            rel: 0,
            showInfo: 0
          }
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


    $(document).on("onBeforeClose", ".overlay", function() {
      initializeYoutubeApi();
    });

    initializeYoutubeApi();

  });

})(window);

