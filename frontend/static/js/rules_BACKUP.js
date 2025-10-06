// ============================================
// RULES PAGE - Detailed Execution Logs
// ============================================

// Initialize WebSocket
const socket = io();

let rulesData = [];
let filteredRules = [];
let currentPage = 1;
const itemsPerPage = 20;

// ============================================
// WEBSOCKET EVENTS
// ============================================

socket.on('connect', () => {
    console.log('✓ Connected to server');
});

socket.on('rule_executed', (rule) => {
    rulesData.push(rule);
    filterRules(); // Refresh display with new rule
});

socket.on('simulation_started', () => {
    console.log('✓ Simulation started - clearing old rules');
    rulesData = [];
    filteredRules = [];
    currentPage = 1;
    updateStats();
    displayRules();
});

socket.on('simulation_complete', () => {
    console.log('✓ Simulation complete - rules persisted');
    // Data stays in rulesData
});

// ============================================
// DATA LOADING (LEGACY)
// ============================================

async function loadRulesData() {
    // This function is now mainly for backward compatibility
    // Data is primarily loaded via loadExistingData() on page load
    try {
        const response = await fetch('/api/get_current_data');
        const data = await response.json();
        
        if (data.rules) {
            rulesData = data.rules;
            filteredRules = [...rulesData];
            
            updateStats();
            populateRuleFilter();
            displayRules();
        }
    } catch (error) {
        console.error('Error loading rules data:', error);
        document.getElementById('rulesContainer').innerHTML = '<p class="text-center">No rules data available</p>';
    }
}

// ============================================
// STATS UPDATE
// ============================================

function updateStats() {
    document.getElementById('total-rules').textContent = rulesData.length;
    
    const uniqueRules = new Set(rulesData.map(r => r.rule_name));
    document.getElementById('unique-rules').textContent = uniqueRules.size;
    
    // Find most fired rule
    const ruleCounts = {};
    rulesData.forEach(rule => {
        ruleCounts[rule.rule_name] = (ruleCounts[rule.rule_name] || 0) + 1;
    });
    
    if (Object.keys(ruleCounts).length > 0) {
        const topRule = Object.entries(ruleCounts).sort((a, b) => b[1] - a[1])[0];
        document.getElementById('top-rule').textContent = topRule[0].replace(/_/g, ' ').substring(0, 20);
    }
    
    // Avg per step
    const steps = new Set(rulesData.map(r => r.step));
    const avgPerStep = steps.size > 0 ? (rulesData.length / steps.size).toFixed(1) : 0;
    document.getElementById('avg-per-step').textContent = avgPerStep;
}

// ============================================
// RULE FILTER
// ============================================

function populateRuleFilter() {
    const uniqueRules = [...new Set(rulesData.map(r => r.rule_name))].sort();
    const select = document.getElementById('ruleFilter');
    
    select.innerHTML = '<option value="">All Rules</option>';
    uniqueRules.forEach(ruleName => {
        const option = document.createElement('option');
        option.value = ruleName;
        option.textContent = ruleName.replace(/_/g, ' ');
        select.appendChild(option);
    });
}

document.getElementById('ruleFilter').addEventListener('change', (e) => {
    filterRules();
});

document.getElementById('searchInput').addEventListener('input', (e) => {
    filterRules();
});

function filterRules() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const selectedRule = document.getElementById('ruleFilter').value;
    
    filteredRules = rulesData.filter(rule => {
        const matchesSearch = searchTerm === '' || 
            JSON.stringify(rule).toLowerCase().includes(searchTerm);
        const matchesFilter = selectedRule === '' || rule.rule_name === selectedRule;
        
        return matchesSearch && matchesFilter;
    });
    
    currentPage = 1;
    displayRules();
}

// ============================================
// RULES DISPLAY
// ============================================

function displayRules() {
    const container = document.getElementById('rulesContainer');
    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageRules = filteredRules.slice(start, end);
    
    if (pageRules.length === 0) {
        container.innerHTML = '<p class="text-center">No rules found matching your criteria</p>';
        return;
    }
    
    container.innerHTML = pageRules.map(rule => createRuleCard(rule)).join('');
    updatePagination();
}

