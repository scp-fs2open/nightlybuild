(function() {
    var socket = io({transports: ['websocket']});
    var logEl = document.getElementById('update-log');
    var statusEl = document.getElementById('build-status');
    var buttons = ['btn-rebuild', 'btn-restart', 'btn-stop'].map(function(id) {
        return document.getElementById(id);
    });

    var STATUS_LABELS = {
        idle: 'Idle',
        rebuilding: 'Rebuilding...',
        restarting: 'Restarting...',
        stopping: 'Stopping...'
    };

    socket.on('update_log_lines', function(msg) {
        if (!logEl) {
            // Log area may not exist yet (was empty or error) — create it
            var h2 = document.querySelectorAll('h2');
            var target = h2.length ? h2[h2.length - 1] : null;
            // Remove any "empty" paragraph
            if (target && target.nextElementSibling && target.nextElementSibling.tagName === 'P') {
                target.nextElementSibling.remove();
            }
            logEl = document.createElement('pre');
            logEl.className = 'log-output';
            logEl.id = 'update-log';
            if (target) {
                target.parentNode.insertBefore(logEl, target.nextSibling);
            }
        }
        logEl.textContent += msg.data;
        logEl.scrollTop = logEl.scrollHeight;
    });

    socket.on('update_log_truncated', function() {
        if (logEl) {
            logEl.textContent = '';
        }
    });

    socket.on('build_status', function(msg) {
        if (statusEl) {
            statusEl.className = 'status-indicator ' + msg.status;
            var label = STATUS_LABELS[msg.status] || msg.status;
            statusEl.innerHTML = '<span class="status-dot"></span>' + label;
        }
        buttons.forEach(function(btn) {
            if (btn) btn.disabled = msg.is_running;
        });
    });
})();
