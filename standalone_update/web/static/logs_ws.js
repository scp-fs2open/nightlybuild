(function() {
    var socket = io({transports: ['websocket']});
    var statusEl = document.getElementById('ws-status');
    var panels = {};
    ['standalone', 'multi'].forEach(function(id) {
        panels[id] = document.getElementById('log-' + id);
    });

    socket.on('connect', function() {
        if (statusEl) statusEl.textContent = 'Live (connected)';
    });

    socket.on('disconnect', function() {
        if (statusEl) statusEl.textContent = 'Disconnected \u2014 reconnecting...';
    });

    ['standalone', 'multi'].forEach(function(id) {
        socket.on('game_log_lines_' + id, function(msg) {
            var el = panels[id];
            if (!el) return;
            el.textContent += msg.data;
            el.scrollTop = el.scrollHeight;
        });

        socket.on('game_log_truncated_' + id, function() {
            var el = panels[id];
            if (el) el.textContent = '';
        });
    });
})();
