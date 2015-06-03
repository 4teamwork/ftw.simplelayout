$(function(){

  var youtube_player = {
    playVideo: function(container, config) {
        youtube_player.loadPlayer(container, config);
      },

    loadPlayer: function(container, config) {

      var defaults = {
        videoId: null,
        playerVars: {
          autoplay: 0,
          controls: 0,
          rel: 0,
          showInfo: 0
        }};

        options = $.extend(defaults, config);

      new YT.Player(container, options);
    }
  };


  initialize_youtube_api = function(callback){
    var youtube_videos = $('.sl-youtube-video');
    if (youtube_videos.length){

      window.onYouTubePlayerAPIReady = function(){
          youtube_videos.each(function(i, element){
            var video = $(element);
            youtube_player.playVideo(video.attr('id'), video.data('youtube'));
          });
       };

      if (typeof YT === 'undefined' || typeof YT.Player === 'undefined'){
        $.getScript('//www.youtube.com/iframe_api');
      } else {
        window.onYouTubePlayerAPIReady();
      }
    }
  };


  $(document).on('onBeforeClose', '.overlay', function(){
    initialize_youtube_api();
  });

  initialize_youtube_api();

});