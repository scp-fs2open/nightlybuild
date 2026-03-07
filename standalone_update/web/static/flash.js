document.addEventListener('DOMContentLoaded', function () {
    document.addEventListener('click', function (e) {
        if (e.target.classList.contains('flash-close')) {
            e.target.parentNode.remove();
        }
    });
});
