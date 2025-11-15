// This script runs on both index.html and dashboard.html
// It checks the current page and applies the correct logic.

document.addEventListener('DOMContentLoaded', () => {
    
    // Logic for index.html (Registration Page)
    if (document.getElementById('age-gate')) {
        const checkAgeBtn = document.getElementById('check-age-btn');
        const dobInput = document.getElementById('dob');
        const ageMessage = document.getElementById('age-message');
        const consentModal = document.getElementById('consent-modal');
        const consentText = document.getElementById('consent-text');
        const closeModalBtn = document.getElementById('close-modal');
        const consentForm = document.getElementById('consent-form');
        const adultRegistration = document.getElementById('adult-registration');
        const adultForm = document.getElementById('adult-form');
        
        checkAgeBtn.addEventListener('click', () => {
            const dob = new Date(dobInput.value);
            if (isNaN(dob.getTime())) {
                ageMessage.textContent = 'Please enter a valid date of birth.';
                return;
            }

            const age = calculateAge(dob);
            const userTier = getTier(age);
            
            // Store tier temporarily
            localStorage.setItem('tempTier', userTier.tier);
            
            ageMessage.textContent = `You are ${age} years old. Your access tier is: ${userTier.name}.`;
            ageMessage.className = 'message success';

            // Show correct follow-up
            if (userTier.tier === 'ineligible') {
                ageMessage.className = 'message error';
                ageMessage.textContent = 'We are sorry, but you must be at least 13 years old to join The Agora.';
            } else if (userTier.tier === 'disciple' || userTier.tier === 'scribe') {
                // Show consent modal
                consentText.textContent = userTier.consentMessage;
                consentModal.style.display = 'block';
            } else if (userTier.tier === 'elder') {
                // Show adult registration form
                document.getElementById('age-gate').style.display = 'none';
                adultRegistration.style.display = 'block';
            }
        });

        // Close modal
        closeModalBtn.addEventListener('click', () => {
            consentModal.style.display = 'none';
        });

        // Handle consent form submission (mock)
        consentForm.addEventListener('submit', (e) => {
            e.preventDefault();
            // In a real app, this would trigger a backend process.
            // For this prototype, we'll simulate a "pending consent" state
            // and log the user in to show the dashboard.
            
            const tier = localStorage.getItem('tempTier');
            console.log(`Simulating consent request for a ${tier} user.`);
            
            // Log the user in for the demo
            logInUser(tier);
        });

        // Handle adult registration (mock)
        adultForm.addEventListener('submit', (e) => {
            e.preventDefault();
            // Log the user in for the demo
            logInUser('elder');
        });

    } // End of index.html logic

    // Logic for dashboard.html
    if (document.getElementById('dashboard-content')) {
        const userTier = localStorage.getItem('userTier');
        const tierName = document.getElementById('user-tier-name');
        const welcomeMessage = document.getElementById('welcome-message');
        const logoutBtn = document.getElementById('logout-btn');

        if (!userTier) {
            // If no user is logged in, redirect to index
            window.location.href = 'index.html';
            return;
        }
        
        const tierInfo = getTier(null, userTier); // Get info by tier name
        
        // Set welcome message
        tierName.textContent = tierInfo.name;
        welcomeMessage.textContent = `Welcome to your ${tierInfo.name} dashboard. ${tierInfo.welcome}`;

        // Show/Hide feature modules based on tier
        if (userTier === 'disciple') {
            document.querySelector('.tier-disciple').style.display = 'block';
        }
        
        if (userTier === 'scribe') {
            document.querySelector('.tier-disciple').style.display = 'block'; // Scribes get Disciple features
            document.querySelector('.tier-scribe').style.display = 'block';
        }

        if (userTier === 'elder') {
            document.querySelector('.tier-disciple').style.display = 'block'; // Elders get all features
            document.querySelector('.tier-scribe').style.display = 'block';
            document.querySelector('.tier-elder').style.display = 'block';
        }
        
        // Logout
        logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('userTier');
            window.location.href = 'index.html';
        });

    } // End of dashboard.html logic

});


// --- Helper Functions ---

function calculateAge(birthDate) {
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }
    return age;
}

function getTier(age, tierName = null) {
    if (tierName) {
        if (tierName === 'disciple') return { tier: 'disciple', name: 'Disciple', welcome: 'Here you can safely explore core topics.' };
        if (tierName === 'scribe') return { tier: 'scribe', name: 'Scribe', welcome: 'You have access to creative tools and more advanced forums.' };
        if (tierName === 'elder') return { tier: 'elder', name: 'Elder', welcome: 'You have full access to all platform features.' };
    }
    
    if (age < 13) {
        return { tier: 'ineligible' };
    } else if (age >= 13 && age <= 15) {
        return { 
            tier: 'disciple', 
            name: 'Disciple (13-15)', 
            consentMessage: 'As a Disciple, you will have access to all core lessons and pre-moderated forums. We require your guardian\'s consent to join.' 
        };
    } else if (age >= 16 && age <= 17) {
        return { 
            tier: 'scribe', 
            name: 'Scribe (16-17)', 
            consentMessage: 'As a Scribe, you have expanded access, including post-moderated forums and community content tools. We still require guardian consent until you are 18.' 
        };
    } else { // 18+
        return { 
            tier: 'elder', 
            name: 'Elder (18+)', 
            consentMessage: '' 
        };
    }
}

function logInUser(tier) {
    localStorage.setItem('userTier', tier);
    localStorage.removeItem('tempTier');
    // Redirect to dashboard
    window.location.href = 'dashboard.html';
}
