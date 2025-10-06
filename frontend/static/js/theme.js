// ============================================
// THEME TOGGLE FUNCTIONALITY
// Shared across all pages
// ============================================

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    const themeButton = document.querySelector('.theme-toggle');
    if (themeButton) {
        themeButton.textContent = newTheme === 'dark' ? '☀️' : '🌙';
    }
}

// Load saved theme on page load
function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    const themeButton = document.querySelector('.theme-toggle');
    if (themeButton) {
        themeButton.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
    }
}

// Initialize theme when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadTheme);
} else {
    loadTheme();
}
