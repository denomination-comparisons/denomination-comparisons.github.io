// ARTI-koppling: JavaScript för vokabulärhjälp och interaktivitet

document.addEventListener('DOMContentLoaded', function() {
    // Exempel på vokabulärdata (kan hämtas från databas)
    const vocabulary = {
        'familj': 'En grupp människor som bor tillsammans',
        'skola': 'Plats där barn lär sig',
        'miljö': 'Naturen och världen runt oss'
    };

    // Lägg till hover-effekter för ord
    const textContent = document.querySelector('.text-content');
    if (textContent) {
        const words = textContent.innerHTML.split(' ');
        textContent.innerHTML = words.map(word => {
            const cleanWord = word.replace(/[^\w]/g, '').toLowerCase();
            if (vocabulary[cleanWord]) {
                return `<span class="word-hint" data-definition="${vocabulary[cleanWord]}">${word}</span>`;
            }
            return word;
        }).join(' ');
    }
});