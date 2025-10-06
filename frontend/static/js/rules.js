// ============================================
// RULES PAGE - Detailed Execution Logs
// Complete Rebuild with Clean Data Persistence
// ============================================

// Initialize WebSocket
const socket = io();

// Global state - rules data
let rulesData = [];
let filteredRules = [];

// Pagination state
let currentPage = 1;
const itemsPerPage = 20;

// ============================================
// WEBSOCKET EVENT HANDLERS
// ============================================

socket.on('connect', () => {
    console.log('✓ Rules page connected to WebSocket');
});

socket.on('simulation_started', () => {
    console.log('✓ New simulation started - clearing rules');
    
    // Clear all data
    rulesData = [];
    filteredRules = [];
    currentPage = 1;
    
    // Clear display
    displayRules();
    updateStats();
    populateRuleFilter();
});

socket.on('rule_executed', (rule) => {
    // Add new rule
    rulesData.push(rule);
    
    // Re-filter and display
    filterRules();
    updateStats();
    populateRuleFilter();
});

socket.on('simulation_complete', () => {
    console.log('✓ Simulation complete - rules persisted');
    // Data stays in rulesData for navigation persistence
});

// ============================================
// RULES DISPLAY FUNCTIONS
// ============================================

function displayRules() {
    const container = document.getElementById('rulesContainer');
    
    if (!container) {
        console.error('Rules container not found!');
        return;
    }
    
    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageRules = filteredRules.slice(start, end);
    
    if (pageRules.length === 0) {
        container.innerHTML = '<p class="text-center" style="padding: 2rem; color: var(--text-secondary);">No rules found matching your criteria</p>';
        updatePagination();
        return;
    }
    
    container.innerHTML = pageRules.map(rule => createRuleCard(rule)).join('');
    updatePagination();
}

function createRuleCard(rule) {
    const timestamp = rule.timestamp ? new Date(rule.timestamp).toLocaleString() : 'N/A';
    const badgeClass = getBadgeClass(rule.rule_name || 'unknown');
    const ruleName = (rule.rule_name || 'Unknown').replace(/_/g, ' ');
    const ruleDescription = rule.rule_description || 'No description available';
    const conditionMet = rule.condition_met || 'N/A';
    const action = rule.action || 'N/A';
    
    return `
        <div class="card mb-2" style="padding: 1rem;">
            <div class="flex justify-between items-center mb-2">
                <div>
                    <span class="badge ${badgeClass}">${ruleName}</span>
                    <span class="badge badge-info">Step ${rule.step || 0}</span>
                </div>
                <span class="text-secondary" style="font-size: 0.85rem;">${timestamp}</span>
            </div>
            <p style="margin: 0.5rem 0; color: var(--text-secondary);">${ruleDescription}</p>
            <div style="background: var(--bg-tertiary); padding: 0.75rem; border-radius: var(--radius-md); margin: 0.5rem 0;">
                <strong style="color: var(--primary);">Condition:</strong> ${conditionMet}
            </div>
            <div style="background: var(--bg-tertiary); padding: 0.75rem; border-radius: var(--radius-md);">
                <strong style="color: var(--success);">Action:</strong> ${action}
            </div>
            ${createEntitiesDisplay(rule.entities)}
        </div>
    `;
}

function createEntitiesDisplay(entities) {
    if (!entities || Object.keys(entities).length === 0) return '';
    
    const entitiesHtml = Object.entries(entities).map(([key, value]) => {
        const valueStr = typeof value === 'object' ? JSON.stringify(value) : value;
        return `<span class="badge badge-secondary" style="margin: 0.25rem;">${key}: ${valueStr}</span>`;
    }).join('');
    
    return `
        <div style="margin-top: 0.75rem;">
            <strong style="color: var(--text-primary);">Entities:</strong>
            <div style="margin-top: 0.5rem;">${entitiesHtml}</div>
        </div>
    `;
}

function getBadgeClass(ruleName) {
    const name = ruleName.toLowerCase();
    if (name.includes('purchase')) return 'badge-primary';
    if (name.includes('inventory')) return 'badge-warning';
    if (name.includes('loyalty')) return 'badge-success';
    if (name.includes('service')) return 'badge-info';
    if (name.includes('pricing')) return 'badge-danger';
    return 'badge-secondary';
}

