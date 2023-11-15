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

    // Select all Attributes
    const selectAllAttributesCheckbox = document.getElementById('select-all-attributes');
    const checkboxesattributes = document.querySelectorAll('input[name="attributes[]"]');
    selectAllAttributesCheckbox.addEventListener('change', function(e) {
        checkboxesattributes.forEach(checkboxesattributes => {
            checkboxesattributes.checked = selectAllAttributesCheckbox.checked;
        });
    });

    // Submit form with selected Generations and Attributes
    const form = document.getElementById('gameForm');
    form.addEventListener('submit', function(e) {
        const gensChecked = document.querySelectorAll('input[name="gen[]"]:checked').length;
        const attributesChecked = document.querySelectorAll('input[name="attributes[]"]:checked').length;

        // Check if at least one value in both Generations and Attributes is selected
        if (gensChecked === 0 || attributesChecked === 0) {
            e.preventDefault(); 
            alert('Please select at least one value in Generations and Attributes!!!');
        }
    });
});