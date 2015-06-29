var port = parseInt(process.argv[2] || 9001);

var io = require('socket.io').listen(port);

io.set('log level', 1);
io.sockets.on('connection', function (socket) {
  console.log('client connected!');

  socket.on('room', function(room) {
    console.log('got <room> event emitting <sync-room>. room.id =', room.id);
    socket.broadcast.emit('sync-room', room);
  });
});
