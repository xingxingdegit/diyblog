    var socket = io();
    socket.on('connect', function() {
        socket.emit('my event', {data: 'is test, is connected'});
        console.log('is connect')
    });
    socket.on('disconnect', function() {
        
        console.log('disconnect')
    })
    socket.on('message', function(data) {
        console.log('message')
        console.log(data)
        console.log('message')
    })