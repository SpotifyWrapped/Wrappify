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
    setInterval(nextSlide, 20000);

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
