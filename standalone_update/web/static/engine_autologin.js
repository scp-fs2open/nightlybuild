// Auto-authenticate to the legacy engine webui.
// The Flask proxy injects real Basic Auth credentials on every request,
// so the actual values passed here don't matter — we just need to trigger
// the login event so jQuery UI enables all tabs.
//
// This script loads after main.js, so our login handler fires after
// main.js's handler (which enables all tabs), letting us safely switch
// to the Server tab as the default landing page.
$(document).ready(function () {
    webui.events.subscribe('login', function () {
        $('#tabContainer').tabs('option', 'active', 1);
    });
    webui.auth.do('proxy', 'proxy');
});
