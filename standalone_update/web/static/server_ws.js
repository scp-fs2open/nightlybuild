(function() {
    var socket = io({transports: ['websocket']});
    socket.on('connect', function() {
        socket.emit('join_page', 'server');
    });
    var logEl = document.getElementById('update-log');
    var statusEl = document.getElementById('build-status');
    var msgEl = document.getElementById('action-message');
    var buttons = ['btn-rebuild', 'btn-update', 'btn-restart', 'btn-stop'].map(function(id) {
        return document.getElementById(id);
    });

    var STATUS_LABELS = {
        idle: 'Idle',
        rebuilding: 'Rebuilding...',
        updating: 'Updating & Restarting...',
        restarting: 'Restarting...',
        stopping: 'Stopping...'
    };

    function doAction(action) {
        if (msgEl) msgEl.textContent = '';
        socket.emit('server_action', {action: action}, function(resp) {
            if (!resp.ok && msgEl) {
                msgEl.textContent = resp.error;
                msgEl.className = 'flash error';
            }
        });
    }

    buttons[0].addEventListener('click', function() { doAction('rebuild'); });
    buttons[1].addEventListener('click', function() { doAction('update'); });
    buttons[2].addEventListener('click', function() { doAction('restart'); });
    buttons[3].addEventListener('click', function() { doAction('stop'); });

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

    var BUILD_INFO_FIELDS = [
        {key: 'binary', label: 'Binary'},
        {key: 'build_type', label: 'Build Type'},
        {key: 'compiler', label: 'Compiler'},
        {key: 'reference', label: 'Reference'},
        {key: 'commit', label: 'Commit', code: true},
        {key: 'mod_dirname', label: 'Mod', suffix_key: 'mod_vcs'},
        {key: 'extra_flags', label: 'Extra Flags', code: true},
        {key: 'built_at', label: 'Built'},
        {key: 'mods_updated_at', label: 'Mods Updated'}
    ];

    socket.on('build_info', function(msg) {
        var container = document.querySelector('.build-info');
        var info = msg.info;
        if (!info) {
            if (container) container.remove();
            return;
        }
        if (!container) {
            container = document.createElement('div');
            container.className = 'build-info';
            var controls = document.querySelector('.server-controls');
            if (controls) controls.parentNode.insertBefore(container, controls.nextSibling);
        }
        var html = '<h3>Current Deployment</h3><table class="info-table">';
        BUILD_INFO_FIELDS.forEach(function(f) {
            var val = info[f.key];
            if (!val) return;
            var display = f.code ? '<code>' + val + '</code>' : val;
            if (f.suffix_key && info[f.suffix_key]) {
                display += ' <span class="info-secondary">(' + info[f.suffix_key] + ')</span>';
            }
            html += '<tr><td class="info-label">' + f.label + '</td><td>' + display + '</td></tr>';
        });
        html += '</table>';
        container.innerHTML = html;
    });

    // Engine process status
    var ENGINE_STATES = {
        true:  {cls: 'running',  label: 'Engine running'},
        false: {cls: 'stopped',  label: 'Engine not running'},
        null:  {cls: 'unknown',  label: 'Engine status unknown'}
    };

    socket.on('engine_status', function(msg) {
        var el = document.getElementById('engine-status');
        if (!el) return;
        var state = ENGINE_STATES[msg.running] || ENGINE_STATES[null];
        el.className = 'engine-status ' + state.cls;
        var label = el.querySelector('.engine-label');
        if (label) label.textContent = state.label;
    });

    socket.on('build_status', function(msg) {
        if (statusEl) {
            statusEl.className = 'status-indicator ' + msg.status;
            var label = STATUS_LABELS[msg.status] || msg.status;
            statusEl.textContent = '';
            var dot = document.createElement('span');
            dot.className = 'status-dot';
            statusEl.appendChild(dot);
            statusEl.appendChild(document.createTextNode(label));
        }
        buttons.forEach(function(btn) {
            if (btn) btn.disabled = msg.is_running;
        });
        // Clear action message when status changes
        if (msgEl) msgEl.textContent = '';
    });
})();
