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
