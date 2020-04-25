var tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

function onYouTubeIframeAPIReady() {

var player = null;
var timestamp = 0
function createPlayer(yt_id, timestamp) {
    player = new YT.Player('player', {
      height: '390',
      width: '640',
      videoId: yt_id,
      playerVars: { 'autoplay': 1, 'controls': 0, 'disablekb': 1},
      events: {
        'onReady': onPlayerReady,
        'onStateChange': onPlayerStateChange
      }
    });
}

function onPlayerReady(event) {
    event.target.playVideo();
    event.target.seekTo(timestamp, true)
}

var queue = new Vue({
  el: '#queue',
  data: {
    items: []
  },
  methods: {
    dragStart:function(event)  {
      event.preventDefault()
    },
    dragging:function(event) {
      event.preventDefault()
    },
    allowDrop: function(event) {
      event.preventDefault();
    },
    drop: function(event) {
      event.preventDefault();
      var data = event.dataTransfer.getData("Text");
      processInput(data);
    }
  }
})

var history = new Vue({
  el: '#history',
  data: {
    items: []
  }
})

var submitField = new Vue({
  el: '#url',
  data: {
    // declare message with an empty value
    url: ''
  },
  methods: {
    submit: function (event) {
      if (event) {
            processInput(this.url)
      }
    }
  }
})

var socket = io();

socket.on('connect', function() {
    console.log("Connected")
    socket.emit('message', 'New client connected');
    socket.emit('requestState')
});

socket.on('state', (state) => {
    console.log(state)

    queue.items = []
    state.queue.forEach(function(entry) {
        queue.items.push(entry)
    });

    history.items = []
    state.history.forEach(function(entry) {
        history.items.push(entry)
    });

    timestamp = parseFloat(state.timestamp)

    if (state.currentId === "")
        return

    if (player == null)
    {
        createPlayer(state.currentId, timestamp)
    }
    else if (player.getVideoData().video_id != state.currentId ||
             player.getPlayerState() == YT.PlayerState.ENDED)
    {
        player.loadVideoById(state.currentId, timestamp)
        M.toast({html: 'Playing: ' + state.currentTitle})
    }
    else
    {
        if( player.getCurrentTime() - 2 > timestamp ||
            player.getCurrentTime() + 2 < timestamp)
            player.seekTo(timestamp, true)
    }
});

socket.on('message', (msg) => {
    console.log(msg)
    M.toast({html: '' + msg})
});

var nextButton = new Vue({
  el: '#next',
  methods: {
    next: function (event) {
      if (event) {
        if (player !== null)
            socket.emit('requestSkip', '' + player.getVideoData().video_id)
        else
            socket.emit('requestSkip', '')
      }
    }
  }
})

updateTimestampTimer = null
function onPlayerStateChange(event) {
    if (event.data == YT.PlayerState.ENDED) {
        socket.emit('requestNext', '' + player.getVideoData().video_id)
    }
    if (event.data == YT.PlayerState.PLAYING) {
        clearTimeout(updateTimestampTimer);
        updateTimestampTimer = setTimeout(updateTimestamp, 1000);
    }
}

function updateTimestamp()
{
    // Only update when playing
    if (player.getPlayerState() == YT.PlayerState.PLAYING)
    {
        socket.emit('requestUpdateTimestamp', {id: player.getVideoData().video_id, timestamp: player.getCurrentTime()})
        setTimeout(updateTimestamp, 1000);
    }
}

function processInput(input) {
    var regex = /^.*(v=|be\/)(.{11}).*$/g;
    var match = regex.exec(input);

    if (match.length > 2)
    {
        var found_id = match[2]
        console.log("Entered:   " + input)
        console.log("Match:     " + found_id);

        //M.toast({html: 'Requesting: ' + found_id})
        submitField.url = ''

        socket.emit('addUrl', found_id);
    }
    else
    {
        M.toast({html: 'Failed to parse url'})
    }
}

} // onYouTubeIframeAPIReady



//