function createRuleCard(rule) {
    const timestamp = new Date(rule.timestamp).toLocaleString();
    const badgeClass = getBadgeClass(rule.rule_name);
    
    return `
        <div class="card mb-2" style="padding: 1rem;">
            <div class="flex justify-between items-center mb-2">
                <div>
                    <span class="badge ${badgeClass}">${rule.rule_name.replace(/_/g, ' ')}</span>
                    <span class="badge badge-info">Step ${rule.step}</span>
                </div>
                <span class="text-secondary" style="font-size: 0.85rem;">${timestamp}</span>
            </div>
            <p style="margin: 0.5rem 0; color: var(--text-secondary);">${rule.rule_description}</p>
            <div style="background: var(--bg-tertiary); padding: 0.75rem; border-radius: var(--radius-md); margin: 0.5rem 0;">
                <strong style="color: var(--primary);">Condition:</strong> ${rule.condition_met || 'N/A'}
            </div>
            <div style="background: var(--bg-tertiary); padding: 0.75rem; border-radius: var(--radius-md);">
                <strong style="color: var(--success);">Action:</strong> ${rule.action || 'N/A'}
            </div>
            ${createEntitiesDisplay(rule.entities)}
        </div>
    `;
}

function createEntitiesDisplay(entities) {
    if (!entities || Object.keys(entities).length === 0) return '';
    
    const entitiesHtml = Object.entries(entities).map(([key, value]) => {
        return `<span class="badge badge-secondary" style="margin: 0.25rem;">${key}: ${JSON.stringify(value)}</span>`;
    }).join('');
    
    return `
        <div style="margin-top: 0.75rem;">
            <strong style="color: var(--text-primary);">Entities:</strong>
            <div style="margin-top: 0.5rem;">${entitiesHtml}</div>
        </div>
    `;
}

function getBadgeClass(ruleName) {
    if (ruleName.includes('purchase')) return 'badge-primary';
    if (ruleName.includes('inventory')) return 'badge-warning';
    if (ruleName.includes('loyalty')) return 'badge-success';
    if (ruleName.includes('service')) return 'badge-info';
    if (ruleName.includes('pricing')) return 'badge-danger';
    return 'badge-secondary';
}

// ============================================
// PAGINATION
// ============================================

function updatePagination() {
    const totalPages = Math.ceil(filteredRules.length / itemsPerPage);
    const pagination = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    
    // Previous button
    html += `<button class="pagination-btn" onclick="changePage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>‹ Prev</button>`;
    
    // Page numbers
    for (let i = 1; i <= Math.min(totalPages, 10); i++) {
        html += `<button class="pagination-btn ${i === currentPage ? 'active' : ''}" onclick="changePage(${i})">${i}</button>`;
    }
    
    // Next button
    html += `<button class="pagination-btn" onclick="changePage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>Next ›</button>`;
    
    pagination.innerHTML = html;
}

function changePage(page) {
    const totalPages = Math.ceil(filteredRules.length / itemsPerPage);
    if (page < 1 || page > totalPages) return;
    
    currentPage = page;
    displayRules();
    document.getElementById('rulesContainer').scrollTop = 0;
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function refreshRules() {
    loadRulesData();
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    const themeButton = document.querySelector('.theme-toggle');
    themeButton.textContent = newTheme === 'dark' ? '☀️' : '🌙';
}

// Load saved theme
const savedTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);
const themeButton = document.querySelector('.theme-toggle');
if (themeButton) {
    themeButton.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
}

// ============================================
// LOAD DATA FROM SERVER (DATA PERSISTENCE!)
// ============================================

async function loadExistingData() {
    try {
        const response = await fetch('/api/get_current_data');
        const data = await response.json();
        
        if (data.has_data && data.rules && data.rules.length > 0) {
            console.log('✓ Loading existing rules data from server');
            console.log('Rules count:', data.rules.length);
            
            // Restore rules data
            rulesData = data.rules;
            filteredRules = [...rulesData];
            
            // Wait a moment for DOM to be fully ready
            setTimeout(() => {
                try {
                    // Update display
                    updateStats();
                    populateRuleFilter();
                    displayRules();
                    console.log('✓ Rules restored from server data');
                } catch (error) {
                    console.error('Error displaying rules:', error);
                }
            }, 100);
            
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
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    loadExistingData(); // Load data from server if available
    
    // Refresh every 10 seconds if simulation running (kept for compatibility)
    setInterval(() => {
        fetch('/api/simulation_status')
            .then(r => r.json())
            .then(status => {
                if (status.running) {
                    // During simulation, we get real-time updates via WebSocket
                    // No need to poll
                }
            });
    }, 10000);
});
