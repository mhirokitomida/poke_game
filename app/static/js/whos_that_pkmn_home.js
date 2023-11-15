// Submit forms with settings
document.addEventListener('DOMContentLoaded', function() {
    // Select all Generations
    const selectAllGenCheckbox = document.getElementById('select-all-gen');
    const checkboxesgen = document.querySelectorAll('input[name="gen[]"]');
    selectAllGenCheckbox.addEventListener('change', function(e) {
        checkboxesgen.forEach(checkboxesgen => {
            checkboxesgen.checked = selectAllGenCheckbox.checked;
        });
    });

    // Submit form with selected Generations
    const form = document.getElementById('gameForm');
    form.addEventListener('submit', function(e) {
        const gensChecked = document.querySelectorAll('input[name="gen[]"]:checked').length;

        // Check if at least one value in Generations is selected
        if (gensChecked === 0) {
            e.preventDefault(); 
            alert('Please select at least one value in Generations!!!');
        }
    });
});