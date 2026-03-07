(function() {
    var socket = io({transports: ['websocket']});
    var statusEl = document.getElementById('ws-status');

    // Discover panel IDs from the DOM (elements with id="log-<panel_id>")
    var panelEls = document.querySelectorAll('[id^="log-"]');
    var panels = {};
    panelEls.forEach(function(el) {
        var id = el.id.replace(/^log-/, '');
        panels[id] = el;
    });

    socket.on('connect', function() {
        socket.emit('join_page', 'logs');
        if (statusEl) statusEl.textContent = 'Live (connected)';
    });

    socket.on('disconnect', function() {
        if (statusEl) statusEl.textContent = 'Disconnected \u2014 reconnecting...';
    });

    Object.keys(panels).forEach(function(id) {
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
