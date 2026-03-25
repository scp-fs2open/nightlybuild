function toggleOverride(checkbox, varName) {
    var input = document.getElementById('value_' + varName);
    var row = checkbox.closest('.form-row');
    input.disabled = !checkbox.checked;
    if (checkbox.checked) {
        row.classList.add('overridden');
        if (!input.value) input.focus();
    } else {
        row.classList.remove('overridden');
    }
}

document.querySelectorAll('input[name^="override_"]').forEach(function(checkbox) {
    var varName = checkbox.name.slice('override_'.length);
    checkbox.addEventListener('change', function() {
        toggleOverride(checkbox, varName);
    });
});
