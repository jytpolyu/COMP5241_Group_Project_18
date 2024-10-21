document.addEventListener('DOMContentLoaded', function() {
    // Page loading animation
    const loader = document.createElement('div');
    loader.id = 'loader';
    loader.style.position = 'fixed';
    loader.style.top = '0';
    loader.style.left = '0';
    loader.style.width = '100%';
    loader.style.height = '100%';
    loader.style.backgroundColor = '#f8f9fa';
    loader.style.zIndex = '9999';
    loader.style.display = 'flex';
    loader.style.justifyContent = 'center';
    loader.style.alignItems = 'center';
    loader.innerHTML = '<div class="spinner-border text-dark" role="status"><span class="visually-hidden">Loading...</span></div>';
    document.body.appendChild(loader);

    window.addEventListener('load', function() {
        loader.style.display = 'none';
    });

    // Hover effect
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseover', function() {
            card.style.transform = 'scale(1.05)';
            card.style.transition = 'transform 0.3s';
        });
        card.addEventListener('mouseout', function() {
            card.style.transform = 'scale(1)';
        });
    });

    // Scroll to top button
    const scrollToTopBtn = document.createElement('button');
    scrollToTopBtn.id = 'scrollToTopBtn';
    scrollToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    scrollToTopBtn.style.position = 'fixed';
    scrollToTopBtn.style.bottom = '20px';
    scrollToTopBtn.style.right = '20px';
    scrollToTopBtn.style.backgroundColor = '#343a40';
    scrollToTopBtn.style.color = '#ffffff';
    scrollToTopBtn.style.border = 'none';
    scrollToTopBtn.style.borderRadius = '50%';
    scrollToTopBtn.style.padding = '10px';
    scrollToTopBtn.style.cursor = 'pointer';
    scrollToTopBtn.style.display = 'none';
    document.body.appendChild(scrollToTopBtn);

    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            scrollToTopBtn.style.display = 'block';
        } else {
            scrollToTopBtn.style.display = 'none';
        }
    });

    scrollToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Sidebar toggle
    const menuToggle = document.getElementById('menu-toggle');
    const wrapper = document.getElementById('wrapper');
    menuToggle.addEventListener('click', function() {
        wrapper.classList.toggle('toggled');
    });
});