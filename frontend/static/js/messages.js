// ============================================
// MESSAGES PAGE - Message Log Display
// Complete Rebuild with Clean Data Persistence
// ============================================

// Initialize WebSocket
const socket = io();

// Global state - messages data
let messagesData = [];
let filteredMessages = [];

// Pagination state
let currentPage = 1;
const itemsPerPage = 20;

// ============================================
// WEBSOCKET EVENT HANDLERS
// ============================================

socket.on('connect', () => {
    console.log('✓ Messages page connected to WebSocket');
});

socket.on('simulation_started', () => {
    console.log('✓ New simulation started - clearing messages');
    
    // Clear all data
    messagesData = [];
    filteredMessages = [];
    currentPage = 1;
    
    // Clear display
    displayMessages();
    updateStats();
    populateTypeFilter();
});

socket.on('message_logged', (message) => {
    // Add new message
    messagesData.push(message);
    
    // Re-filter and display
    filterMessages();
    updateStats();
    populateTypeFilter();
});

socket.on('simulation_complete', () => {
    console.log('✓ Simulation complete - messages persisted');
    // Data stays in messagesData for navigation persistence
});

// ============================================
// MESSAGE DISPLAY FUNCTIONS
// ============================================

function displayMessages() {
    const container = document.getElementById('messagesContainer');
    
    if (!container) {
        console.error('Messages container not found!');
        return;
    }
    
    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageMessages = filteredMessages.slice(start, end);
    
    if (pageMessages.length === 0) {
        container.innerHTML = '<p class="text-center" style="padding: 2rem; color: var(--text-secondary);">No messages found</p>';
        updatePagination();
        return;
    }
    
    container.innerHTML = pageMessages.map(msg => {
        const timestamp = msg.timestamp ? new Date(msg.timestamp).toLocaleString() : 'N/A';
        
        // Better content handling - extract meaningful information
        let contentStr = 'No content';
        if (msg.content) {
            if (typeof msg.content === 'object') {
                // Pretty print the object
                contentStr = JSON.stringify(msg.content, null, 2);
            } else {
                contentStr = msg.content;
            }
        } else if (msg.performative) {
            // If no content but has performative, show that
            contentStr = `Performative: ${msg.performative}`;
        } else if (msg.conversation_id) {
            // Show conversation ID if available
            contentStr = `Conversation ID: ${msg.conversation_id}`;
        }
        
        return `
            <div class="card mb-2" style="padding: 1rem;">
                <div class="flex justify-between items-center mb-2">
                    <div>
                        <span class="badge badge-primary">${msg.sender || 'Unknown'}</span>
                        <span style="margin: 0 0.5rem;">→</span>
                        <span class="badge badge-success">${msg.receiver || 'Unknown'}</span>
                        <span class="badge badge-info">${msg.type || 'Unknown'}</span>
                        <span class="badge badge-secondary">Step ${msg.step || 0}</span>
                    </div>
                    <span class="text-secondary" style="font-size: 0.85rem;">${timestamp}</span>
                </div>
                <div style="background: var(--bg-tertiary); padding: 0.75rem; border-radius: var(--radius-md);">
                    <pre style="margin: 0; white-space: pre-wrap; font-family: 'Fira Code', monospace; font-size: 0.9rem; color: var(--text-primary);">${contentStr}</pre>
                </div>
            </div>
        `;
    }).join('');
    
    updatePagination();
}

function updatePagination() {
    const pagination = document.getElementById('pagination');
    
    if (!pagination) {
        return;
    }
    
    const totalPages = Math.ceil(filteredMessages.length / itemsPerPage);
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = `<button class="pagination-btn" onclick="changePage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>‹ Prev</button>`;
    
    for (let i = 1; i <= Math.min(totalPages, 10); i++) {
        html += `<button class="pagination-btn ${i === currentPage ? 'active' : ''}" onclick="changePage(${i})">${i}</button>`;
    }
    
    html += `<button class="pagination-btn" onclick="changePage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>Next ›</button>`;
    
    pagination.innerHTML = html;
}

function changePage(page) {
    const totalPages = Math.ceil(filteredMessages.length / itemsPerPage);
    if (page < 1 || page > totalPages) return;
    
    currentPage = page;
    displayMessages();
    
    // Scroll to top
    const container = document.getElementById('messagesContainer');
    if (container) {
        container.scrollTop = 0;
    }
}

// ============================================
// FILTERING FUNCTIONS
// ============================================

function filterMessages() {
    const searchInput = document.getElementById('searchInput');
    const typeFilter = document.getElementById('typeFilter');
    
    const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
    const selectedType = typeFilter ? typeFilter.value : '';
    
    filteredMessages = messagesData.filter(msg => {
        const matchesSearch = searchTerm === '' || JSON.stringify(msg).toLowerCase().includes(searchTerm);
        const matchesType = selectedType === '' || msg.type === selectedType;
        return matchesSearch && matchesType;
    });
    
    currentPage = 1;
    displayMessages();
}

function populateTypeFilter() {
    const select = document.getElementById('typeFilter');
    
    if (!select) {
        return;
    }
    
    const uniqueTypes = [...new Set(messagesData.map(m => m.type || 'Unknown'))].sort();
    
    select.innerHTML = '<option value="">All Types</option>';
    uniqueTypes.forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type;
        select.appendChild(option);
    });
}

// ============================================
// STATS UPDATE FUNCTIONS
// ============================================

function updateStats() {
    // Total messages
    updateStatElement('total-messages', messagesData.length);
    
    // Unique types
    const uniqueTypes = new Set(messagesData.map(m => m.type || 'Unknown'));
    updateStatElement('unique-types', uniqueTypes.size);
    
    // Average per step
    const steps = new Set(messagesData.map(m => m.step));
    const avgPerStep = steps.size > 0 ? (messagesData.length / steps.size).toFixed(1) : '0';
    updateStatElement('avg-per-step-msg', avgPerStep);
}

function updateStatElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

// ============================================
// EVENT LISTENERS
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('Messages page loaded - setting up event listeners...');
    
    // Setup filter listeners
    const typeFilter = document.getElementById('typeFilter');
    if (typeFilter) {
        typeFilter.addEventListener('change', () => filterMessages());
    }
    
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', () => filterMessages());
    }
    
    // Load existing data
    loadExistingData();
});

// ============================================
// DATA PERSISTENCE - LOAD FROM SERVER
// ============================================

async function loadExistingData() {
    try {
        console.log('Loading existing messages data from server...');
        const response = await fetch('/api/get_current_data');
        const data = await response.json();
        
        if (data.has_data && data.messages && data.messages.length > 0) {
            console.log('✓ Found existing messages data');
            
            // Restore messages data
            messagesData = data.messages || [];
            filteredMessages = [...messagesData];
            
            // Update display
            displayMessages();
            updateStats();
            populateTypeFilter();
            
            console.log('✓ Messages page fully restored from server');
        } else {
            console.log('No previous messages data found');
        }
    } catch (error) {
        console.error('Error loading existing data:', error);
    }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function refreshMessages() {
    console.log('Refreshing messages data...');
    loadExistingData();
}

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

// Load saved theme
const savedTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);
const themeButton = document.querySelector('.theme-toggle');
if (themeButton) {
    themeButton.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
}
