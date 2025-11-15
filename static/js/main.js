// Main JavaScript for The Cinematic

// Toggle mobile menu
function toggleMobileMenu() {
    const menu = document.getElementById('mobileMenu');
    if (menu) {
        menu.classList.toggle('active');
    }
}

// Toggle user menu
function toggleUserMenu() {
    const menu = document.getElementById('userMenu');
    if (menu) {
        menu.classList.toggle('hidden');
    }
}

// Close menus when clicking outside
document.addEventListener('click', function(event) {
    const userMenu = document.getElementById('userMenu');
    const mobileMenu = document.getElementById('mobileMenu');
    
    // Close user menu if clicking outside
    if (userMenu && !event.target.closest('[onclick="toggleUserMenu()"]')) {
        userMenu.classList.add('hidden');
    }
    
    // Close mobile menu if clicking outside
    if (mobileMenu && mobileMenu.classList.contains('active')) {
        if (!event.target.closest('.mobile-menu') && !event.target.closest('[onclick="toggleMobileMenu()"]')) {
            mobileMenu.classList.remove('active');
        }
    }
});

// Create star rating component for movie detail page
function createMovieRating(containerId, initialRating, csrfToken, movieId) {
    const container = document.getElementById(containerId);
    const ratingText = document.getElementById('ratingText');
    
    if (!container) return;
    
    let currentRating = initialRating;
    let hoverRating = 0;
    
    // Create 5 stars
    for (let i = 1; i <= 5; i++) {
        const star = document.createElement('svg');
        star.className = 'star w-8 h-8';
        star.setAttribute('viewBox', '0 0 24 24');
        star.innerHTML = '<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path>';
        
        // Add hover effect
        star.addEventListener('mouseenter', () => {
            hoverRating = i;
            updateStars();
        });
        
        star.addEventListener('mouseleave', () => {
            hoverRating = 0;
            updateStars();
        });
        
        // Add click to save rating
        star.addEventListener('click', () => {
            currentRating = i;
            updateStars();
            saveRating(i);
        });
        
        container.appendChild(star);
    }
    
    // Update star appearance
    function updateStars() {
        const stars = container.querySelectorAll('.star');
        const rating = hoverRating || currentRating;
        
        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('filled');
            } else {
                star.classList.remove('filled');
            }
        });
        
        // Update rating text
        if (ratingText) {
            if (currentRating > 0) {
                ratingText.textContent = `You rated: ${currentRating}/5`;
            } else {
                ratingText.textContent = '';
            }
        }
    }
    
    // Save rating to backend via AJAX
    function saveRating(rating) {
        fetch(`/movie/${movieId}/rate/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `rating=${rating}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Rating saved successfully');
                if (ratingText) {
                    ratingText.textContent = `You rated: ${rating}/5`;
                }
            } else {
                console.error('Failed to save rating');
                alert('Failed to save rating. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    }
    
    // Initialize stars
    updateStars();
}

// Auto-hide messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('[class*="bg-red-900"], [class*="bg-green-900"]');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.transition = 'opacity 0.5s';
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 500);
        }, 5000);
    });
});

// Smooth scroll to top button (optional enhancement)
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Show scroll-to-top button when scrolled down
window.addEventListener('scroll', function() {
    const scrollBtn = document.getElementById('scrollToTop');
    if (scrollBtn) {
        if (window.pageYOffset > 300) {
            scrollBtn.classList.remove('hidden');
        } else {
            scrollBtn.classList.add('hidden');
        }
    }
});