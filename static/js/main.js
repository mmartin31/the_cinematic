// ============================================
// THE CINEMATIC - MAIN JAVASCRIPT
// static/js/main.js
// ============================================

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

// Toggle advanced search filters
function toggleAdvancedSearch() {
    const advancedSearch = document.getElementById('advancedSearch');
    if (advancedSearch) {
        advancedSearch.classList.toggle('hidden');
    }
}

// Close menus when clicking outside
document.addEventListener('click', function(event) {
    const userMenu = document.getElementById('userMenu');
    const mobileMenu = document.getElementById('mobileMenu');
    const advancedSearch = document.getElementById('advancedSearch');
    
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
    
    // Close advanced search if clicking outside
    if (advancedSearch && !advancedSearch.classList.contains('hidden')) {
        if (!event.target.closest('#advancedSearch') && !event.target.closest('[onclick="toggleAdvancedSearch()"]')) {
            advancedSearch.classList.add('hidden');
        }
    }
});

// Create star rating component for movie detail page
function createMovieRating(containerId, initialRating, csrfToken, movieId) {
    console.log('createMovieRating called with:', { containerId, initialRating, csrfToken, movieId });
    const container = document.getElementById(containerId);
    const ratingText = document.getElementById('ratingText');
    
    console.log('Container found:', !!container);
    console.log('RatingText found:', !!ratingText);
    
    if (!container) {
        console.error('Container element not found:', containerId);
        return;
    }
    
    let currentRating = parseInt(initialRating, 10) || 0;
    let hoverRating = 0;
    
    // Create 5 stars using Unicode characters
    for (let i = 1; i <= 5; i++) {
        const star = document.createElement('span');
        star.className = 'star';
        star.textContent = '☆'; // Empty star
        star.style.fontSize = '32px';
        star.style.cursor = 'pointer';
        star.style.marginRight = '8px';
        star.style.display = 'inline-block';
        star.style.userSelect = 'none';
        
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
                star.textContent = '★'; // Filled star
                star.style.color = '#fbbf24';
            } else {
                star.textContent = '☆'; // Empty star
                star.style.color = '#64748b';
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
                // Show success message
                showNotification('Rating saved!', 'success');
            } else {
                console.error('Failed to save rating');
                showNotification('Failed to save rating. Please try again.', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('An error occurred. Please try again.', 'error');
        });
    }
    
    // Initialize stars
    updateStars();
}

// Show notification toast
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 px-6 py-4 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full ${
        type === 'success' ? 'bg-green-600' : 
        type === 'error' ? 'bg-red-600' : 
        'bg-blue-600'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Slide in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Slide out and remove
    setTimeout(() => {
        notification.style.transform = 'translateX(full)';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Auto-hide Django messages after 5 seconds
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

// Smooth scroll to top
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

// Lazy load images
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img[loading="lazy"]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src || img.src;
                    img.classList.add('fade-in');
                    observer.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Press '/' to focus search
    if (event.key === '/' && document.activeElement.tagName !== 'INPUT') {
        event.preventDefault();
        const searchInput = document.querySelector('input[name="search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Press 'Escape' to close modals/menus
    if (event.key === 'Escape') {
        const userMenu = document.getElementById('userMenu');
        const mobileMenu = document.getElementById('mobileMenu');
        const advancedSearch = document.getElementById('advancedSearch');
        
        if (userMenu) userMenu.classList.add('hidden');
        if (mobileMenu) mobileMenu.classList.remove('active');
        if (advancedSearch && !advancedSearch.classList.contains('hidden')) {
            advancedSearch.classList.add('hidden');
        }
    }
});

// Form validation helper
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('border-red-500');
            isValid = false;
        } else {
            field.classList.remove('border-red-500');
        }
    });
    
    return isValid;
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Live search (optional enhancement)
function initLiveSearch() {
    const searchInput = document.querySelector('input[name="search"]');
    if (!searchInput) return;
    
    const debouncedSearch = debounce(() => {
        // Auto-submit form after typing stops for 500ms
        if (searchInput.value.length >= 3 || searchInput.value.length === 0) {
            searchInput.form.submit();
        }
    }, 500);
    
    searchInput.addEventListener('input', debouncedSearch);
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('The Cinematic - Ready');
    
    // Uncomment to enable live search
    // initLiveSearch();
});

// Performance monitoring (development only)
if (window.performance && console.log) {
    window.addEventListener('load', function() {
        const perfData = window.performance.timing;
        const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
        console.log(`Page loaded in ${pageLoadTime}ms`);
    });
}