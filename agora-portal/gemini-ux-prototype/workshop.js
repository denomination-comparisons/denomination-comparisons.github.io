document.addEventListener('DOMContentLoaded', () => {
    // Mock data for fragments a user might have
    const userFragments = [
        { id: 'frag1', name: 'Grace', color: '#3498db' },
        { id: 'frag2', name: 'Covenant', color: '#e67e22' },
        { id: 'frag3', name: 'Exodus', color: '#9b59b6' },
        { id: 'frag4', name: 'Logos', color: '#2ecc71' },
        { id: 'frag5', name: 'Forgiveness', color: '#f1c40f' },
    ];

    const inventoryList = document.getElementById('inventory-list');
    const craftingSlots = document.getElementById('crafting-slots');
    const saveCredoBtn = document.getElementById('save-credo-btn');
    const craftMessage = document.getElementById('craft-message');
    const credoText = document.getElementById('credo-text');
    const placeholderText = document.querySelector('.placeholder-text');

    let draggedItem = null;

    // Populate inventory
    userFragments.forEach(fragment => {
        const fragEl = createFragmentElement(fragment);
        inventoryList.appendChild(fragEl);
    });

    function createFragmentElement(fragment) {
        const el = document.createElement('div');
        el.textContent = fragment.name;
        el.id = fragment.id;
        el.className = 'fragment-item';
        el.style.backgroundColor = fragment.color;
        el.draggable = true;
        
        // Drag events
        el.addEventListener('dragstart', (e) => {
            draggedItem = e.target;
            setTimeout(() => {
                e.target.style.display = 'none';
            }, 0);
        });

        el.addEventListener('dragend', () => {
            setTimeout(() => {
                if (draggedItem) {
                    draggedItem.style.display = 'block';
                    draggedItem = null;
                }
            }, 0);
        });
        return el;
    }

    // Crafting Slot Events
    craftingSlots.addEventListener('dragover', (e) => {
        e.preventDefault(); // Necessary to allow drop
    });

    craftingSlots.addEventListener('dragenter', (e) => {
        e.preventDefault();
        craftingSlots.classList.add('hovered');
        placeholderText.style.display = 'none';
    });

    craftingSlots.addEventListener('dragleave', ()_=> {
        craftingSlots.classList.remove('hovered');
    });

    craftingSlots.addEventListener('drop', (e) => {
        e.preventDefault();
        if (draggedItem) {
            // Check if it's from inventory (not already in the slot)
            if (draggedItem.parentElement.id === 'inventory-list') {
                const clone = draggedItem.cloneNode(true); // Clone it
                clone.draggable = false; // Make it non-draggable in the slot
                craftingSlots.appendChild(clone);
            }
            draggedItem.style.display = 'block'; // Make original visible again
            draggedItem = null;
            craftingSlots.classList.remove('hovered');
        }
    });

    // Save Credo
    saveCredoBtn.addEventListener('click', () => {
        const fragmentsInCredo = [...craftingSlots.children].filter(el => el.classList.contains('fragment-item'));
        const fragmentNames = fragmentsInCredo.map(f => f.textContent).join(', ');
        const reflection = credoText.value;

        if (fragmentsInCredo.length === 0 || reflection.trim() === '') {
            craftMessage.textContent = 'Please add fragments and write a reflection.';
            craftMessage.className = 'message error';
            return;
        }

        // In a real app, this sends to a backend.
        console.log('SAVING CREDO:');
        console.log('Fragments:', fragmentNames);
        console.log('Reflection:', reflection);

        craftMessage.textContent = 'Your Credo has been saved to your private journal!';
        craftMessage.className = 'message success';
        
        // Clear board
        craftingSlots.innerHTML = '<span class="placeholder-text">Drag fragments here</span>';
        credoText.value = '';
    });
});
