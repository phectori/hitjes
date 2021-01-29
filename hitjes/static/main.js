var tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);


// Global scope
var player = null
var playerState = -1
var playerCurrentVideoId = 0
var playerReady = false
var timestamp = 0
var socket = null

function onYouTubeIframeAPIReady() {

function createPlayer(yt_id, timestamp) {
    var p = new YT.Player('player', {
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
    playerReady = true;
    player = event.target;

    event.target.playVideo();
    event.target.seekTo(timestamp, true)
}

var search = new Vue({
  el: '#search',
  data: {
    items: [],
    show: false
  },
  methods: {
    submit: function (id) {
      if (id) {
        socket.emit('add_url', id);
        this.items = [];
        this.show = false;
      }
    }
  }
})

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

socket = io();

socket.on('connect', function() {
    console.log("Connected")
    socket.emit('message', 'New client connected');
    socket.emit('request_state')
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
});

socket.on('search_results', (search_results) => {
  console.log(search_results)
  
  search.show = true;

  search.items = []
  search_results.forEach(function(entry) {
    search.items.push(entry)
  });
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
            socket.emit('request_skip', '' + playerCurrentVideoId)
        else
            socket.emit('request_skip', '')
      }
    }
  }
})

updateTimestampTimer = null
function onPlayerStateChange(event) {
    playerState = event.data
    if (event.data == YT.PlayerState.ENDED) {
        socket.emit('request_next', '' + playerCurrentVideoId)
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
        socket.emit('request_update_timestamp', {id: playerCurrentVideoId, timestamp: player.getCurrentTime()})
        setTimeout(updateTimestamp, 1000);
    }
}

function processInput(input) {
    var regex = /^.*(v=|be\/)(.{11}).*$/g;
    var match = regex.exec(input);

    if (match != null && match.length > 2)
    {
        var found_id = match[2]
        console.log("Entered:   " + input)
        console.log("Match:     " + found_id);

        //M.toast({html: 'Requesting: ' + found_id})
        submitField.url = ''

        socket.emit('add_url', found_id);
    }
    else
    {
        M.toast({html: 'No url, searching'})
        socket.emit('search', input);
    }
}

} // onYouTubeIframeAPIReady



//
