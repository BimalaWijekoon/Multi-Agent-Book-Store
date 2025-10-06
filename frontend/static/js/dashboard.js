// ============================================
// BOOKSTORE SIMULATION DASHBOARD - CLEAN VERSION
// Real-time WebSocket + Server-Side Persistence
// ============================================

const socket = io();

// Global state
let simulationRunning = false;
let currentStep = 0;
let totalSteps = 0;
let metricsHistory = [];
let transactionsList = [];
let rulesList = [];
let liveChart = null;
let finalMetrics = null;

// ============================================
// WEBSOCKET HANDLERS
// ============================================

socket.on('connect', () => {
    console.log('✓ WebSocket Connected');
    addConsoleLog('✓ Connected to server', 'success');
});

socket.on('disconnect', () => {
    console.log('✗ WebSocket Disconnected');
});

socket.on('console_log', (data) => {
    addConsoleLog(data.message, data.level.toLowerCase());
});

socket.on('simulation_started', () => {
    console.log('🔄 New simulation started - clearing old data');
    // Clear everything for new simulation
    metricsHistory = [];
    transactionsList = [];
    rulesList = [];
    finalMetrics = null;
    currentStep = 0;
    
    // Clear UI
    document.getElementById('transactionsBody').innerHTML = '<tr><td colspan="4" class="text-center">Waiting for transactions...</td></tr>';
    document.getElementById('rulesBody').innerHTML = '<tr><td colspan="3" class="text-center">Waiting for rules...</td></tr>';
    resetStatCards();
    
    if (liveChart) {
        liveChart.data.labels = [];
        liveChart.data.datasets.forEach(ds => ds.data = []);
        liveChart.update();
    }
});

socket.on('metrics_update', (metrics) => {
    console.log('📊 Metrics update:', metrics.step);
    metricsHistory.push(metrics);
    updateMetrics(metrics);
    updateLiveChart(metrics);
    currentStep = metrics.step;
    updateProgress();
    finalMetrics = metrics;
});

socket.on('transaction_logged', (transaction) => {
    console.log('💰 Transaction logged');
    transactionsList.push(transaction);
    addTransactionRow(transaction);
});

socket.on('rule_executed', (rule) => {
    console.log('⚙️ Rule executed:', rule.rule_name);
    rulesList.push(rule);
    addRuleRow(rule);
});

socket.on('simulation_complete', (summary) => {
    console.log('✅ Simulation complete');
    simulationRunning = false;
    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').disabled = true;
    addConsoleLog('🎉 Simulation completed!', 'success');
    if (summary.final_metrics) {
        addConsoleLog(`📊 Final Revenue: Rs. ${summary.final_metrics.total_revenue}`, 'info');
        addConsoleLog(`📖 Books Sold: ${summary.final_metrics.books_sold}`, 'info');
    }
});

socket.on('simulation_error', (error) => {
    console.error('❌ Simulation error:', error);
    simulationRunning = false;
    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').disabled = true;
    addConsoleLog(`❌ Error: ${error.error}`, 'error');
});

// ============================================
// FORM SUBMISSION
// ============================================

document.getElementById('simulationForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (simulationRunning) {
        addConsoleLog('⚠️ Simulation already running!', 'warning');
        return;
    }
    
    const formData = {
        num_customers: parseInt(document.getElementById('num_customers').value),
        num_employees: parseInt(document.getElementById('num_employees').value),
        num_books: parseInt(document.getElementById('num_books').value),
        num_steps: parseInt(document.getElementById('num_steps').value)
    };
    
    totalSteps = formData.num_steps;
    
    // Show progress bar
    document.getElementById('progressContainer').style.display = 'block';
    updateProgress();
    
    // Disable/enable buttons
    document.getElementById('startBtn').disabled = true;
    document.getElementById('stopBtn').disabled = false;
    simulationRunning = true;
    
    addConsoleLog('🚀 Starting simulation...', 'info');
    
    try {
        const response = await fetch('/api/start_simulation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.error) {
            addConsoleLog(`❌ Error: ${result.error}`, 'error');
            simulationRunning = false;
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
        }
    } catch (error) {
        addConsoleLog(`❌ Failed: ${error.message}`, 'error');
        simulationRunning = false;
        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
    }
});

// ============================================
// UI UPDATE FUNCTIONS
// ============================================

function updateMetrics(metrics) {
    document.getElementById('stat-customers').textContent = metrics.active_customers || 0;
    document.getElementById('stat-employees').textContent = metrics.active_employees || 0;
    document.getElementById('stat-revenue').textContent = `Rs. ${(metrics.total_revenue || 0).toFixed(2)}`;
    document.getElementById('stat-books-sold').textContent = metrics.books_sold || 0;
}

function resetStatCards() {
    document.getElementById('stat-customers').textContent = '0';
    document.getElementById('stat-employees').textContent = '0';
    document.getElementById('stat-revenue').textContent = '$0.00';
    document.getElementById('stat-books-sold').textContent = '0';
}

function updateProgress() {
    if (totalSteps === 0) return;
    const percent = Math.round((currentStep / totalSteps) * 100);
    document.getElementById('progressBar').style.width = `${percent}%`;
    document.getElementById('progressBar').textContent = `${percent}%`;
    document.getElementById('progressText').textContent = `Step ${currentStep} / ${totalSteps}`;
}

function updateLiveChart(metrics) {
    if (!liveChart) return;
    
    liveChart.data.labels.push(`Step ${metrics.step}`);
    liveChart.data.datasets[0].data.push(metrics.total_revenue || 0);
    liveChart.data.datasets[1].data.push(metrics.books_sold || 0);
    liveChart.data.datasets[2].data.push(metrics.avg_customer_satisfaction || 0);
    
    // Keep only last 30 points for performance
    if (liveChart.data.labels.length > 30) {
        liveChart.data.labels.shift();
        liveChart.data.datasets.forEach(ds => ds.data.shift());
    }
    
    liveChart.update('none');
}

