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

function goToSlide(index) {
    currentSlide = index; // Set currentSlide to the clicked index
    showSlide(currentSlide);
}

// Show the first slide initially
showSlide(currentSlide);

// Change slide every 5 seconds
setInterval(nextSlide, 20000);
