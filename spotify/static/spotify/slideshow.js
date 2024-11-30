document.addEventListener("DOMContentLoaded", function () {
    let currentSlide = 0;
    const slides = document.querySelectorAll('.slides');
    const progressBars = document.querySelectorAll('.progress-bar');

    function showSlide(index) {
        slides.forEach((slide, i) => {
            slide.style.display = (i === index) ? 'block' : 'none';
        });
        
        // Update progress bars
        progressBars.forEach((bar, i) => {
            bar.classList.toggle('active', i === index);
        });
    }

    function nextSlide() {
        currentSlide = (currentSlide + 1) % slides.length; // Cycle through slides
        showSlide(currentSlide);
    }

    function previousSlide() {
        currentSlide = (currentSlide - 1 + slides.length) % slides.length; // Cycle backward
        showSlide(currentSlide);
    }

    function goToSlide(index) {
        currentSlide = index; // Set currentSlide to the clicked index
        showSlide(currentSlide);
    }

    // Show the first slide initially
    showSlide(currentSlide);

    // Change slide every 20 seconds
    setInterval(nextSlide, 200000);

    // Attach click events to progress bars
    progressBars.forEach((bar, index) => {
        bar.addEventListener('click', () => goToSlide(index));
    });

    // Add keydown event listener for the right and left arrow keys
    document.addEventListener('keydown', function (event) {
        if (event.key === 'ArrowRight') {
            nextSlide();
        } else if (event.key === 'ArrowLeft') {
            previousSlide();
        }
    });

});

document.addEventListener('DOMContentLoaded', () => {
    const topArtistsContainer = document.querySelector('.top-artists-container');

    // Allow the container to expand if needed for wider designs
    if (topArtistsContainer) {
        topArtistsContainer.classList.add('wide'); // Apply "wide" layout
    }
    
    // Utility: Calculate dynamic element count based on screen size
    function getDynamicCount(baseCount) {
        const screenWidth = window.innerWidth;
        if (screenWidth <= 480) return Math.ceil(baseCount * 0.5); // 30% for small screens
        if (screenWidth <= 768) return Math.ceil(baseCount * 0.8); // 60% for medium screens
        return baseCount; // Default for larger screens
    }

    // Floating Icons
    const genreIconsContainer = document.querySelector('.floating-icons-container');
    const genres = {
        rock: '🎸', pop: '🎤', jazz: '🎷', 'hip-hop': '🤘', classical: '🎻', reggae: '🥁', edm: '💽', disco: '🪩'
    };
    let totalIcons = getDynamicCount(20);

    function generateIcons() {
        genreIconsContainer.innerHTML = ''; // Clear previous icons
        for (let i = 0; i < totalIcons; i++) {
            const icon = document.createElement('div');
            icon.className = 'floating-icon';
            const genre = Object.keys(genres)[Math.floor(Math.random() * Object.keys(genres).length)];
            icon.textContent = genres[genre];
            icon.style.top = `${Math.random() * 90}%`;
            icon.style.left = `${Math.random() * 90}%`;
            icon.style.animationDelay = `${Math.random() * 5}s`;
            genreIconsContainer.appendChild(icon);
        }
    }
    generateIcons();

    // Falling Emojis
    const emojisContainer = document.getElementById('falling-emojis-container');
    const emojis = ['🔥', '💎', '❤️', '🌈', '👑'];
    let totalEmojis = getDynamicCount(30);

    function createFallingEmoji() {
        const emoji = document.createElement('div');
        emoji.className = 'falling-emoji';
        emoji.textContent = emojis[Math.floor(Math.random() * emojis.length)];
        emoji.style.left = `${Math.random() * 100}%`;
        emoji.style.fontSize = `${20 + Math.random() * 20}px`;
        const duration = 3 + Math.random() * 5;
        emoji.style.animationDuration = `${duration}s`;
        emojisContainer.appendChild(emoji);
        setTimeout(() => emoji.remove(), duration * 1000);
    }

    setInterval(() => {
        if (document.querySelectorAll('.falling-emoji').length < totalEmojis) {
            createFallingEmoji();
        }
    }, 200);

    // Floating Hearts
    const heartsContainer = document.getElementById('floating-hearts-container');
    const hearts = ['❤️', '💖', '💜', '💕', '💛', '🩷', '💙', '💓', '❤️‍🔥', '🤎', '🩵', '🤍'];
    let maxHearts = getDynamicCount(20);

    function createRandomHeart() {
        const heart = document.createElement('div');
        heart.className = 'floating-heart';
        heart.textContent = hearts[Math.floor(Math.random() * hearts.length)];
        heart.style.top = `${Math.random() * 100}%`;
        heart.style.left = `${Math.random() * 100}%`;
        heart.style.fontSize = `${20 + Math.random() * 40}px`;
        const duration = 4 + Math.random() * 3;
        heart.style.animationDuration = `${duration}s`;
        heartsContainer.appendChild(heart);
        setTimeout(() => heart.remove(), duration * 1000);
    }

    setInterval(() => {
        if (document.querySelectorAll('.floating-heart').length < maxHearts) {
            createRandomHeart();
        }
    }, 300);

    // Falling Stars
    const starsContainer = document.getElementById('falling-stars-container');
    const stars = ['✨', '⭐', '🌟', '💫'];
    let totalStars = getDynamicCount(20);

    function createFallingStar() {
        const star = document.createElement('div');
        star.className = 'falling-star';
        star.textContent = stars[Math.floor(Math.random() * stars.length)];
        star.style.left = `${Math.random() * 100}%`;
        star.style.fontSize = `${20 + Math.random() * 10}px`;
        const duration = 3 + Math.random() * 4;
        star.style.animationDuration = `${duration}s`;
        starsContainer.appendChild(star);
        setTimeout(() => star.remove(), duration * 1000);
    }

    setInterval(() => {
        if (document.querySelectorAll('.falling-star').length < totalStars) {
            createFallingStar();
        }
    }, 200);

    // Recalculate counts on resize
    window.addEventListener('resize', () => {
        totalIcons = getDynamicCount(20);
        totalEmojis = getDynamicCount(30);
        maxHearts = getDynamicCount(20);
        totalStars = getDynamicCount(20);
        generateIcons();
    });
});