// ============================================
// PAGINATION FUNCTIONS
// ============================================

function updatePagination() {
    const pagination = document.getElementById('pagination');
    
    if (!pagination) {
        return;
    }
    
    const totalPages = Math.ceil(filteredRules.length / itemsPerPage);
    
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
    const totalPages = Math.ceil(filteredRules.length / itemsPerPage);
    if (page < 1 || page > totalPages) return;
    
    currentPage = page;
    displayRules();
    
    // Scroll to top
    const container = document.getElementById('rulesContainer');
    if (container) {
        container.scrollTop = 0;
    }
}

// ============================================
// FILTERING FUNCTIONS
// ============================================

function filterRules() {
    const searchInput = document.getElementById('searchInput');
    const ruleFilter = document.getElementById('ruleFilter');
    
    const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
    const selectedRule = ruleFilter ? ruleFilter.value : '';
    
    filteredRules = rulesData.filter(rule => {
        const matchesSearch = searchTerm === '' || JSON.stringify(rule).toLowerCase().includes(searchTerm);
        const matchesFilter = selectedRule === '' || rule.rule_name === selectedRule;
        return matchesSearch && matchesFilter;
    });
    
    currentPage = 1;
    displayRules();
}

function populateRuleFilter() {
    const select = document.getElementById('ruleFilter');
    
    if (!select) {
        return;
    }
    
    const uniqueRules = [...new Set(rulesData.map(r => r.rule_name || 'Unknown'))].sort();
    
    select.innerHTML = '<option value="">All Rules</option>';
    uniqueRules.forEach(ruleName => {
        const option = document.createElement('option');
        option.value = ruleName;
        option.textContent = ruleName.replace(/_/g, ' ');
        select.appendChild(option);
    });
}

// ============================================
// STATS UPDATE FUNCTIONS
// ============================================

function updateStats() {
    // Total rules
    updateStatElement('total-rules', rulesData.length);
    
    // Unique rules
    const uniqueRules = new Set(rulesData.map(r => r.rule_name || 'Unknown'));
    updateStatElement('unique-rules', uniqueRules.size);
    
    // Most fired rule
    if (rulesData.length > 0) {
        const ruleCounts = {};
        rulesData.forEach(rule => {
            const ruleName = rule.rule_name || 'Unknown';
            ruleCounts[ruleName] = (ruleCounts[ruleName] || 0) + 1;
        });
        
        const topRule = Object.entries(ruleCounts).sort((a, b) => b[1] - a[1])[0];
        const topRuleName = topRule[0].replace(/_/g, ' ').substring(0, 20);
        updateStatElement('top-rule', topRuleName);
    } else {
        updateStatElement('top-rule', 'N/A');
    }
    
    // Average per step
    const steps = new Set(rulesData.map(r => r.step));
    const avgPerStep = steps.size > 0 ? (rulesData.length / steps.size).toFixed(1) : '0';
    updateStatElement('avg-per-step', avgPerStep);
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
    console.log('Rules page loaded - setting up event listeners...');
    
    // Setup filter listeners
    const ruleFilter = document.getElementById('ruleFilter');
    if (ruleFilter) {
        ruleFilter.addEventListener('change', () => filterRules());
    }
    
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', () => filterRules());
    }
    
    // Load existing data
    loadExistingData();
});

// ============================================
// DATA PERSISTENCE - LOAD FROM SERVER
// ============================================

async function loadExistingData() {
    try {
        console.log('Loading existing rules data from server...');
        const response = await fetch('/api/get_current_data');
        const data = await response.json();
        
        if (data.has_data && data.rules && data.rules.length > 0) {
            console.log('✓ Found existing rules data');
            
            // Restore rules data
            rulesData = data.rules || [];
            filteredRules = [...rulesData];
            
            // Update display
            displayRules();
            updateStats();
            populateRuleFilter();
            
            console.log('✓ Rules page fully restored from server');
        } else {
            console.log('No previous rules data found');
            displayRules(); // Show empty state
        }
    } catch (error) {
        console.error('Error loading existing data:', error);
        displayRules(); // Show empty state
    }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function refreshRules() {
    console.log('Refreshing rules data...');
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
