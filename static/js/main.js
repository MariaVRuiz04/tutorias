// Wait for document to be ready
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // If flashed messages exist, auto-dismiss them after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add animation on scroll for elements with .animate-on-scroll class
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    if (animatedElements.length > 0) {
        // Create intersection observer to check when elements are in viewport
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animated');
                }
            });
        }, {
            threshold: 0.1
        });
        
        // Observe each animated element
        animatedElements.forEach(el => {
            observer.observe(el);
        });
    }
    
    // Make entire card clickable if it has a main link
    const cardLinks = document.querySelectorAll('.card-link-wrapper');
    cardLinks.forEach(card => {
        const link = card.querySelector('.card-main-link');
        if (link) {
            card.addEventListener('click', function(e) {
                // Don't trigger if clicked on another link or button inside the card
                if (!e.target.closest('a:not(.card-main-link)') && 
                    !e.target.closest('button')) {
                    link.click();
                }
            });
        }
    });
});

// Add API endpoint function for notification count - note this is just the frontend part,
// the actual endpoint would need to be implemented in the Flask app
function checkNotificationCount() {
    // This function would normally make an API request to the server
    // For demonstration purposes, we're returning a simulated response
    return {
        count: Math.floor(Math.random() * 3)  // Simulate 0-2 notifications
    };
}