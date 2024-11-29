// Paths to your light and dark CSS files by page
const themePaths = {
    profile: {
        light: "{% static 'spotify/profile-light.css' %}",
        dark: "{% static 'spotify/profile-dark.css' %}",
    },
    wraps: {
        light: "{% static 'spotify/wraps-light.css' %}",
        dark: "{% static 'spotify/wraps-dark.css' %}",
    },
    wraps_library: {
        light: "{% static 'spotify/library-light.css' %}",
        dark: "{% static 'spotify/library-dark.css' %}",
    },
    game: {
        light: "{% static 'spotify/game-light.css' %}",
        dark: "{% static 'spotify/game-dark.css' %}",
    },
};

// Get references to elements
const themeStyle = document.getElementById('theme-style');
const darkModeToggle = document.getElementById('dark-mode-toggle');
const darkModeText = document.getElementById('dark-mode-text');
const darkModeIcon = document.getElementById('dark-mode-icon');
const currentPage = document.body.dataset.page;

// Function to apply the theme
function applyTheme(theme) {
    if (currentPage && themePaths[currentPage]) {
        themeStyle.setAttribute('href', theme === 'dark' ? themePaths[currentPage].dark : themePaths[currentPage].light);
    }
    if (darkModeText) {
        darkModeText.textContent = theme === 'dark' ? 'Dark Mode' : 'Light Mode'; // Update text dynamically
    }
    if (darkModeIcon) {
        darkModeIcon.src = theme === 'dark' ? "{% static 'images/darkmode.png' %}" : "{% static 'images/lightmode.png' %}";
    }
    if (darkModeToggle) {
        darkModeToggle.checked = theme === 'dark';
    }
}

// Initialize theme from localStorage
const savedTheme = localStorage.getItem('theme') || 'light';
applyTheme(savedTheme);

// Listen for toggle changes and update theme dynamically
if (darkModeToggle) {
    darkModeToggle.addEventListener('change', () => {
        const newTheme = darkModeToggle.checked ? 'dark' : 'light';
        localStorage.setItem('theme', newTheme); // Save theme to localStorage
        applyTheme(newTheme); // Apply theme to current page
    });
}

// Listen for theme changes across tabs
window.addEventListener('storage', (event) => {
    if (event.key === 'theme') {
        applyTheme(event.newValue); // Apply the new theme when detected
    }
});
