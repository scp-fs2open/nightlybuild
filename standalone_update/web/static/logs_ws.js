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
        if (statusEl) statusEl.textContent = 'Connected';
    });

    socket.on('disconnect', function() {
        if (statusEl) statusEl.textContent = 'Disconnected \u2014 reconnecting...';
    });

    // Engine process status — combine ongoing engine_status with one-time
    // lsof check (log_file_active) to determine per-panel badge state.
    var engineRunning = null;    // updated by engine_status events
    var logFileActive = {};      // panel_id -> bool, set once by log_file_active

    function updateEngineBadges() {
        var badges = document.querySelectorAll('[id^="engine-status-"]');
        badges.forEach(function(el) {
            var panelId = el.id.replace(/^engine-status-/, '');
            var cls, label;
            if (engineRunning === null) {
                cls = 'unknown'; label = 'Engine status unknown';
            } else if (!engineRunning) {
                cls = 'stopped'; label = 'Engine not running';
            } else if (logFileActive[panelId] === true) {
                cls = 'running'; label = 'Log active';
            } else if (logFileActive[panelId] === false) {
                cls = 'stale'; label = 'Engine running \u2014 log stale';
            } else {
                cls = 'running'; label = 'Engine running';
            }
            el.className = 'engine-status ' + cls;
            var labelEl = el.querySelector('.engine-label');
            if (labelEl) labelEl.textContent = label;
        });
    }

    socket.on('engine_status', function(msg) {
        engineRunning = msg.running;
        updateEngineBadges();
    });

    socket.on('log_file_active', function(msg) {
        logFileActive = msg.panels || {};
        updateEngineBadges();
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
