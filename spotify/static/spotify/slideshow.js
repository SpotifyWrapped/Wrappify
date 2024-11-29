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
    const genreIconsContainer = document.querySelector('.floating-icons-container');

    // Map genres to emojis
    const genres = {
        rock: '🎸',
        pop: '🎤',
        jazz: '🎷',
        'hip-hop': '🤘',
        classical: '🎻',
        reggae: '🥁',
        edm: '💽',
        disco: '🪩'
    };

    const totalIcons = 30; // Number of icons to display

    // Generate floating icons
    for (let i = 0; i < totalIcons; i++) {
        const icon = document.createElement('div');
        icon.className = 'floating-icon';

        // Randomly pick a genre
        const genre = Object.keys(genres)[Math.floor(Math.random() * Object.keys(genres).length)];

        // Set the emoji as the content
        icon.textContent = genres[genre];

        // Random positioning
        icon.style.top = `${Math.random() * 90}%`; // Ensure no icons go too close to the edges
        icon.style.left = `${Math.random() * 90}%`;

        // Random animation delay
        icon.style.animationDelay = `${Math.random() * 5}s`;

        // Append to the container
        genreIconsContainer.appendChild(icon);
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const emojisContainer = document.getElementById('falling-emojis-container');
    const emojis = ['🔥', '💎', '❤️', '🌈', '👑', '☕',]; // Array of emojis
    const totalEmojis = 30; // Maximum number of emojis visible at once

    function createFallingEmoji() {
        const emoji = document.createElement('div');
        emoji.className = 'falling-emoji';
        emoji.textContent = emojis[Math.floor(Math.random() * emojis.length)]; // Randomly pick an emoji

        // Random horizontal position
        emoji.style.left = `${Math.random() * 100}%`;

        // Random size for variation
        const size = 20 + Math.random() * 20; // Size between 20px and 40px
        emoji.style.fontSize = `${size}px`;

        // Random animation duration (falling speed)
        const duration = 3 + Math.random() * 5; // Between 3s and 8s
        emoji.style.animationDuration = `${duration}s`;

        // Append the emoji to the container
        emojisContainer.appendChild(emoji);

        // Remove the emoji after the animation completes
        setTimeout(() => {
            emoji.remove();
        }, duration * 1000); // Match removal time to animation duration
    }

    // Generate emojis at intervals
    setInterval(() => {
        if (document.querySelectorAll('.falling-emoji').length < totalEmojis) {
            createFallingEmoji();
        }
    }, 200); // Adjust interval for emoji frequency
});


document.addEventListener('DOMContentLoaded', () => {
    const heartsContainer = document.getElementById('floating-hearts-container');
    const hearts = ['❤️', '💖', '💜', '💕', '💛', '🩷','💙', '💓', '❤️‍🔥', '🤎', '🩵', '🤍']; // Array of heart emojis
    const maxHearts = 20; // Maximum number of hearts visible at once

    function createRandomHeart() {
        const heart = document.createElement('div');
        heart.className = 'floating-heart';
        heart.textContent = hearts[Math.floor(Math.random() * hearts.length)]; // Random heart emoji

        // Random position on the screen
        heart.style.top = `${Math.random() * 100}%`; // Random vertical position
        heart.style.left = `${Math.random() * 100}%`; // Random horizontal position

        // Random size for the heart
        const size = 20 + Math.random() * 40; // Size between 20px and 60px
        heart.style.fontSize = `${size}px`;

        // Random animation duration
        const duration = 4 + Math.random() * 3; // Duration between 4-7 seconds
        heart.style.animationDuration = `${duration}s`;

        // Append the heart to the container
        heartsContainer.appendChild(heart);

        // Remove the heart after the animation ends
        setTimeout(() => {
            heart.remove();
        }, duration * 1000);
    }

    // Generate hearts at intervals
    setInterval(() => {
        if (document.querySelectorAll('.floating-heart').length < maxHearts) {
            createRandomHeart();
        }
    }, 300); // Creates a new heart every 300ms
});

document.addEventListener('DOMContentLoaded', () => {
    const starsContainer = document.getElementById('falling-stars-container');
    const emojis = ['✨', '⭐', '🌟', '💫']; // Array of star-related emojis
    const totalStars = 20; // Maximum number of stars visible at once

    function createFallingStar() {
        const star = document.createElement('div');
        star.className = 'falling-star';
        star.textContent = emojis[Math.floor(Math.random() * emojis.length)]; // Randomly pick a star emoji

        // Random horizontal position
        star.style.left = `${Math.random() * 100}%`;

        // Random size for variation
        const size = 20 + Math.random() * 10; // Between 20px and 50px
        star.style.fontSize = `${size}px`;

        // Random animation duration (falling speed)
        const duration = 3 + Math.random() * 4; // Between 3s and 7s
        star.style.animationDuration = `${duration}s`;

        // Append the star to the container
        starsContainer.appendChild(star);

        // Remove the star after the animation completes
        setTimeout(() => {
            star.remove();
        }, duration * 1000);
    }

    // Create stars at intervals
    setInterval(() => {
        if (document.querySelectorAll('.falling-star').length < totalStars) {
            createFallingStar();
        }
    }, 200); // Adjust interval for star frequency
});



