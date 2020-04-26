var tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

function onYouTubeIframeAPIReady() {

var player = null
var playerState = -1
var playerCurrentVideoId = 0
var playerReady = false
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
    playerReady = true
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

var listenerCounter = new Vue({
  el: '#listenerCounter',
  data: {
    clients: []
  }
})

var socket = io();

socket.on('connect', function() {
    console.log("Connected")
    socket.emit('message', 'New client connected');
    socket.emit('requestState')
});

socket.on('state', (newState) => {
    console.log(newState)

    queue.items = []
    newState.queue.forEach(function(entry) {
        queue.items.push(entry)
    });

    history.items = []
    newState.history.forEach(function(entry) {
        history.items.push(entry)
    });

    listenerCounter.clients = newState.clients

    timestamp = parseFloat(newState.timestamp)

    if (newState.currentId === "")
        return

    if (!playerReady)
    {
        createPlayer(newState.currentId, timestamp)
        playerCurrentVideoId = newState.currentId
    }
    else if (playerCurrentVideoId != newState.currentId ||
             playerState == YT.PlayerState.ENDED)
    {
        player.loadVideoById(newState.currentId, timestamp)
        M.toast({html: 'Playing: ' + newState.currentTitle})
        playerCurrentVideoId = newState.currentId
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
    playerState = event.data
    if (event.data == YT.PlayerState.ENDED) {
        socket.emit('requestNext', '' + playerCurrentVideoId)
    }
    if (event.data == YT.PlayerState.PLAYING) {
        clearTimeout(updateTimestampTimer);
        updateTimestampTimer = setTimeout(updateTimestamp, 1000);
    }
}

function updateTimestamp()
{
    if (!playerReady)
        return;

    // Only update when playing
    if (playerState == YT.PlayerState.PLAYING)
    {
        socket.emit('requestUpdateTimestamp', {id: playerCurrentVideoId, timestamp: player.getCurrentTime()})
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
