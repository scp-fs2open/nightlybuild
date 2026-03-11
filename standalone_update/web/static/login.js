document.addEventListener('DOMContentLoaded', function () {
    var btn = document.querySelector('.password-toggle');
    if (!btn) return;
    var input = document.getElementById('password');
    btn.addEventListener('click', function () {
        var show = input.type === 'password';
        input.type = show ? 'text' : 'password';
        btn.textContent = show ? 'Hide' : 'Show';
        btn.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
    });
});
