let score = 0;
let lastChangedPkmnId = null;

// Alert the user when they attempt to navigate to another page
document.addEventListener('DOMContentLoaded', function() {
    let showUnloadAlert = true;

    const links = document.querySelectorAll('a');
    const confirmModal = document.getElementById('confirmModal');
    const confirmYes = document.getElementById('confirmYes');
    const confirmNo = document.getElementById('confirmNo');
    let currentLink = null;

    for(let link of links) {
        link.addEventListener('click', function(event) {
            if (showUnloadAlert) {
                event.preventDefault();
                currentLink = link.getAttribute('href');
                confirmModal.style.display = 'block';
            }
        });
    }

    confirmYes.addEventListener('click', function() {
        window.location.href = currentLink;
    });

    confirmNo.addEventListener('click', function() {
        confirmModal.style.display = 'none';
        currentLink = null;
    });
});

// Check selected Pokemon
document.querySelector('.pokemon_battle').addEventListener('click', function(event) {
    if (event.target.tagName === 'IMG') {
        checkWinner(event.target);
    }
});

// Function to animate attribute number
function animateStat(elementId, targetValue, stat_used) {
    let currentValue = 0;
    const value = (stat_used == 'Total') ? 10 : 
                (stat_used == 'Weight (Kg)') ? 3.1 : 
                (stat_used == 'Height (cm)') ? 0.1  : 5;
    let elementToShow = document.getElementById(elementId);

    if (elementToShow) {
        elementToShow.style.visibility = "visible";
    } else {
        console.error(`Element with ID ${elementId} not found.`);
    }

    return new Promise((resolve) => {
        function increaseStat() {
            if (currentValue < targetValue) {
                currentValue = parseFloat((currentValue + value).toFixed(1));
                if (currentValue > targetValue) {
                    currentValue = targetValue;
                }
                document.getElementById(elementId).textContent = currentValue;
                requestAnimationFrame(increaseStat);
            } else if (targetValue === 0) {
                document.getElementById(elementId).textContent = '?';
            } else {
                setTimeout(() => {
                    resolve(); 
                }, 500);
                
            }
        }
        increaseStat();
    });
}

// Function to check if user got the right answer
function checkWinner(selectedPkmn) {
    const statUsed = document.getElementById('stat').textContent;
    const pkmn1Elem = document.getElementById('pkmn-1').querySelector('img');
    const pkmn2Elem = document.getElementById('pkmn-2').querySelector('img');

    const selectedStat = parseFloat(selectedPkmn.getAttribute('data-stat'));
    const otherPkmn = selectedPkmn === pkmn1Elem ? pkmn2Elem : pkmn1Elem;
    const otherStat = parseFloat(otherPkmn.getAttribute('data-stat'));

    if (selectedStat >= otherStat) {
        userAction(true);
        score += 1;
        document.getElementById('score').textContent = "Score: " + score;

        let parentDivId;
        if (!lastChangedPkmnId) {
            parentDivId = selectedPkmn === pkmn1Elem ? "pkmn-1" : "pkmn-2";
        } else {
            parentDivId = lastChangedPkmnId === "pkmn-1" ? "pkmn-2" : "pkmn-1";
        }
        lastChangedPkmnId = parentDivId; 

        redrawPokemons(parentDivId);

    } else {
        userAction(false);
        score = 0; 
        document.getElementById('pkmn-1').classList.add('disabled');
        document.getElementById('pkmn-2').classList.add('disabled');
        Promise.all([
            animateStat("stat-pkmn-1", parseFloat(pkmn1Elem.getAttribute('data-stat')), statUsed),
            animateStat("stat-pkmn-2", parseFloat(pkmn2Elem.getAttribute('data-stat')), statUsed)
        ]).then(() => {
            postToURL("/higher_lower", { game_end_arg: "end" });
        });
    }
}

// Function to request new Pokemon to server
function redrawPokemons(lastChangedPkmnId) {
    // Temporarily disable click on Pokemon
    document.getElementById('pkmn-1').classList.add('disabled');
    document.getElementById('pkmn-2').classList.add('disabled');

    // Get current stat and Pokemons element
    const statUsed = document.getElementById('stat').textContent;
    const pkmn1Elem = document.getElementById('pkmn-1').querySelector('img');
    const pkmn2Elem = document.getElementById('pkmn-2').querySelector('img');

    // Request server to redraw Pokemon
    fetch(`/redraw_pokemons_hl?last_id=${lastChangedPkmnId}`)
    .then(response => response.json())
    .then(data => {
        // Check if Game ended
        if (data.game_end == 'True') {
            Promise.all([
                animateStat("stat-pkmn-1", parseFloat(pkmn1Elem.getAttribute('data-stat')), statUsed),
                animateStat("stat-pkmn-2", parseFloat(pkmn2Elem.getAttribute('data-stat')), statUsed)
            ]).then(() => {
                postToURL("/higher_lower", { game_end_arg: "end_full" });
            });
        }
        else{
            Promise.all([
                animateStat("stat-pkmn-1", parseFloat(pkmn1Elem.getAttribute('data-stat')), statUsed),
                animateStat("stat-pkmn-2", parseFloat(pkmn2Elem.getAttribute('data-stat')), statUsed)
            ]).then(() => {
                // Get new stat
                const statDiv = document.getElementById('stat');
                statDiv.textContent = data.random_stat;
                const statUsed = statDiv.textContent;
        
                // Change one Pokemon and maintain the other
                const [newPokemonDiv, oldPokemonDiv] = lastChangedPkmnId === 'pkmn-1' ? 
                [document.getElementById('pkmn-2'), document.getElementById('pkmn-1')] : 
                [document.getElementById('pkmn-1'), document.getElementById('pkmn-2')];

                // New Pokemon
                newPokemonDiv.querySelector('h2').textContent = data.new_pokemon.name;
                newPokemonDiv.querySelector('img').src = data.new_pokemon.sprite;
                newPokemonDiv.querySelector('img').setAttribute('data-stat', data.new_pokemon.stat);

                // Maintain Pokemon
                oldPokemonDiv.querySelector('h2').textContent = data.old_pokemon.name;
                oldPokemonDiv.querySelector('img').src = data.old_pokemon.sprite;
                oldPokemonDiv.querySelector('img').setAttribute('data-stat', data.old_pokemon.stat);

                // Enable click on Pokemon again
                setTimeout(() => {
                    document.getElementById('pkmn-1').classList.remove('disabled');
                    document.getElementById('pkmn-2').classList.remove('disabled');
                    document.getElementById("stat-pkmn-1").style.visibility = "hidden";
                    document.getElementById("stat-pkmn-2").style.visibility = "hidden";
                }, 800);
            });
        }
    });
}