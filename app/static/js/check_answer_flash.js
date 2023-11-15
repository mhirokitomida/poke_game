// Function to flash green/red for the user's correct/incorrect answer
function userAction(isCorrect) {
    const main_content = document.querySelector('.main_content');
    if (isCorrect) {
        main_content.classList.add('correct');
        setTimeout(() => {
            main_content.classList.remove('correct');
        }, 500);
    } else {
        main_content.classList.add('wrong');
        setTimeout(() => {
            main_content.classList.remove('wrong');
        }, 500);
    }
}