var tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

function onYouTubeIframeAPIReady() {
    createPlayer();
}

var player;
function createPlayer() {
    player = new YT.Player('player', {
      height: '390',
      width: '640',
      videoId: 't0bPrt69rag',
      playerVars: { 'autoplay': 0, 'controls': 0, 'disablekb': 1},
      events: {
        'onReady': onPlayerReady,
        'onStateChange': onPlayerStateChange
      }
    });
}

function onPlayerReady(event) {
event.target.seekTo(0, true);
//event.target.playVideo();
}

var done = false;
function onPlayerStateChange(event) {
// if (event.data == YT.PlayerState.PLAYING && !done) {
//   setTimeout(stopVideo, 6000);
//   done = true;
// }
}
function stopVideo() {
    player.stopVideo();
}

var socket = io();
socket.on('connect', function() {
    socket.emit('my event', {data: 'I\'m connected!'});
});