function addTransactionRow(transaction) {
    const tbody = document.getElementById('transactionsBody');
    
    // Remove placeholder if exists
    if (tbody.children.length === 1 && tbody.children[0].cells.length === 1) {
        tbody.innerHTML = '';
    }
    
    const row = tbody.insertRow(0); // Insert at top
    row.innerHTML = `
        <td>Step ${transaction.step}</td>
        <td>${transaction.customer || 'Unknown'}</td>
        <td>${transaction.book || 'Unknown'}</td>
        <td>Rs. ${(transaction.price || 0).toFixed(2)}</td>
    `;
    
    // Keep only last 10
    while (tbody.children.length > 10) {
        tbody.deleteRow(tbody.children.length - 1);
    }
}

function addRuleRow(rule) {
    const tbody = document.getElementById('rulesBody');
    
    // Remove placeholder if exists
    if (tbody.children.length === 1 && tbody.children[0].cells.length === 1) {
        tbody.innerHTML = '';
    }
    
    const row = tbody.insertRow(0); // Insert at top
    row.innerHTML = `
        <td>Step ${rule.step}</td>
        <td>${rule.rule_name.replace(/_/g, ' ')}</td>
        <td><span class="badge badge-success">Triggered</span></td>
    `;
    
    // Keep only last 10
    while (tbody.children.length > 10) {
        tbody.deleteRow(tbody.children.length - 1);
    }
}

function addConsoleLog(message, level = 'info') {
    const terminalContent = document.getElementById('terminalContent');
    const line = document.createElement('div');
    line.className = `terminal-line ${level}`;
    
    const timestamp = new Date().toLocaleTimeString();
    line.textContent = `[${timestamp}] ${message}`;
    
    terminalContent.appendChild(line);
    terminalContent.scrollTop = terminalContent.scrollHeight;
    
    // Keep only last 100 lines
    while (terminalContent.children.length > 100) {
        terminalContent.removeChild(terminalContent.firstChild);
    }
}

// ============================================
// CHART INITIALIZATION
// ============================================

function initializeLiveChart() {
    const ctx = document.getElementById('liveMetricsChart').getContext('2d');
    
    liveChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Revenue ($)',
                    data: [],
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Books Sold',
                    data: [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true,
                    yAxisID: 'y1'
                },
                {
                    label: 'Customer Satisfaction',
                    data: [],
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    tension: 0.4,
                    fill: true,
                    yAxisID: 'y2'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#e0e0e0',
                        usePointStyle: true
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: { display: true, text: 'Revenue ($)', color: '#6366f1' },
                    ticks: { color: '#e0e0e0' },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: { display: true, text: 'Books Sold', color: '#10b981' },
                    ticks: { color: '#e0e0e0' },
                    grid: { drawOnChartArea: false }
                },
                y2: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: { display: true, text: 'Satisfaction', color: '#f59e0b' },
                    min: 0,
                    max: 1,
                    ticks: { color: '#e0e0e0' },
                    grid: { drawOnChartArea: false }
                },
                x: {
                    ticks: { color: '#e0e0e0' },
                    grid: { color: 'rgba(255,255,255,0.1)' }
                }
            }
        }
    });
}

// ============================================
// DATA PERSISTENCE - LOAD FROM SERVER
// ============================================

async function loadExistingData() {
    try {
        const response = await fetch('/api/get_current_data');
        const data = await response.json();
        
        if (!data.has_data || !data.metrics || data.metrics.length === 0) {
            console.log('No existing data to load');
            return;
        }
        
        console.log('✓ Loading data from server:', data.metrics.length, 'steps');
        
        // Restore global arrays
        metricsHistory = data.metrics;
        transactionsList = data.transactions || [];
        rulesList = data.rules || [];
        finalMetrics = data.metrics[data.metrics.length - 1];
        
        // Update stat cards with final metrics
        if (finalMetrics) {
            updateMetrics(finalMetrics);
        }
        
        // Restore chart
        if (liveChart && metricsHistory.length > 0) {
            liveChart.data.labels = metricsHistory.map(m => `Step ${m.step}`);
            liveChart.data.datasets[0].data = metricsHistory.map(m => m.total_revenue || 0);
            liveChart.data.datasets[1].data = metricsHistory.map(m => m.books_sold || 0);
            liveChart.data.datasets[2].data = metricsHistory.map(m => m.avg_customer_satisfaction || 0);
            liveChart.update('none');
        }
        
        // Restore transaction table
        const tbody = document.getElementById('transactionsBody');
        tbody.innerHTML = '';
        transactionsList.slice(-10).reverse().forEach(t => addTransactionRow(t));
        
        // Restore rules table
        const rulesBody = document.getElementById('rulesBody');
        rulesBody.innerHTML = '';
        rulesList.slice(-10).reverse().forEach(r => addRuleRow(r));
        
        // Restore progress bar
        if (data.metadata && data.metadata.steps) {
            totalSteps = data.metadata.steps;
            currentStep = metricsHistory.length;
            updateProgress();
            document.getElementById('progressContainer').style.display = 'block';
        }
        
        addConsoleLog('✓ Previous simulation data loaded', 'success');
        console.log('✅ Data restoration complete');
        
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// ============================================
// THEME TOGGLE
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

// Load saved theme
const savedTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);
const themeButton = document.querySelector('.theme-toggle');
if (themeButton) {
    themeButton.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Dashboard initializing...');
    initializeLiveChart();
    loadExistingData();
    addConsoleLog('✓ Dashboard initialized', 'success');
});
