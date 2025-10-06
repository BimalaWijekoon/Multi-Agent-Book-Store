// History Page JavaScript

// Load history on page load
document.addEventListener('DOMContentLoaded', function() {
    loadHistory();
});

// Load simulation history from API
function loadHistory() {
    fetch('/api/get_simulation_history')
        .then(response => response.json())
        .then(data => {
            if (data.simulations && data.simulations.length > 0) {
                displayHistory(data.simulations);
            } else {
                displayEmptyState();
            }
        })
        .catch(error => {
            console.error('Error loading history:', error);
            displayErrorState();
        });
}

// Display simulation history
function displayHistory(simulations) {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = '';
    
    // Sort by timestamp (newest first)
    simulations.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    simulations.forEach((sim, index) => {
        const card = createHistoryCard(sim, index);
        historyList.appendChild(card);
    });
}

// Create a history card for a simulation
function createHistoryCard(sim, index) {
    const card = document.createElement('div');
    card.className = 'history-card';
    
    // Format timestamp
    const date = new Date(sim.timestamp);
    const formattedDate = date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    card.innerHTML = `
        <div class="history-header">
            <div class="history-timestamp">
                📅 ${formattedDate}
            </div>
            <div class="history-status status-completed">
                ✓ Completed
            </div>
        </div>
        
        <div class="history-stats">
            <div class="history-stat">
                <div class="history-stat-value">${sim.num_customers || 0}</div>
                <div class="history-stat-label">👥 Customers</div>
            </div>
            <div class="history-stat">
                <div class="history-stat-value">${sim.num_employees || 0}</div>
                <div class="history-stat-label">👨‍💼 Employees</div>
            </div>
            <div class="history-stat">
                <div class="history-stat-value">${sim.num_books || 0}</div>
                <div class="history-stat-label">📚 Books</div>
            </div>
            <div class="history-stat">
                <div class="history-stat-value">${sim.steps || 0}</div>
                <div class="history-stat-label">⏱️ Steps</div>
            </div>
            <div class="history-stat">
                <div class="history-stat-value">$${(sim.revenue || 0).toFixed(0)}</div>
                <div class="history-stat-label">💰 Revenue</div>
            </div>
            <div class="history-stat">
                <div class="history-stat-value">${(sim.satisfaction || 0).toFixed(1)}%</div>
                <div class="history-stat-label">😊 Satisfaction</div>
            </div>
        </div>
        
        <button class="btn btn-primary load-button" onclick="loadSimulation('${sim.directory}')">
            📂 Load Simulation
        </button>
    `;
    
    return card;
}

// Load a specific simulation
function loadSimulation(directory) {
    // Show loading state
    const button = event.target;
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '⏳ Loading...';
    
    fetch(`/api/load_simulation/${directory}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success message
                button.innerHTML = '✓ Loaded!';
                button.style.background = 'var(--success)';
                
                // Redirect to dashboard after short delay
                setTimeout(() => {
                    window.location.href = '/';
                }, 1000);
            } else {
                throw new Error(data.error || 'Failed to load simulation');
            }
        })
        .catch(error => {
            console.error('Error loading simulation:', error);
            button.disabled = false;
            button.innerHTML = '❌ Failed - Try Again';
            button.style.background = 'var(--danger)';
            
            // Reset button after delay
            setTimeout(() => {
                button.innerHTML = originalText;
                button.style.background = '';
            }, 2000);
        });
}

// Refresh history
function refreshHistory() {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">🔄</div>
            <p>Refreshing history...</p>
        </div>
    `;
    loadHistory();
}

// Display empty state
function displayEmptyState() {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">📦</div>
            <h3>No Simulations Found</h3>
            <p>Run a simulation to see it here!</p>
            <button class="btn btn-primary" onclick="window.location.href='/'">
                ▶️ Start New Simulation
            </button>
        </div>
    `;
}

// Display error state
function displayErrorState() {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">⚠️</div>
            <h3>Error Loading History</h3>
            <p>Could not load simulation history. Please try again.</p>
            <button class="btn btn-primary" onclick="refreshHistory()">
                🔄 Retry
            </button>
        </div>
    `;
}

// Theme toggle function
function toggleTheme() {
    document.body.classList.toggle('light-theme');
    localStorage.setItem('theme', document.body.classList.contains('light-theme') ? 'light' : 'dark');
}

// Apply saved theme
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'light') {
    document.body.classList.add('light-theme');
}
