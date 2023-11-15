// Function to check user input in the toogle button (day/night switch)
document.addEventListener('DOMContentLoaded', function() {
    const toggleInput = document.getElementById('toggleBackground');

    // Check the stored state when loading the page
    const toggleState = localStorage.getItem('toggleState');
    if (toggleState === 'on') {
        toggleInput.checked = true;
        document.querySelector('.main_content').style.backgroundImage = 'url("/static/assets/night.jpg")';
    } else {
        toggleInput.checked = false;
        document.querySelector('.main_content').style.backgroundImage = 'url("/static/assets/day.jpg")';
    }

    // Update the localStorage when the toggle is changed
    toggleInput.addEventListener('change', function() {
        if (toggleInput.checked) {
            localStorage.setItem('toggleState', 'on');
            document.querySelector('.main_content').style.backgroundImage = 'url("/static/assets/night.jpg")';
        } else {
            localStorage.setItem('toggleState', 'off');
            document.querySelector('.main_content').style.backgroundImage = 'url("/static/assets/day.jpg")';
        }
    });
});