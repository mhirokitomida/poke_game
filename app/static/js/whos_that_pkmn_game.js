let score = 0;

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

// When the generation filter changes, update the list with both filters
document.getElementById('generation-filter').addEventListener('change', function() {
    const genFilter = this.value;
    const textFilter = document.getElementById('global-filter').value;
    updateList(textFilter, genFilter);
});

// When the text filter changes, update the list with both filters
document.getElementById('global-filter').addEventListener('input', function() {
    const textFilter = this.value;
    const genFilter = document.getElementById('generation-filter').value;
    updateList(textFilter, genFilter);
});

// Initialize the list on page load
document.addEventListener('DOMContentLoaded', () => {
    const textFilter = document.getElementById('global-filter').value;
    const genFilter = document.getElementById('generation-filter').value;
    updateList(textFilter, genFilter);
});

// Initialize the list on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeLists(); 
});

// Logic for form submission
document.getElementById('gameForm').onsubmit = function(event) {
    event.preventDefault();

    var selectedPokemon = document.querySelector('input[name="selected_pokemon"]:checked');
    var filterInput = document.getElementById('global-filter');
    var genFilter = document.getElementById('generation-filter');
    if(selectedPokemon){
        filterInput.value = '';
        genFilter.value = 'All';
        updateList();
        checkWinner(selectedPokemon);
    } else {
        alert('No Pokémon selected');
        event.preventDefault(); // Prevents the form from being submitted if no Pokémon is selected
    }
};

// Function to filter all lists based on the value of the global filter
function filterAllLists() {
    var filterValue = document.getElementById('global-filter').value.toLowerCase();
    var listItems = document.querySelectorAll('.scrollable-list .pokemon-list');

    listItems.forEach(function(item) {
        var text = item.textContent.toLowerCase();
        if (text.includes(filterValue)) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

function updateList(textFilter = '', genFilter = 'All') {
    const listId = 'pokemon-list';
    const ul = document.getElementById(listId);
    if (!ul) return; // Exits the function if the list item is not found

    ul.innerHTML = ''; // Clears the current list

    // Filters by generation first, if necessary
    let filteredGenerations = genFilter === 'All' ? Object.values(generations_dict) : [generations_dict[genFilter]];

    // Combines all arrays of id_names into a single array and filters by text
    filteredGenerations.flat()
        .filter(name => name.toLowerCase().includes(textFilter.toLowerCase()))
        .forEach(name => {
            // Creation and addition of list elements as before
            const div = document.createElement('div');
            div.className = 'custom-radio';
            const input = document.createElement('input');
            input.type = 'radio';
            input.id = name;
            input.name = 'selected_pokemon';
            input.value = name;
            const label = document.createElement('label');
            label.htmlFor = name;
            label.textContent = name;

            div.appendChild(input);
            div.appendChild(label);
            ul.appendChild(div);
        });
}

// Function to initialize the lists the first time the page loads
function initializeLists() {
    updateList(); // Initializes with all items
    // Sets up the generation filter
    document.getElementById('generation-filter').addEventListener('change', function() {
        const gen = this.value;
        const globalFilter = document.getElementById('global-filter').value;
        updateList(globalFilter, gen); // Updates the list with the global and generation filters
    });
}

// Function to switch Pokemon Sprite 
function switchPokemonSprite(newSpriteSrc) {
    var pokemonSprite = document.getElementById('pokemonImage');
    pokemonSprite.src = newSpriteSrc;
    setTimeout(() => {
                    console.log('Switching sprite...'); 
                    }, 500);
}

// Function to check if user got the right answer
function checkWinner(pkmnElem) {
    
    var selectedPkmn = pkmnElem.value;
    var pokemonImage = document.getElementById('pokemonImage');
    var pokemonName = pokemonImage.getAttribute('id_name');
    var pokemonSprite = pokemonImage.getAttribute('sprite');

    if (selectedPkmn == pokemonName) {
        userAction(true);
        score += 1;
        document.getElementById('score').textContent = "Score: " + score;

        Promise.all([
            switchPokemonSprite(pokemonSprite)
        ]).then(() => {
            document.getElementById('name_pkmn').textContent = pokemonName;
            setTimeout(() => {
                redrawPokemons();
            }, 1500);
        });

    } else {
        userAction(false);
        score = 0; 
        Promise.all([
            switchPokemonSprite(pokemonSprite)
        ]).then(() => {
            document.getElementById('name_pkmn').textContent = pokemonName;
            setTimeout(() => {
                postToURL("/whos_that_pkmn", { game_end_arg: "end" });
            }, 1500);
        });
    }
}

// Function to request new Pokemon to server
function redrawPokemons() {
    var pokemonImage = document.getElementById('pokemonImage');
    var pokemonName = pokemonImage.getAttribute('id_name');
    var pokemonSprite = pokemonImage.getAttribute('sprite');

    // Request server to redraw Pokemon
    fetch(`/redraw_pokemons_wtp`)
    .then(response => response.json())
    .then(data => {
        // Check if Game ended
        if (data.game_end == 'True') {
            Promise.all([
                switchPokemonSprite(pokemonSprite)
            ]).then(() => {
                document.getElementById('name_pkmn').textContent = pokemonName;
                postToURL("/whos_that_pkmn", { game_end_arg: "end_full" });
            });
        }
        else{
            // Current Pokemon Element
            const newPokemonDiv = document.getElementById('pkmn');

            // Update the Pokémon based on the div ID
            document.getElementById('name_pkmn').textContent = '?';
            newPokemonDiv.querySelector('img').src = data.shadow_sprite;
            newPokemonDiv.querySelector('img').setAttribute('id_name', data.id_name);
            newPokemonDiv.querySelector('img').setAttribute('sprite', data.sprite);
        }
    });
}